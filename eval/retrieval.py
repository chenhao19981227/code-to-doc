#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eval/retrieval.py --- KB card parser, citation parser and a pure-Python BM25 retriever.

This module is the shared foundation for the whole evaluation harness. It implements
two contracts from ``docs/FORMATS.md``:

* **Card format** (FORMATS.md §1.2 / §1.3). The retrieval unit is one ``^## `` block.
  Each card carries five bullet fields ``- **类型**: ...`` / ``同义词`` / ``模块`` /
  ``置信度`` / ``溯源``. Mermaid fenced blocks inside a card are kept verbatim in the
  chunk text (they are just part of the body).
* **Citation format** (FORMATS.md §1.2). ``溯源`` holds one or more
  ``path:startLine-endLine`` (a single ``path:line`` is also accepted), comma separated
  and usually wrapped in backticks. Paths are relative to the code root passed to the
  callers (``--root``), *not* to this file.

Nothing here touches the network and there are no third-party dependencies. The BM25
implementation is hand-written (no ``rank_bm25`` / ``numpy``).

Tokenisation notes
------------------
Latin/digit runs (length >= 2) are used directly. CJK runs are expanded into single
characters **and** character bigrams, which is a cheap and dependency-free way to give
Chinese text usable term statistics.

Public helpers used by the other scripts:

* :func:`parse_kb`               -> ``(cards, warnings)``
* :func:`resolve_citation_path`  -> absolute ``Path`` or ``None``
* :func:`read_source_lines`      -> list of lines or ``None``
* :func:`card_claim_text`        -> card body without the metadata bullets
* :func:`norm_rel`               -> POSIX-normalised relative path
* :func:`write_verification_report` -> write a markdown report under ``<kb>/verification``
* :class:`BM25Retriever`

CLI (ad-hoc testing)::

    python eval/retrieval.py --kb docs/biz "发票什么时候生成" --k 5 [--json]
"""

from __future__ import annotations

import argparse
import json
import math
import os
import posixpath
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

# --------------------------------------------------------------------------- #
# Regexes
# --------------------------------------------------------------------------- #

#: Cuts a markdown file into retrieval units (one per ``## `` heading).
CARD_SPLIT_RE = re.compile(r"^## ", re.MULTILINE)

#: ``- **字段**: value`` (also accepts ``- *字段*:`` and full-width colon).
BULLET_RE = re.compile(
    r"^[ \t]*[-*][ \t]*\*\*(?P<key>[^*]+?)\*\*[ \t]*[:：][ \t]*(?P<value>.*?)[ \t]*$",
    re.MULTILINE,
)

#: Card id prefix, e.g. ``BR-001`` (see FORMATS.md §1.2).
CARD_ID_RE = re.compile(r"^[ \t]*(?P<id>[A-Z][A-Z0-9]*-\d+)\b")

#: ``path:line`` or ``path:line-line`` (accepts ``-``, ``–``, ``—``, ``~`` as range
#: separators and both ASCII / full-width colons).  An optional Windows drive prefix
#: is tolerated.  Paths are validated separately (must look path-ish).
CITATION_RE = re.compile(
    r"(?P<path>(?:[A-Za-z]:)?[^\s,;，；、`\"'()\[\]{}<>|]+?)"
    r"[:：](?P<start>\d+)(?:[ \t]*[-–—~][ \t]*(?P<end>\d+))?"
)

#: Field names that the contract marks as required (FORMATS.md §1.2).
REQUIRED_FIELDS = ("类型", "同义词", "模块", "置信度", "溯源")

_PILL_TO_CONFIDENCE = {"🟢": "confirmed", "🟡": "inferred", "🔴": "gap"}

_CJK_RUN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]+")
_LATIN_RE = re.compile(r"[a-z0-9_]+")

#: A line is comment-only when its first non-blank characters match one of these.
#: The bare ``*`` catches Javadoc/block-comment continuation lines such as `` * foo``.
_LINE_COMMENT_PREFIXES = ("//", "/*", "*/", "*", "#", "<!--", "--", "'''", '"""')


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #


@dataclass
class Citation:
    """A single ``path:startLine-endLine`` source reference from a card's ``溯源``."""

    path: str
    start_line: int
    end_line: int
    raw: str = ""

    @property
    def slug(self) -> str:
        return f"{self.path}:{self.start_line}-{self.end_line}"


@dataclass
class Card:
    """One ``## `` retrieval unit (a knowledge card, or a whole-file fallback)."""

    card_id: str
    title: str
    source_path: str
    chunk_index: int
    body: str
    fields: Dict[str, str] = field(default_factory=dict)
    citations: List[Citation] = field(default_factory=list)
    confidence: str = ""  # confirmed | inferred | gap | "" (unknown)
    is_file_chunk: bool = False

    @property
    def chunk_id(self) -> str:
        return f"{self.source_path}#{self.chunk_index}"

    @property
    def synonyms(self) -> str:
        return self.fields.get("同义词", "")

    @property
    def module(self) -> str:
        return self.fields.get("模块", "")

    @property
    def type(self) -> str:
        return self.fields.get("类型", "")

    def to_meta(self) -> dict:
        """Small, JSON-friendly description (no body) used in reports."""
        return {
            "chunk_id": self.chunk_id,
            "card_id": self.card_id,
            "title": self.title,
            "source_path": self.source_path,
            "module": self.module,
            "type": self.type,
            "confidence": self.confidence,
            "citations": [c.slug for c in self.citations],
        }


# --------------------------------------------------------------------------- #
# Parsing helpers
# --------------------------------------------------------------------------- #


def norm_rel(path: str) -> str:
    """POSIX-normalise a path for comparison (``\\`` -> ``/``, strips ``./``)."""
    s = (path or "").strip().replace("\\", "/")
    if not s:
        return ""
    s = posixpath.normpath(s)
    if s == ".":
        return ""
    while s.startswith("./"):
        s = s[2:]
    return s.lstrip("/")


def parse_confidence(value: str) -> str:
    """Map a ``置信度`` value (``🟢 confirmed`` etc.) to a canonical level."""
    v = value or ""
    for pill, name in _PILL_TO_CONFIDENCE.items():
        if pill in v:
            return name
    low = v.strip().lower()
    for name in ("confirmed", "inferred", "gap"):
        if name in low:
            return name
    return ""


def parse_citations(raw_value: str) -> List[Citation]:
    """Extract citations from a ``溯源`` field value.

    Backtick-wrapped spans are preferred (that is the documented card syntax); if
    none are present the whole value is scanned.  Robust against prose around the
    citations and against malformed entries (they are returned as-is so the L0
    checker can flag them instead of crashing).
    """
    if not raw_value:
        return []
    spans = re.findall(r"`([^`]+)`", raw_value)
    text = " , ".join(spans) if spans else raw_value

    out: List[Citation] = []
    seen = set()
    for m in CITATION_RE.finditer(text):
        path = m.group("path").strip()
        # A citation path must look path-ish (has a separator or an extension).
        if not (("/" in path) or ("\\" in path) or ("." in path)):
            continue
        try:
            start = int(m.group("start"))
            end = int(m.group("end")) if m.group("end") else start
        except (TypeError, ValueError):  # pragma: no cover - regex guarantees digits
            continue
        key = (path, start, end)
        if key in seen:
            continue
        seen.add(key)
        out.append(Citation(path=path, start_line=start, end_line=end, raw=m.group(0).strip()))
    return out


def _first_h1(text: str) -> str:
    m = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def parse_card(block: str, source_path: str, chunk_index: int) -> Card:
    """Parse a single ``## `` block into a :class:`Card`. Never raises."""
    first_line = block.split("\n", 1)[0]
    heading = re.sub(r"^##\s*", "", first_line).strip()

    fields: Dict[str, str] = {}
    try:
        for m in BULLET_RE.finditer(block):
            key = m.group("key").strip()
            if key and key not in fields:
                fields[key] = m.group("value").strip()
    except re.error as exc:  # pragma: no cover - defensive only
        fields["_parse_error"] = str(exc)

    card_id = ""
    title = heading
    m_id = CARD_ID_RE.match(heading)
    if m_id:
        card_id = m_id.group("id")
        title = heading[m_id.end():].strip(" -–—:：") or heading

    confidence = parse_confidence(fields.get("置信度", ""))
    citations = parse_citations(fields.get("溯源", ""))

    return Card(
        card_id=card_id,
        title=title,
        source_path=source_path,
        chunk_index=chunk_index,
        body=block.rstrip("\n"),
        fields=fields,
        citations=citations,
        confidence=confidence,
    )


def _split_file(text: str, source_path: str, warnings: List[str]) -> List[Card]:
    """Split one markdown file into cards on ``^## ``; fall back to a file chunk."""
    matches = list(CARD_SPLIT_RE.finditer(text))
    if not matches:
        body = text.strip()
        if not body:
            return []
        title = _first_h1(text) or Path(source_path).stem
        return [
            Card(
                card_id="",
                title=title,
                source_path=source_path,
                chunk_index=1,
                body=body,
                fields={},
                citations=[],
                confidence="",
                is_file_chunk=True,
            )
        ]

    out: List[Card] = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end].rstrip("\n")
        try:
            card = parse_card(block, source_path, i + 1)
        except Exception as exc:  # noqa: BLE001 - never crash on a malformed card
            warnings.append(f"failed to parse card #{i + 1} in {source_path}: {exc}")
            continue
        # Only validate blocks that declare themselves as knowledge cards (a card id
        # such as ``BR-001`` and/or a ``类型`` field).  Prose sections -- e.g. an
        # overview file's ``## 业务能力`` -- are kept as retrievable chunks but are
        # not reported as malformed cards.
        if card.card_id or "类型" in card.fields:
            for req in REQUIRED_FIELDS:
                if req not in card.fields:
                    warnings.append(f"{source_path}#{i + 1} missing required field **{req}**")
        out.append(card)
    return out


#: KB files that are process artifacts rather than business knowledge.  They read like
#: plausible prose but carry no domain facts, yet they demonstrably surface in top-k
#: (``questions.md`` ranked #2 for a credit question).  Excluded from the index.
_INDEX_EXCLUDE_FILES = frozenset({"gaps.md", "questions.md", "confidence-report.md"})


def parse_kb(kb_dir: str) -> Tuple[List[Card], List[str]]:
    """Parse every ``*.md`` under ``kb_dir`` into cards.

    ``verification/`` is skipped (it holds our own reports, not knowledge), as are the
    process artifacts in ``_INDEX_EXCLUDE_FILES``. Missing or empty directories are
    tolerated and reported through the warnings list. Results are deterministic: files
    sorted by relative path, cards by position inside the file.
    """
    warnings: List[str] = []
    cards: List[Card] = []
    base = Path(kb_dir)
    if not base.exists() or not base.is_dir():
        return cards, [f"knowledge base directory not found or empty: {kb_dir}"]

    files = sorted((p for p in base.rglob("*.md") if p.is_file()), key=lambda p: p.as_posix())
    for f in files:
        rel = f.relative_to(base).as_posix()
        if "verification" in rel.split("/"):
            continue
        if f.name in _INDEX_EXCLUDE_FILES:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            warnings.append(f"cannot read {rel}: {exc}")
            continue
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        cards.extend(_split_file(text, rel, warnings))
    return cards, warnings


def card_claim_text(card: Card) -> str:
    """Return the card's assertions (title + prose) with the metadata bullets removed."""
    kept = [ln for ln in card.body.split("\n") if not BULLET_RE.match(ln)]
    txt = "\n".join(kept).strip()
    return txt or card.body


# --------------------------------------------------------------------------- #
# Source-file helpers
# --------------------------------------------------------------------------- #


def resolve_citation_path(root: Optional[str], citation_path: str) -> Optional[Path]:
    """Resolve a citation path relative to ``root``; return the ``Path`` or ``None``.

    Both ``/`` and ``\\`` separators are accepted. An absolute citation that exists is
    honoured as a fallback. Only regular files are returned.
    """
    if not citation_path:
        return None
    raw = citation_path.strip().strip("`\"'")
    if not raw:
        return None

    candidates: List[Path] = []
    as_forward = raw.replace("\\", "/")
    p = Path(as_forward)
    if p.is_absolute():
        candidates.append(p)
    elif root:
        candidates.append(Path(root) / as_forward)
        candidates.append(Path(root) / raw)
    else:
        candidates.append(Path(as_forward))

    for c in candidates:
        try:
            if c.is_file():
                return c
        except OSError:
            continue
    return None


def read_source_lines(path: Path) -> Optional[List[str]]:
    """Read a file into a list of lines (newlines stripped); ``None`` if unreadable."""
    try:
        data = Path(path).read_text(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        return None
    data = data.replace("\r\n", "\n").replace("\r", "\n")
    return data.split("\n")


def is_meaningful_line(line: str) -> bool:
    """True if a line is neither blank nor a comment-only line (FORMATS.md §3.4)."""
    s = line.strip()
    if not s:
        return False
    for prefix in _LINE_COMMENT_PREFIXES:
        if s.startswith(prefix):
            return False
    return True


def write_verification_report(kb_dir: str, filename: str, markdown: str) -> Optional[str]:
    """Write ``markdown`` to ``<kb_dir>/verification/<filename>``. Returns the path."""
    try:
        d = Path(kb_dir) / "verification"
        d.mkdir(parents=True, exist_ok=True)
        target = d / filename
        target.write_text(markdown, encoding="utf-8")
        return str(target)
    except OSError as exc:  # pragma: no cover - defensive
        print(f"[report] could not write {filename}: {exc}", file=sys.stderr)
        return None


# --------------------------------------------------------------------------- #
# BM25
# --------------------------------------------------------------------------- #


def tokenize(text: str) -> List[str]:
    """Tokenise text: latin/digit runs, plus CJK unigrams and bigrams."""
    text = (text or "").lower()
    tokens: List[str] = []
    for m in _LATIN_RE.finditer(text):
        t = m.group(0)
        if len(t) >= 2:
            tokens.append(t)
    for m in _CJK_RUN_RE.finditer(text):
        run = m.group(0)
        tokens.extend(run)
        for i in range(len(run) - 1):
            tokens.append(run[i : i + 2])
    return tokens


class BM25Retriever:
    """Pure-Python Okapi BM25 over KB cards (``k1=1.5``, ``b=0.75`` by default)."""

    def __init__(self, kb_dir: str, k1: float = 1.5, b: float = 0.75) -> None:
        self.kb_dir = str(kb_dir)
        self.k1 = k1
        self.b = b
        self.cards: List[Card]
        self.warnings: List[str]
        self.cards, self.warnings = parse_kb(kb_dir)

        self._n = len(self.cards)
        self._doc_len: List[int] = []
        self._postings: Dict[str, List[Tuple[int, int]]] = {}
        self._idf: Dict[str, float] = {}
        self._avgdl = 0.0
        self._build()

    def _build(self) -> None:
        df: Dict[str, int] = {}
        for i, card in enumerate(self.cards):
            toks = tokenize(card.body)
            self._doc_len.append(len(toks))
            counts: Dict[str, int] = {}
            for t in toks:
                counts[t] = counts.get(t, 0) + 1
            for t, tf in counts.items():
                self._postings.setdefault(t, []).append((i, tf))
                df[t] = df.get(t, 0) + 1
        self._avgdl = (sum(self._doc_len) / self._n) if self._n else 0.0
        self._idf = {
            t: math.log(1.0 + (self._n - d + 0.5) / (d + 0.5)) for t, d in df.items()
        }

    @property
    def n_chunks(self) -> int:
        return self._n

    def search(self, query: str, k: int = 5, dedup: bool = True) -> List[dict]:
        """Return the top-``k`` cards as dicts ``{chunk_id,title,text,score,source_path}``.

        A knowledge base routinely contains the same logical card more than once
        (e.g. a per-module view under ``modules/`` and a global file such as
        ``rules.md`` both carry ``BR-012``).  Left alone, those duplicates consume
        several of the ``k`` slots with identical content, so retrieval effectively
        returns far fewer distinct cards than ``k``.  With ``dedup=True`` (default)
        only the highest-scoring copy of each distinct card is kept; distinctness is
        the card id when present, otherwise the normalised title.
        """
        if k <= 0 or self._n == 0 or not query or not query.strip():
            return []
        q_tokens = list(dict.fromkeys(tokenize(query)))
        scores = [0.0] * self._n
        for t in q_tokens:
            posting = self._postings.get(t)
            if not posting:
                continue
            idf = self._idf[t]
            for i, tf in posting:
                denom = tf + self.k1 * (1.0 - self.b + self.b * self._doc_len[i] / self._avgdl)
                if denom <= 0:  # pragma: no cover - defensive
                    continue
                scores[i] += idf * (tf * (self.k1 + 1.0)) / denom

        order = sorted(
            range(self._n),
            key=lambda i: (-scores[i], self.cards[i].source_path, self.cards[i].chunk_index),
        )
        results: List[dict] = []
        seen: set = set()
        for i in order:
            if scores[i] <= 0.0:
                break
            card = self.cards[i]
            if dedup:
                key = card.card_id or card.title.strip().lower()
                if key in seen:
                    continue
                seen.add(key)
            results.append(
                {
                    "chunk_id": card.chunk_id,
                    "title": card.title,
                    "text": card.body,
                    "score": scores[i],
                    "source_path": card.source_path,
                }
            )
            if len(results) >= k:
                break
        return results


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _reconfigure_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        except (AttributeError, ValueError):  # pragma: no cover - non-reconfigurable
            pass


def _main(argv: Optional[Sequence[str]] = None) -> int:
    _reconfigure_stdout()
    parser = argparse.ArgumentParser(
        description="Ad-hoc BM25 query over a generated knowledge base (docs/FORMATS.md §1.2)."
    )
    parser.add_argument("--kb", required=True, help="knowledge base directory, e.g. docs/biz")
    parser.add_argument("--k", type=int, default=5, help="number of chunks to return (default 5)")
    parser.add_argument("--json", action="store_true", help="machine-readable JSON output")
    parser.add_argument("query", nargs="*", help="query text")
    args = parser.parse_args(argv)

    query = " ".join(args.query).strip()
    retriever = BM25Retriever(args.kb)

    if retriever.n_chunks == 0:
        msg = f"[retrieval] no KB chunks found under: {args.kb}"
        if args.json:
            print(json.dumps({"kb": args.kb, "chunks": 0, "query": query, "results": [], "warning": msg}, ensure_ascii=False))
        else:
            print(msg)
        return 0

    if not query:
        msg = f"[retrieval] {retriever.n_chunks} chunk(s) indexed. Provide a query, e.g. `--kb {args.kb} 发票 生成`."
        if args.json:
            print(json.dumps({"kb": args.kb, "chunks": retriever.n_chunks, "query": "", "results": [], "warning": msg}, ensure_ascii=False))
        else:
            print(msg)
        return 0

    results = retriever.search(query, args.k)
    if args.json:
        print(json.dumps({"kb": args.kb, "chunks": retriever.n_chunks, "query": query, "results": results}, ensure_ascii=False, indent=2))
        return 0

    print(f"[retrieval] {retriever.n_chunks} chunk(s) indexed; top {len(results)} for: {query}")
    for rank, r in enumerate(results, 1):
        print(f"  {rank}. score={r['score']:.3f}  {r['chunk_id']}  {r['title']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
