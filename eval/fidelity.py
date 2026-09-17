#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eval/fidelity.py --- L1 citation fidelity via an LLM judge (sampled).

Contract: ``docs/FORMATS.md`` §3.2-§3.4.

Definition
----------
Only cards whose ``置信度`` is 🟢 ``confirmed`` or 🟡 ``inferred`` **and** that carry at
least one ``溯源`` citation are eligible.  A reproducible random ``--sample`` fraction of
them is drawn, and for each sampled card the judge is shown:

* the card's claim text (title + prose, metadata bullets stripped), and
* the actual source lines named by the citations (numbered).

The judge independently re-reads the cited code and returns one of:

* ``supported``    --- the cited code directly justifies the claim;
* ``contradicted`` --- the cited code contradicts the claim;
* ``unclear``      --- the cited code neither clearly supports nor contradicts it.

Metrics (FORMATS.md §3.2):

* ``hallucination_rate`` --- ``contradicted / sampled`` (``null`` when nothing sampled)
* ``verdicts``           --- counts of supported / contradicted / unclear

Sampling is deterministic (``random.Random(20260101)``) so repeated runs are comparable.
Network I/O only happens when the script runs with a real provider; with
``LLM_PROVIDER=none`` the layer is skipped with a clear message and exit code 0.

CLI::

    python eval/fidelity.py --kb docs/biz --root <代码根> --sample 0.3 --json
    python eval/fidelity.py --kb docs/biz --root <代码根> --sample 0.3 --write-report
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm import LLMError, get_client  # noqa: E402
from retrieval import (  # noqa: E402
    Card,
    card_claim_text,
    parse_kb,
    read_source_lines,
    resolve_citation_path,
    write_verification_report,
)

SAMPLE_SEED = 20260101
ELIGIBLE_CONFIDENCE = ("confirmed", "inferred")
MAX_SOURCE_CHARS = 14000
MAX_LINES_PER_CITATION = 200

SYSTEM_PROMPT = (
    "You are a strict verification judge for a business knowledge base.\n"
    "You receive a CLAIM taken from a knowledge card and the SOURCE CODE that the card "
    "cites. Decide whether the claim is supported by the cited source.\n"
    "Return ONLY a JSON object, no prose and no code fences:\n"
    '{"verdict": "supported" | "contradicted" | "unclear", "reason": "<one short sentence>"}\n'
    "Rules:\n"
    "- supported: the cited code directly implies or contains the claim (correct condition, "
    "threshold, value or behavior).\n"
    "- contradicted: the cited code contradicts the claim (wrong number, wrong condition, "
    "opposite behavior, claim about something the code does not do).\n"
    "- unclear: the cited code neither clearly supports nor contradicts the claim "
    "(insufficient or irrelevant evidence). Be strict: when in doubt, use unclear.\n"
)


def _source_block(card: Card, root: Optional[str]) -> str:
    """Render the cited source lines as a numbered, numbered-by-file text block."""
    parts: List[str] = []
    for cit in card.citations:
        path = resolve_citation_path(root, cit.path) if root else None
        if path is None:
            parts.append(f"--- {cit.slug} ---\n<SOURCE FILE NOT FOUND>")
            continue
        lines = read_source_lines(path) or []
        start = max(1, cit.start_line)
        end = min(len(lines), cit.end_line)
        if end < start:
            parts.append(f"--- {cit.slug} ---\n<CITED RANGE OUT OF FILE BOUNDS ({len(lines)} lines)>")
            continue
        segment = lines[start - 1 : end][:MAX_LINES_PER_CITATION]
        numbered = "\n".join(f"{start + i:>5}: {ln}" for i, ln in enumerate(segment))
        parts.append(f"--- {cit.slug} ---\n{numbered}")
    return "\n\n".join(parts)


def _eligible(cards: Sequence[Card]) -> List[Card]:
    return [c for c in cards if c.confidence in ELIGIBLE_CONFIDENCE and c.citations]


def _sample(cards: Sequence[Card], fraction: float) -> List[Card]:
    n = len(cards)
    if n == 0:
        return []
    size = int(round(n * fraction))
    if fraction > 0 and size == 0:
        size = 1
    size = max(0, min(size, n))
    if size >= n:
        return list(cards)
    return random.Random(SAMPLE_SEED).sample(list(cards), size)


def _judge_card(client, card: Card, root: Optional[str]) -> dict:
    claim = card_claim_text(card)
    source = _source_block(card, root)
    if len(source) > MAX_SOURCE_CHARS:
        source = source[:MAX_SOURCE_CHARS] + "\n... <truncated>"
    user = f"CLAIM:\n{claim}\n\nCITED SOURCE CODE:\n{source}\n\nReturn the JSON verdict."
    try:
        obj = client.chat_json(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user},
            ],
            temperature=0.0,
            max_tokens=300,
        )
    except LLMError as exc:
        return {"verdict": "unclear", "reason": f"LLM error: {exc}", "error": True}

    verdict = str((obj or {}).get("verdict", "")).strip().lower()
    reason = str((obj or {}).get("reason", "")).strip()
    if verdict not in ("supported", "contradicted", "unclear"):
        return {"verdict": "unclear", "reason": reason or "unparseable judge reply", "error": True}
    return {"verdict": verdict, "reason": reason}


def run(kb: str, root: str, sample_fraction: float, client=None, max_items: Optional[int] = None) -> dict:
    client = client or get_client()
    cards, warnings = parse_kb(kb)
    eligible = _eligible(cards)
    sampled = _sample(eligible, sample_fraction)
    if max_items is not None:
        sampled = sampled[:max_items]

    verdicts = {"supported": 0, "contradicted": 0, "unclear": 0}
    details: List[dict] = []
    skipped_reason: Optional[str] = None

    if not client.enabled:
        skipped_reason = "LLM_PROVIDER=none: L1 fidelity requires a judge LLM; layer skipped."
    elif not eligible:
        skipped_reason = "no eligible cards (need confidence confirmed/inferred AND citations)."
    else:
        for card in sampled:
            outcome = _judge_card(client, card, root)
            verdicts[outcome["verdict"]] = verdicts.get(outcome["verdict"], 0) + 1
            details.append(
                {
                    "chunk_id": card.chunk_id,
                    "card_id": card.card_id,
                    "title": card.title,
                    "source_path": card.source_path,
                    "confidence": card.confidence,
                    "citations": [c.slug for c in card.citations],
                    "verdict": outcome["verdict"],
                    "reason": outcome.get("reason", ""),
                    "error": bool(outcome.get("error")),
                }
            )

    n_sampled = len(details)
    hallucination_rate = (verdicts["contradicted"] / n_sampled) if n_sampled else None

    if not cards:
        warnings.append(f"no knowledge cards found under {kb}")

    return {
        "script": "fidelity",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "kb": kb,
        "root": root,
        "sample": sample_fraction,
        "sample_seed": SAMPLE_SEED,
        "cards": len(cards),
        "eligible_cards": len(eligible),
        "sampled": n_sampled,
        # --- exact metric names ---
        "hallucination_rate": hallucination_rate,
        "verdicts": verdicts,
        # --- extras ---
        "skipped": skipped_reason is not None,
        "skipped_reason": skipped_reason,
        "llm": client.describe(),
        "details": details,
        "warnings": warnings,
    }


def _fmt_rate(value: Optional[float]) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def build_report(result: dict) -> str:
    lines = [
        "# L1 引用忠实度报告 (fidelity)",
        "",
        f"- 生成时间: {result['generated_at']}",
        f"- 知识库: `{result['kb']}`",
        f"- 代码根: `{result['root']}`",
        f"- 抽样比例: {result['sample']} (seed={result['sample_seed']})",
        f"- 候选卡（🟢/🟡 且有引用）: {result['eligible_cards']}",
        f"- 实际抽样: {result['sampled']}",
        f"- LLM: {result['llm']}",
        "",
    ]
    if result["skipped"]:
        lines.append(f"**已跳过**: {result['skipped_reason']}")
        lines.append("")
        return "\n".join(lines)

    lines += [
        "## 指标",
        "",
        f"- **hallucination_rate: {_fmt_rate(result['hallucination_rate'])}**",
        f"- verdicts: supported={result['verdicts'].get('supported', 0)}, "
        f"contradicted={result['verdicts'].get('contradicted', 0)}, "
        f"unclear={result['verdicts'].get('unclear', 0)}",
        "",
        "## 逐条判定",
        "",
        "| 卡片 | 判定 | 说明 |",
        "|---|---|---|",
    ]
    for d in result["details"]:
        reason = (d["reason"] or "").replace("|", "\\|")
        lines.append(f"| {d['card_id'] or d['chunk_id']} | {d['verdict']} | {reason} |")
    lines.append("")
    return "\n".join(lines)


def print_human(result: dict) -> None:
    print(f"[fidelity] cards={result['cards']} eligible={result['eligible_cards']} sampled={result['sampled']}")
    if result["skipped"]:
        print(f"[fidelity] skipped: {result['skipped_reason']}")
        return
    print(
        f"[L1] hallucination_rate={_fmt_rate(result['hallucination_rate'])} "
        f"verdicts={result['verdicts']}"
    )
    for d in result["details"]:
        print(f"     - {d['card_id'] or d['chunk_id']}: {d['verdict']} ({d['reason']})")


def _reconfigure_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        except (AttributeError, ValueError):  # pragma: no cover
            pass


def main(argv: Optional[Sequence[str]] = None) -> int:
    _reconfigure_stdout()
    parser = argparse.ArgumentParser(
        description="L1 citation fidelity via LLM judge, sampled (docs/FORMATS.md §3)."
    )
    parser.add_argument("--kb", required=True, help="knowledge base directory, e.g. docs/biz")
    parser.add_argument("--root", required=True, help="source code root, e.g. <代码根>")
    parser.add_argument("--sample", type=float, default=0.3, help="fraction of eligible cards to judge")
    parser.add_argument("--json", action="store_true", help="print a single JSON object to stdout")
    parser.add_argument("--write-report", action="store_true", help="write markdown report to <kb>/verification/")
    args = parser.parse_args(argv)

    fraction = args.sample
    if fraction < 0:
        fraction = 0.0
    if fraction > 1:
        fraction = 1.0

    result = run(args.kb, args.root, fraction)

    if args.write_report:
        path = write_verification_report(args.kb, "L1-fidelity.md", build_report(result))
        if path:
            result["report_path"] = path
            if not args.json:
                print(f"[report] wrote {path}")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_human(result)

    if not result["cards"]:
        print(f"[fidelity] no knowledge cards under {args.kb}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
