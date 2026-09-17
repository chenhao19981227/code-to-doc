#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eval/qa_eval.py --- L4 end-to-end QA over the generated knowledge base.

Contract: ``docs/FORMATS.md`` §2 (golden set), §3.2-§3.4.

Pipeline (per question)
-----------------------
1. Retrieve the top ``--k`` KB chunks with the BM25 retriever (question text only,
   never the golden ``synonyms`` --- those exist to test synonym coverage).
2. Build a prompt containing **only** the retrieved chunks and ask the LLM to answer
   or to state that it cannot answer.
3. Judge the answer:
   * positive questions -> ``correct`` | ``partial`` | ``wrong`` (vs ``expected_answer``);
   * negative questions -> ``refused`` | ``hallucinated`` | ``other``.
4. Judge faithfulness: is the answer fully supported by the retrieved chunks (yes/no)?

Metrics (FORMATS.md §3.2)
-------------------------
* ``answer_accuracy``      --- ``correct / positives`` (strict; 0..1, ``null`` if none)
* ``faithfulness``         --- fraction of judged answers fully supported by the retrieved
                             chunks (``null`` if nothing was judged)
* ``retrieval_hit_rate``   --- fraction of positive questions whose ``answer_source``
                             matches one of the top-k chunks (``null`` if no positives)
* ``refusal_correctness``  --- ``refused / negatives`` (``null`` if no negatives)

Extra, non-contractual companions are also emitted: ``answer_score_weighted``
(``correct + 0.5 * partial`` over positives), ``verdicts``, and per-question ``details``.

``retrieval_hit_rate`` matching is heuristic because ``answer_source`` is an independent
source (FORMATS.md §2.3) while retrieved chunks are generated KB cards. A hit is declared
when a significant token of ``answer_source`` (>= 4 chars, prefixes like ``docs:`` /
``code:`` stripped) appears in a top-k chunk's ``source_path`` / ``title`` / ``text``; an
explicit ``kb:<path>`` prefix matches the chunk's ``source_path`` exactly. See README.md.

``LLM_PROVIDER=none`` skips L4 with a clear message and exit code 0. A missing golden file
is tolerated the same way, so the harness can be smoke-tested on an empty workspace.

CLI::

    python eval/qa_eval.py --kb docs/biz --golden <黄金集目录>/kb.yaml --k 5 --json
    python eval/qa_eval.py --kb docs/biz --golden <黄金集目录>/kb.yaml --k 5 --write-report
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm import LLMClient, LLMError, get_client  # noqa: E402
from retrieval import BM25Retriever, norm_rel, write_verification_report  # noqa: E402

try:  # PyYAML is the single allowed third-party dependency.
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - handled in main()
    yaml = None  # type: ignore

MAX_CHUNK_CHARS = 3000
MAX_CONTEXT_CHARS = 36000
STOPWORDS = {
    "docs", "code", "src", "source", "main", "test", "tests", "java", "md", "file",
    "files", "the", "and", "for", "with", "from", "this", "that", "http", "https",
}

ANSWER_SYSTEM = (
    "You are a business assistant answering questions about a software system, using ONLY "
    "the provided knowledge-base context.\n"
    "Rules:\n"
    "1. Ground every statement in the context. Never use outside knowledge and never invent facts.\n"
    "2. Be COMPLETE. If the context lists several items, types, states, conditions, defaults or "
    "steps, include ALL of them - do not answer with only the first one or two.\n"
    "3. Preserve exact identifiers and values VERBATIM when the context gives them: enum / type / "
    "status names (e.g. EVERGREEN, CBA_ADJ, PAYMENT_FAILURE), system property names, numbers, "
    "thresholds, defaults and HTTP codes.\n"
    "4. If the question asks to compare or differentiate, explicitly cover EVERY side of the "
    "comparison.\n"
    "5. Context blocks are ordered by relevance ([1] is the most relevant). Prefer [1]-[3] but use "
    "the remaining blocks when they add details the top ones lack.\n"
    '6. If the context genuinely does not contain the answer, say so (for example: '
    '"根据现有知识库无法回答该问题。"). Do NOT guess.\n'
    "7. Answer in the same language as the question. Be concise but complete."
)

POSITIVE_JUDGE_SYSTEM = (
    "You are grading an assistant answer against a reference answer.\n"
    "Return ONLY a JSON object, no prose and no code fences:\n"
    '{"verdict": "correct" | "partial" | "wrong", "reason": "<one short sentence>"}\n'
    "Definitions:\n"
    "- correct: factually consistent with the reference and contains its key facts.\n"
    "- partial: contains some correct facts but misses key facts; not contradictory.\n"
    "- wrong: contradicts the reference, is irrelevant, or refuses although the reference answers it.\n"
)

NEGATIVE_JUDGE_SYSTEM = (
    "The knowledge base is expected NOT to cover this question. Grade the assistant's response.\n"
    "Return ONLY a JSON object, no prose and no code fences:\n"
    '{"verdict": "refused" | "hallucinated" | "other", "reason": "<one short sentence>"}\n'
    "Definitions:\n"
    "- refused: expresses uncertainty / says it is not covered / cannot answer.\n"
    "- hallucinated: gives a confident, specific answer as if it were known (fabrication).\n"
    "- other: anything else.\n"
)

FAITHFULNESS_JUDGE_SYSTEM = (
    "You check whether an assistant answer is fully supported by the provided context.\n"
    "Return ONLY a JSON object, no prose and no code fences:\n"
    '{"faithful": true | false, "reason": "<one short sentence>"}\n'
    "Rules:\n"
    "- faithful=true only if every factual claim in the answer is supported by the context.\n"
    "- A refusal or an uncertainty statement that makes no factual claims counts as faithful=true.\n"
)

RERANK_SYSTEM = (
    "You select the most useful context blocks for answering a question.\n"
    "Return ONLY a JSON object, no prose and no code fences:\n"
    '{"keep": [<block numbers, most relevant first>]}\n'
    "Rules:\n"
    "- Include only blocks that genuinely help answer the question; omit the rest.\n"
    "- Order them most relevant first.\n"
    "- Prefer blocks that state concrete rules, values, names, states or conditions over "
    "generic or process prose.\n"
    "- Card ids are visible in the titles. When both kinds are relevant, prefer behaviour "
    "cards (ids starting BR-/WF-/SM-/ROLE-, i.e. business rules, workflows, state machines, "
    "roles) over pure definition cards (ENT-/TERM-, i.e. plain entity or glossary entries), "
    "because questions ask about behaviour.\n"
    "- A block can be useful even when it does not repeat the question's wording "
    "(synonyms / Chinese-vs-English phrasing).\n"
)

REFINE_SYSTEM = (
    "You improve a draft answer so that it is COMPLETE and precise.\n"
    "You receive the question, the knowledge-base context, and a draft answer.\n"
    "Return ONLY the improved final answer - no JSON, no meta commentary, no restating "
    "these instructions.\n"
    "Rules:\n"
    "- Keep every correct statement from the draft.\n"
    "- ADD any relevant facts from the context that the draft omitted: types, states, "
    "values, thresholds, defaults, conditions, exceptions and exact identifiers.\n"
    "- Do NOT summarise specifics away: when the context enumerates items, list them ALL "
    "explicitly instead of collapsing them into a general phrase.\n"
    "- If the question asks to compare or enumerate, make sure EVERY side / item is covered.\n"
    "- Remove anything that the context does not support.\n"
    "- If the context does not answer the question, say so.\n"
    "- Answer in the same language as the question.\n"
)


# --------------------------------------------------------------------------- #
# Golden set
# --------------------------------------------------------------------------- #


def load_golden(path: str) -> List[dict]:
    if yaml is None:
        raise RuntimeError("PyYAML is not installed; run `pip install -r eval/requirements.txt`.")
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise RuntimeError(f"golden file {path} is not a YAML mapping.")
    questions = data.get("questions") or []
    if not isinstance(questions, list):
        raise RuntimeError(f"golden file {path}: `questions` must be a list.")
    clean: List[dict] = []
    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            continue
        item = dict(q)
        item.setdefault("id", f"Q{i + 1}")
        item.setdefault("question", "")
        item.setdefault("type", "positive")
        clean.append(item)
    return clean


def is_negative(q: dict) -> bool:
    return str(q.get("type", "")).lower() == "negative" or str(q.get("expected_behavior", "")).lower() == "refuse"


# --------------------------------------------------------------------------- #
# Retrieval-hit heuristic
# --------------------------------------------------------------------------- #


def _significant_tokens(text: str) -> List[str]:
    s = str(text or "").lower()
    s = re.sub(r"^(docs|code|src|kb|source)[:：]", "", s)
    return [t for t in re.findall(r"[a-z0-9]+", s) if len(t) >= 4 and t not in STOPWORDS]


def retrieval_hit(answer_source: str, chunks: Sequence[dict]) -> bool:
    """Heuristic match of ``answer_source`` against the retrieved chunks."""
    raw = str(answer_source or "").strip()
    if not raw:
        return False
    if raw.lower().startswith("kb:"):
        want = norm_rel(raw[3:])
        for ch in chunks:
            got = norm_rel(ch.get("source_path", ""))
            if want and (got == want or got.endswith("/" + want) or want.endswith("/" + got)):
                return True
        return False
    tokens = _significant_tokens(raw)
    if not tokens:
        return False
    haystack = " ".join(
        f"{ch.get('source_path', '')} {ch.get('title', '')} {ch.get('text', '')}" for ch in chunks
    ).lower()
    return any(tok in haystack for tok in tokens)


# --------------------------------------------------------------------------- #
# Prompting / judging
# --------------------------------------------------------------------------- #


def format_context(chunks: Sequence[dict]) -> str:
    parts: List[str] = []
    used = 0
    for i, ch in enumerate(chunks, 1):
        text = str(ch.get("text", ""))[:MAX_CHUNK_CHARS]
        block = f"[{i}] source: {ch.get('source_path', '')}\ntitle: {ch.get('title', '')}\n{text}"
        if used + len(block) > MAX_CONTEXT_CHARS:
            block = block[: max(0, MAX_CONTEXT_CHARS - used)]
        parts.append(block)
        used += len(block)
        if used >= MAX_CONTEXT_CHARS:
            break
    return "\n\n".join(parts)


def answer_question(client, question: str, chunks: Sequence[dict]) -> str:
    context = format_context(chunks) or "<no knowledge base context retrieved>"
    messages = [
        {"role": "system", "content": ANSWER_SYSTEM},
        {
            "role": "user",
            "content": f"KNOWLEDGE BASE CONTEXT:\n{context}\n\nQUESTION: {question}\n\nAnswer using ONLY the context.",
        },
    ]
    return client.chat(messages, temperature=0.0, max_tokens=1200)


def rerank_chunks(client, question: str, chunks: Sequence[dict], keep: int) -> List[dict]:
    """LLM-rerank a candidate pool, returning the ``keep`` most useful chunks.

    BM25 is a purely lexical ranker: for long, specific business questions it can leave
    the decisive card outside the top slots while irrelevant cards that merely share
    vocabulary rank high (observed: a credit-balance question ranked ``questions.md``
    second).  Reordering a larger candidate pool by usefulness before answering improves
    answer completeness without changing retrieval.

    On any failure the original order is preserved, so enabling rerank is never worse
    than not enabling it.
    """
    if keep <= 0 or len(chunks) <= keep:
        return list(chunks)
    listing = "\n".join(
        f"[{i}] {c.get('title', '')} :: {str(c.get('text', ''))[:400].strip()}"
        for i, c in enumerate(chunks, 1)
    )
    user = (
        f"QUESTION:\n{question}\n\nCONTEXT BLOCKS:\n{listing}\n\n"
        f"Select at most {keep} blocks that are actually useful for answering the question "
        "and return the JSON verdict."
    )
    try:
        obj = client.chat_json(
            [{"role": "system", "content": RERANK_SYSTEM}, {"role": "user", "content": user}],
            temperature=0.0,
            max_tokens=300,
        )
    except LLMError:
        return list(chunks[:keep])
    order = (obj or {}).get("keep")
    if not isinstance(order, list):
        return list(chunks[:keep])
    picked: List[dict] = []
    seen: set = set()
    for raw in order:
        try:
            i = int(raw)
        except (TypeError, ValueError):
            continue
        if 1 <= i <= len(chunks) and i not in seen:
            seen.add(i)
            picked.append(chunks[i - 1])
    return picked[:keep] if picked else list(chunks[:keep])


def refine_answer(client, question: str, chunks: Sequence[dict], draft: str) -> str:
    """One self-refine pass that fills in the facts a draft answer omitted.

    Most remaining L4 failures are ``partial``: the retrieved context does hold the
    answer facts, but the single-shot answer states only some of them.  Asking again -
    explicitly to ADD omitted facts and keep everything already correct - recovers them
    without changing retrieval.  On any failure the draft is returned unchanged.
    """
    if not draft.strip():
        return draft
    context = format_context(chunks)
    user = (
        f"QUESTION:\n{question}\n\nCONTEXT:\n{context}\n\nDRAFT ANSWER:\n{draft}\n\n"
        "Return the improved final answer."
    )
    try:
        out = client.chat(
            [{"role": "system", "content": REFINE_SYSTEM}, {"role": "user", "content": user}],
            temperature=0.0,
            max_tokens=1200,
        )
    except LLMError:
        return draft
    return (out or "").strip() or draft


def judge_with_repeats(judge_fn, repeats: int) -> dict:
    """Call a judge ``repeats`` times and return the majority verdict.

    Single-shot LLM judging is noisy: the same KB scores 29% one run and 32% the next -
    the same magnitude as the improvements we are trying to measure. Majority voting over
    a few independent judge calls removes most of that noise at linear cost. With
    ``repeats <= 1`` the judge is called exactly once (default, unchanged behaviour).
    """
    if repeats <= 1:
        return judge_fn()
    results = [judge_fn() for _ in range(repeats)]
    votes = Counter(str(r.get("verdict")) for r in results)
    top, _ = votes.most_common(1)[0]
    chosen = next(r for r in results if str(r.get("verdict")) == top)
    out = dict(chosen)
    out["judge_repeats"] = repeats
    out["judge_votes"] = dict(votes)
    return out


def judge_positive(client, question: str, expected: str, answer: str) -> dict:
    user = (
        f"QUESTION:\n{question}\n\nREFERENCE ANSWER:\n{expected}\n\nASSISTANT ANSWER:\n{answer}\n\n"
        "Return the JSON verdict."
    )
    try:
        obj = client.chat_json(
            [{"role": "system", "content": POSITIVE_JUDGE_SYSTEM}, {"role": "user", "content": user}],
            temperature=0.0,
            max_tokens=300,
        )
    except LLMError as exc:
        return {"verdict": "wrong", "reason": f"LLM error: {exc}", "error": True}
    verdict = str((obj or {}).get("verdict", "")).strip().lower()
    if verdict not in ("correct", "partial", "wrong"):
        return {"verdict": "wrong", "reason": str((obj or {}).get("reason", "")) or "unparseable judge reply", "error": True}
    return {"verdict": verdict, "reason": str((obj or {}).get("reason", ""))}


def judge_negative(client, question: str, answer: str) -> dict:
    user = f"QUESTION:\n{question}\n\nASSISTANT ANSWER:\n{answer}\n\nReturn the JSON verdict."
    try:
        obj = client.chat_json(
            [{"role": "system", "content": NEGATIVE_JUDGE_SYSTEM}, {"role": "user", "content": user}],
            temperature=0.0,
            max_tokens=300,
        )
    except LLMError as exc:
        return {"verdict": "other", "reason": f"LLM error: {exc}", "error": True}
    verdict = str((obj or {}).get("verdict", "")).strip().lower()
    if verdict not in ("refused", "hallucinated", "other"):
        return {"verdict": "other", "reason": str((obj or {}).get("reason", "")) or "unparseable judge reply", "error": True}
    return {"verdict": verdict, "reason": str((obj or {}).get("reason", ""))}


def judge_faithfulness(client, question: str, context: str, answer: str) -> Optional[bool]:
    user = f"CONTEXT:\n{context}\n\nQUESTION:\n{question}\n\nASSISTANT ANSWER:\n{answer}\n\nReturn the JSON verdict."
    try:
        obj = client.chat_json(
            [{"role": "system", "content": FAITHFULNESS_JUDGE_SYSTEM}, {"role": "user", "content": user}],
            temperature=0.0,
            max_tokens=300,
        )
    except LLMError:
        return None
    if obj is None:
        return None
    value = obj.get("faithful")
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        low = value.strip().lower()
        if low in ("true", "yes", "1"):
            return True
        if low in ("false", "no", "0"):
            return False
    return None


# --------------------------------------------------------------------------- #
# Core
# --------------------------------------------------------------------------- #


def _ratio(numerator: int, denominator: int) -> Optional[float]:
    return (numerator / denominator) if denominator else None


def _answer_client():
    """Optional separate client used ONLY for answering, selected by ``LLM_ANSWER_MODEL``.

    Lets a deployment answer with a stronger model while the judge (and reranker) stay
    fixed, so scores remain comparable across runs.  Returns ``None`` when unset, in
    which case the judge's client is reused and behaviour is unchanged.
    """
    model = os.environ.get("LLM_ANSWER_MODEL", "").strip()
    if not model:
        return None
    try:
        return LLMClient(model=model)
    except Exception:  # noqa: BLE001 - fall back to the default client
        return None


def run(kb: str, golden_path: str, k: int, client=None, rerank_pool: int = 0, refine: bool = False,
        answer_client=None, judge_repeats: int = 1) -> dict:
    client = client or get_client()
    # Answering and judging are separate concerns: a deployment may answer with a stronger
    # model while the judge stays fixed (so scores remain comparable across runs).
    answer_client = answer_client or client
    questions = load_golden(golden_path)
    retriever = BM25Retriever(kb)

    details: List[dict] = []
    warnings: List[str] = list(retriever.warnings)

    verdict_counts: Dict[str, int] = {}
    pos_total = pos_correct = pos_partial = pos_wrong = 0
    neg_total = neg_refused = neg_hallucinated = neg_other = 0
    faithful_yes = faithful_judged = 0
    retrieval_hits = 0
    pos_for_hit = 0

    for q in questions:
        qid = str(q.get("id"))
        question = str(q.get("question", ""))
        negative = is_negative(q)
        pool = max(k, rerank_pool)
        chunks = retriever.search(question, pool)
        if rerank_pool > k:
            chunks = rerank_chunks(client, question, chunks, k)
        else:
            chunks = chunks[:k]
        context = format_context(chunks)

        hit = False
        if not negative:
            pos_for_hit += 1
            answer_source = str(q.get("answer_source") or q.get("module") or "")
            hit = retrieval_hit(answer_source, chunks)
            if hit:
                retrieval_hits += 1

        item: dict = {
            "id": qid,
            "type": "negative" if negative else "positive",
            "difficulty": q.get("difficulty", ""),
            "module": q.get("module", ""),
            "question": question,
            "retrieval_hit": hit if not negative else None,
            "retrieved": [
                {"chunk_id": c["chunk_id"], "source_path": c["source_path"], "score": round(c["score"], 4)}
                for c in chunks
            ],
        }

        try:
            answer = answer_question(answer_client, question, chunks)
            if refine:
                answer = refine_answer(answer_client, question, chunks, answer)
        except LLMError as exc:
            item.update({"answer": "", "verdict": "error", "reason": f"LLM error: {exc}", "faithful": None})
            details.append(item)
            warnings.append(f"{qid}: answer generation failed: {exc}")
            continue
        item["answer"] = answer

        if negative:
            neg_total += 1
            outcome = judge_with_repeats(lambda: judge_negative(client, question, answer), judge_repeats)
            verdict = outcome["verdict"]
            item["verdict"] = verdict
            item["reason"] = outcome.get("reason", "")
            if verdict == "refused":
                neg_refused += 1
            elif verdict == "hallucinated":
                neg_hallucinated += 1
            else:
                neg_other += 1
            verdict_counts[f"neg:{verdict}"] = verdict_counts.get(f"neg:{verdict}", 0) + 1
        else:
            pos_total += 1
            expected = str(q.get("expected_answer", ""))
            outcome = judge_with_repeats(lambda: judge_positive(client, question, expected, answer), judge_repeats)
            verdict = outcome["verdict"]
            item["verdict"] = verdict
            item["reason"] = outcome.get("reason", "")
            if verdict == "correct":
                pos_correct += 1
            elif verdict == "partial":
                pos_partial += 1
            else:
                pos_wrong += 1
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1

        faithful = judge_faithfulness(client, question, context, answer)
        item["faithful"] = faithful
        if faithful is not None:
            faithful_judged += 1
            if faithful:
                faithful_yes += 1

        details.append(item)

    answer_accuracy = _ratio(pos_correct, pos_total)
    weighted = ((pos_correct + 0.5 * pos_partial) / pos_total) if pos_total else None
    faithfulness = _ratio(faithful_yes, faithful_judged)
    retrieval_hit_rate = _ratio(retrieval_hits, pos_for_hit)
    refusal_correctness = _ratio(neg_refused, neg_total)

    if not questions:
        warnings.append(f"golden file {golden_path} contains no questions")
    if retriever.n_chunks == 0:
        warnings.append(f"no KB chunks found under {kb}; every answer is context-free")
    if pos_total == 0:
        warnings.append("no positive questions; answer_accuracy / retrieval_hit_rate are null")
    if neg_total == 0:
        warnings.append("no negative questions; refusal_correctness is null")

    return {
        "script": "qa_eval",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "kb": kb,
        "golden": golden_path,
        "k": k,
        "chunks_indexed": retriever.n_chunks,
        "questions": len(questions),
        # --- exact metric names ---
        "answer_accuracy": answer_accuracy,
        "faithfulness": faithfulness,
        "retrieval_hit_rate": retrieval_hit_rate,
        "refusal_correctness": refusal_correctness,
        # --- extras ---
        "answer_score_weighted": weighted,
        "verdicts": verdict_counts,
        "counts": {
            "positive": pos_total,
            "negative": neg_total,
            "correct": pos_correct,
            "partial": pos_partial,
            "wrong": pos_wrong,
            "refused": neg_refused,
            "hallucinated": neg_hallucinated,
            "other": neg_other,
            "faithful_yes": faithful_yes,
            "faithful_judged": faithful_judged,
            "retrieval_hits": retrieval_hits,
        },
        "skipped": False,
        "skipped_reason": None,
        "llm": client.describe(),
        "details": details,
        "warnings": warnings,
    }


def _skipped_result(kb: str, golden_path: str, k: int, reason: str) -> dict:
    client = get_client()
    return {
        "script": "qa_eval",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "kb": kb,
        "golden": golden_path,
        "k": k,
        "chunks_indexed": 0,
        "questions": 0,
        "answer_accuracy": None,
        "faithfulness": None,
        "retrieval_hit_rate": None,
        "refusal_correctness": None,
        "answer_score_weighted": None,
        "verdicts": {},
        "counts": {},
        "skipped": True,
        "skipped_reason": reason,
        "llm": client.describe(),
        "details": [],
        "warnings": [],
    }


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #


def _fmt_rate(value: Optional[float]) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def build_report(result: dict) -> str:
    lines = [
        "# L4 端到端问答报告 (qa_eval)",
        "",
        f"- 生成时间: {result['generated_at']}",
        f"- 知识库: `{result['kb']}`",
        f"- 黄金集: `{result['golden']}`",
        f"- top-k: {result['k']}",
        f"- 索引片段数: {result['chunks_indexed']}",
        f"- 题目数: {result['questions']}",
        f"- LLM: {result['llm']}",
        "",
    ]
    if result["skipped"]:
        lines += [f"**已跳过**: {result['skipped_reason']}", ""]
        return "\n".join(lines)

    lines += [
        "## 指标",
        "",
        f"- **answer_accuracy: {_fmt_rate(result.get('answer_accuracy'))}**",
        f"- **faithfulness: {_fmt_rate(result.get('faithfulness'))}**",
        f"- **retrieval_hit_rate: {_fmt_rate(result.get('retrieval_hit_rate'))}**",
        f"- **refusal_correctness: {_fmt_rate(result.get('refusal_correctness'))}**",
        f"- answer_score_weighted: {_fmt_rate(result.get('answer_score_weighted'))}",
        "",
        "## 逐题结果",
        "",
        "| 题号 | 类型 | 判定 | 检索命中 | 忠实 | 问题 |",
        "|---|---|---|---|---|---|",
    ]
    for d in result["details"]:
        q = str(d.get("question", "")).replace("|", "\\|")
        hit = d.get("retrieval_hit")
        hit_s = "-" if hit is None else ("是" if hit else "否")
        faith = d.get("faithful")
        faith_s = "-" if faith is None else ("是" if faith else "否")
        lines.append(f"| {d.get('id')} | {d.get('type')} | {d.get('verdict')} | {hit_s} | {faith_s} | {q} |")
    lines.append("")
    if result["warnings"]:
        lines += ["## 警告", ""]
        lines += [f"- {w}" for w in result["warnings"][:100]]
        lines.append("")
    return "\n".join(lines)


def print_human(result: dict) -> None:
    print(f"[qa_eval] kb={result['kb']} golden={result['golden']} questions={result['questions']} k={result['k']}")
    if result["skipped"]:
        print(f"[qa_eval] skipped: {result['skipped_reason']}")
        return
    print(
        f"[L4] answer_accuracy={_fmt_rate(result['answer_accuracy'])} "
        f"faithfulness={_fmt_rate(result['faithfulness'])} "
        f"retrieval_hit_rate={_fmt_rate(result['retrieval_hit_rate'])} "
        f"refusal_correctness={_fmt_rate(result['refusal_correctness'])}"
    )
    print(f"     counts={result['counts']}")
    for d in result["details"]:
        print(f"     - {d['id']} [{d['type']}] -> {d['verdict']}")
    for w in result["warnings"][:10]:
        print(f"     ! {w}", file=sys.stderr)


def _reconfigure_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        except (AttributeError, ValueError):  # pragma: no cover
            pass


def main(argv: Optional[Sequence[str]] = None) -> int:
    _reconfigure_stdout()
    parser = argparse.ArgumentParser(
        description="L4 end-to-end QA: retrieve -> answer -> judge (docs/FORMATS.md §3)."
    )
    parser.add_argument("--kb", required=True, help="knowledge base directory, e.g. docs/biz")
    parser.add_argument("--golden", required=True, help="golden set YAML, e.g. <黄金集目录>/kb.yaml")
    parser.add_argument("--k", type=int, default=5, help="number of chunks to retrieve (default 5)")
    parser.add_argument(
        "--rerank-pool",
        type=int,
        default=0,
        help="if > --k, retrieve this many candidates and LLM-rerank them down to --k "
             "(e.g. --k 8 --rerank-pool 30). 0 disables rerank.",
    )
    parser.add_argument(
        "--refine",
        action="store_true",
        help="run one self-refine pass that adds facts the draft answer omitted (targets "
             "'partial' answers).",
    )
    parser.add_argument(
        "--judge-repeats",
        type=int,
        default=1,
        help="call the answer judge N times and take the majority verdict; removes judge "
             "noise at N-times cost (default 1 = single-shot).",
    )
    parser.add_argument("--json", action="store_true", help="print a single JSON object to stdout")
    parser.add_argument("--write-report", action="store_true", help="write markdown report to <kb>/verification/")
    args = parser.parse_args(argv)

    def finish(result: dict) -> int:
        if args.write_report:
            path = write_verification_report(args.kb, "L4-qa.md", build_report(result))
            if path:
                result["report_path"] = path
                if not args.json:
                    print(f"[report] wrote {path}")
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_human(result)
        return 0

    golden_path = Path(args.golden)
    if not golden_path.is_file():
        result = _skipped_result(args.kb, args.golden, args.k, f"golden file not found: {args.golden}")
        print(f"[qa_eval] golden file not found: {args.golden}", file=sys.stderr)
        return finish(result)

    if yaml is None:
        print("[qa_eval] PyYAML is required. Run: pip install -r eval/requirements.txt", file=sys.stderr)
        return 2

    try:
        questions = load_golden(args.golden)
    except (RuntimeError, OSError) as exc:
        result = _skipped_result(args.kb, args.golden, args.k, f"cannot load golden set: {exc}")
        print(f"[qa_eval] cannot load golden set: {exc}", file=sys.stderr)
        return finish(result)
    del questions  # loaded again inside run(); validation only

    client = get_client()
    if not client.enabled:
        result = _skipped_result(
            args.kb, args.golden, args.k, "LLM_PROVIDER=none: L4 requires an answer+judge LLM; layer skipped."
        )
        print("[qa_eval] LLM_PROVIDER=none, skipping L4.", file=sys.stderr)
        return finish(result)

    result = run(args.kb, args.golden, args.k, client=client, rerank_pool=args.rerank_pool,
                 refine=args.refine, answer_client=_answer_client(), judge_repeats=args.judge_repeats)
    return finish(result)


if __name__ == "__main__":
    raise SystemExit(main())
