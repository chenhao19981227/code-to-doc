#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eval/mechanical.py --- L0 citation validity + L2 coverage (no LLM).

Contract: ``docs/FORMATS.md`` §3.2 (layers), §3.3 (CLI), §3.4 (metric definitions).

L0 --- 引用有效性 (citation validity)
-----------------------------------
For every citation ``path:startLine-endLine`` found in a card's ``溯源`` field:

1. the file resolves relative to ``--root`` and exists;
2. ``1 <= startLine <= endLine <= <number of lines>``;
3. the cited slice contains at least one non-empty, non-comment-only line.

Reported metrics (exact names from FORMATS.md §3.2):

* ``total_citations``       --- number of citations parsed from the KB
* ``invalid_citation_rate`` --- invalid / total (0.0 when there are no citations)

Every failing citation is emitted in ``invalid_citations[]`` with a machine-readable
``reason`` (``file_not_found`` | ``unreadable`` | ``invalid_range`` |
``line_out_of_range`` | ``comment_only_or_blank``).

L2 --- 覆盖率 (coverage)
----------------------
A deterministic code-entity inventory is built from ``--root``:

* Java **type declarations** (``public class`` / ``interface`` / ``enum`` / ``record``
  / ``@interface``);
* **public methods** (explicit ``public`` modifier, body located by brace matching);
* **permission annotations** (``@PreAuthorize`` / ``@PostAuthorize`` / ``@RolesAllowed``
  / ``@Secured`` / ``@PermitAll`` / ``@DenyAll``).

Heuristics (documented on purpose):

* Only Java files are inventoried. Files under ``target`` / ``build`` / ``out`` /
  ``.git`` / ``.idea`` / ``.gradle`` / ``node_modules`` / ``test`` / ``tests`` are
  skipped, so coverage is about production code.
* Entity spans are found by brace matching, ignoring braces inside strings, chars,
  comments and Java text blocks. Constructors (no return type) are not counted.
* An entity is *referenced* when at least one citation resolves to the same file and
  its line range overlaps the entity span. Paths are compared after POSIX
  normalisation, with a suffix-match fallback for module-prefixed citations.

Reported metrics:

* ``coverage_rate``     --- referenced_entities / total_entities (0.0 if no entities)
* ``missing_entities[]`` --- every entity never referenced by any card

CLI::

    python eval/mechanical.py --kb docs/biz --root benchmark/killbill --json
    python eval/mechanical.py --kb docs/biz --root benchmark/killbill --write-report

Exit code is 0 on success, even when the KB or root is empty (a clear message is then
printed and null/zero metrics are reported).
"""

from __future__ import annotations

import argparse
import bisect
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from retrieval import (  # noqa: E402
    Card,
    is_meaningful_line,
    norm_rel,
    parse_kb,
    read_source_lines,
    resolve_citation_path,
    write_verification_report,
)

# --------------------------------------------------------------------------- #
# Inventory regexes (documented heuristics)
# --------------------------------------------------------------------------- #

# A single annotation, optionally with single-line arguments (`@Foo(bar)`).
_ANNOT = r"@[\w.]+(?:[ \t]*\([^)\n]*\))?"
# Unambiguous separator after an annotation (no nested `[ \t]*\n?[ \t]*`, which would
# allow combinatorial whitespace partitions and cause catastrophic backtracking).
_ANNOT_SEP = r"[ \t]*(?:\n[ \t]*)?"

TYPE_DECL_RE = re.compile(
    r"^[ \t]*(?:" + _ANNOT + _ANNOT_SEP + r")*"
    r"public[ \t]+"
    r"(?:(?:abstract|final|sealed|non-sealed|strictfp|static)[ \t]+)*"
    r"(?P<kind>@interface|class|interface|enum|record)[ \t]+"
    r"(?P<name>[A-Za-z_$][\w$]*)",
    re.MULTILINE,
)

# The return-type group requires each whitespace-separated token to be followed by
# whitespace.  This keeps the split points unique (a single identifier cannot be
# partitioned several ways), which is what avoids exponential backtracking on lines
# such as `public static final String NAME = ...` where no `(` ever follows.
METHOD_DECL_RE = re.compile(
    r"^[ \t]*(?:" + _ANNOT + _ANNOT_SEP + r")*"
    r"public[ \t]+"
    r"(?:(?:static|final|abstract|synchronized|native|default|strictfp)[ \t]+)*"
    r"(?P<ret>(?:[\w$.<>\[\],?]+[ \t]+)+)"
    r"(?P<name>[A-Za-z_$][\w$]*)[ \t]*\(",
    re.MULTILINE,
)

PERMISSION_RE = re.compile(
    r"@(?:PreAuthorize|PostAuthorize|RolesAllowed|Secured|PermitAll|DenyAll)\b"
)

SKIP_DIR_SEGMENTS = {
    "target",
    "build",
    "out",
    "bin",
    ".git",
    ".idea",
    ".gradle",
    ".mvn",
    "node_modules",
    "__pycache__",
    "test",
    "tests",
}


# --------------------------------------------------------------------------- #
# L0 --- citation validity
# --------------------------------------------------------------------------- #


def check_citations(cards: Sequence[Card], root: Optional[str]) -> dict:
    """Validate every citation; return the L0 result dict."""
    total = 0
    invalid: List[dict] = []

    for card in cards:
        for cit in card.citations:
            total += 1
            base_detail = {
                "chunk_id": card.chunk_id,
                "card_id": card.card_id,
                "title": card.title,
                "citation": cit.slug,
                "path": cit.path,
                "start_line": cit.start_line,
                "end_line": cit.end_line,
            }
            abs_path = resolve_citation_path(root, cit.path) if root else None
            if abs_path is None:
                invalid.append({**base_detail, "reason": "file_not_found"})
                continue
            lines = read_source_lines(abs_path)
            if lines is None:
                invalid.append({**base_detail, "reason": "unreadable"})
                continue
            n = len(lines)
            if cit.start_line < 1 or cit.end_line < cit.start_line:
                invalid.append({**base_detail, "reason": "invalid_range", "file_lines": n})
                continue
            if cit.start_line > n or cit.end_line > n:
                invalid.append({**base_detail, "reason": "line_out_of_range", "file_lines": n})
                continue
            segment = lines[cit.start_line - 1 : cit.end_line]
            if not any(is_meaningful_line(ln) for ln in segment):
                invalid.append({**base_detail, "reason": "comment_only_or_blank", "file_lines": n})

    valid = total - len(invalid)
    rate = (len(invalid) / total) if total else 0.0
    return {
        "total_citations": total,
        "valid_citations": valid,
        "invalid_citations_count": len(invalid),
        "invalid_citation_rate": rate,
        "invalid_citations": invalid,
    }


# --------------------------------------------------------------------------- #
# L2 --- code entity inventory + coverage
# --------------------------------------------------------------------------- #


def _line_starts(text: str) -> List[int]:
    starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            starts.append(i + 1)
    return starts


def _line_of(starts: Sequence[int], idx: int) -> int:
    return bisect.bisect_right(starts, idx)


def _match_brace(text: str, open_idx: int) -> Optional[int]:
    """Index just past the ``}`` matching the ``{`` at ``open_idx`` (or ``None``).

    Ignores braces inside line/block comments, strings, chars and Java text blocks.
    """
    if open_idx < 0 or open_idx >= len(text) or text[open_idx] != "{":
        return None
    depth = 0
    i = open_idx
    n = len(text)
    state = None  # None | 'line' | 'block' | 'str' | 'char' | 'text'
    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if state is None:
            if ch == "/" and nxt == "/":
                state = "line"
                i += 2
                continue
            if ch == "/" and nxt == "*":
                state = "block"
                i += 2
                continue
            if ch == '"':
                if text[i : i + 3] == '"""':
                    state = "text"
                    i += 3
                    continue
                state = "str"
                i += 1
                continue
            if ch == "'":
                state = "char"
                i += 1
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
            i += 1
        elif state == "line":
            if ch == "\n":
                state = None
            i += 1
        elif state == "block":
            if ch == "*" and nxt == "/":
                state = None
                i += 2
                continue
            i += 1
        elif state == "str":
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                state = None
            i += 1
        elif state == "char":
            if ch == "\\":
                i += 2
                continue
            if ch == "'":
                state = None
            i += 1
        elif state == "text":
            if text[i : i + 3] == '"""':
                state = None
                i += 3
                continue
            i += 1
    return None


def _find_body_open(text: str, after_paren: int) -> Optional[int]:
    """Given the index just after a method's ``(``, return the index of its body ``{``."""
    i = after_paren
    n = len(text)
    depth = 1
    while i < n:
        ch = text[i]
        if ch == '"':
            i += 1
            while i < n:
                if text[i] == "\\":
                    i += 2
                    continue
                if text[i] == '"':
                    break
                i += 1
            i += 1
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                j = i + 1
                while j < n and text[j] in " \t\r\n":
                    j += 1
                if text.startswith("throws", j):
                    brace = text.find("{", j)
                    semi = text.find(";", j)
                    if brace == -1 or (semi != -1 and semi < brace):
                        return None
                    return brace
                if j < n and text[j] == "{":
                    return j
                return None
        i += 1
    return None


def _extract_entities(text: str, rel: str) -> List[dict]:
    """Extract classes / interfaces / enums / records / public methods / permissions."""
    out: List[dict] = []
    starts = _line_starts(text)
    seen = set()

    def add(kind: str, name: str, start_idx: int, end_idx: int) -> None:
        s = _line_of(starts, start_idx)
        e = _line_of(starts, end_idx)
        if e < s:
            e = s
        key = (kind, name, s)
        if key in seen:
            return
        seen.add(key)
        out.append(
            {
                "id": f"{kind}:{rel}:{s}:{name}",
                "kind": kind,
                "name": name,
                "file": rel,
                "start_line": s,
                "end_line": e,
            }
        )

    for m in TYPE_DECL_RE.finditer(text):
        kind = m.group("kind")
        if kind == "@interface":
            kind = "annotation"
        open_idx = text.find("{", m.end())
        close_idx = _match_brace(text, open_idx) if open_idx != -1 else None
        end_idx = (close_idx - 1) if close_idx else m.end()
        add(kind, m.group("name"), m.start(), end_idx)

    for m in METHOD_DECL_RE.finditer(text):
        body_open = _find_body_open(text, m.end())
        if body_open is None:
            add("method", m.group("name"), m.start(), m.end())
            continue
        close_idx = _match_brace(text, body_open)
        end_idx = (close_idx - 1) if close_idx else body_open
        add("method", m.group("name"), m.start(), end_idx)

    for m in PERMISSION_RE.finditer(text):
        add("permission", m.group(0), m.start(), m.end())

    return out


def build_inventory(
    root: Optional[str], scope: Optional[Sequence[str]] = None
) -> Tuple[List[dict], List[str]]:
    """Walk ``--root`` and build the deterministic entity inventory.

    ``scope`` optionally restricts the walk to the given path prefixes
    (relative to ``root``, e.g. ``invoice`` / ``overdue``).  This keeps the L2
    denominator aligned with the extraction scope: when only a subset of
    modules becomes knowledge cards, inventorying the whole repository would
    make the coverage metric meaningless.
    """
    entities: List[dict] = []
    warnings: List[str] = []
    if not root:
        return entities, ["no --root provided; entity inventory is empty"]
    root_path = Path(root)
    if not root_path.exists() or not root_path.is_dir():
        return entities, [f"code root not found or not a directory: {root}"]

    scope_norm = [s.replace("\\", "/").strip("/") for s in scope if s.strip()] if scope else []
    if scope_norm:
        warnings.append(f"L2 inventory scoped to: {', '.join(scope_norm)}")

    files = sorted((p for p in root_path.rglob("*.java") if p.is_file()), key=lambda p: p.as_posix())
    for f in files:
        rel_parts = f.relative_to(root_path).parts
        if any(seg in SKIP_DIR_SEGMENTS for seg in rel_parts[:-1]):
            continue
        rel = "/".join(rel_parts)
        if scope_norm and not any(rel.startswith(s) for s in scope_norm):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            warnings.append(f"cannot read {rel}: {exc}")
            continue
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        try:
            entities.extend(_extract_entities(text, rel))
        except Exception as exc:  # noqa: BLE001 - never crash on a weird file
            warnings.append(f"inventory failed for {rel}: {exc}")
    return entities, warnings


def _citation_keys(cit, root: Optional[str]) -> List[str]:
    keys = [norm_rel(cit.path)]
    resolved = resolve_citation_path(root, cit.path) if root else None
    if resolved is not None:
        try:
            keys.append(norm_rel(resolved.relative_to(Path(root)).as_posix()))
        except (ValueError, OSError):
            keys.append(norm_rel(str(resolved)))
    return [k for k in keys if k]


def compute_coverage(cards: Sequence[Card], entities: Sequence[dict], root: Optional[str]) -> dict:
    """Compute ``coverage_rate`` and the missing-entity list."""
    exact: Dict[str, List[Tuple[int, int]]] = {}
    by_base: Dict[str, List[Tuple[str, Tuple[int, int]]]] = {}
    for card in cards:
        for cit in card.citations:
            rng = (cit.start_line, cit.end_line)
            for key in _citation_keys(cit, root):
                exact.setdefault(key, []).append(rng)
                base = key.rsplit("/", 1)[-1]
                by_base.setdefault(base, []).append((key, rng))

    referenced = 0
    missing: List[dict] = []
    by_kind: Dict[str, dict] = {}

    for ent in entities:
        kind = ent["kind"]
        stats = by_kind.setdefault(kind, {"total": 0, "referenced": 0})
        stats["total"] += 1

        ranges = list(exact.get(ent["file"], []))
        if not ranges:
            for key, rng in by_base.get(ent["file"].rsplit("/", 1)[-1], []):
                if key == ent["file"] or key.endswith("/" + ent["file"]) or ent["file"].endswith("/" + key):
                    ranges.append(rng)

        hit = any(
            not (r_end < ent["start_line"] or ent["end_line"] < r_start)
            for r_start, r_end in ranges
        )
        if hit:
            referenced += 1
            stats["referenced"] += 1
        else:
            missing.append(ent)

    total = len(entities)
    rate = (referenced / total) if total else 0.0
    return {
        "total_entities": total,
        "referenced_entities": referenced,
        "coverage_rate": rate,
        "entities_by_kind": by_kind,
        "missing_entities": missing,
    }


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #


def _fmt_rate(value: Optional[float]) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def build_report(result: dict) -> str:
    lines: List[str] = []
    lines.append("# L0 / L2 机械评测报告 (mechanical)")
    lines.append("")
    lines.append(f"- 生成时间: {result['generated_at']}")
    lines.append(f"- 知识库: `{result['kb']}`")
    lines.append(f"- 代码根: `{result['root']}`")
    lines.append(f"- 解析卡片数: {result['cards']}")
    lines.append("")
    lines.append("## L0 引用有效性")
    lines.append("")
    lines.append(f"- total_citations: {result['total_citations']}")
    lines.append(f"- valid_citations: {result['valid_citations']}")
    lines.append(f"- invalid_citations: {result['invalid_citations_count']}")
    lines.append(f"- **invalid_citation_rate: {_fmt_rate(result['invalid_citation_rate'])}**")
    lines.append("")
    if result["invalid_citations"]:
        lines.append("| 卡片 | 引用 | 原因 |")
        lines.append("|---|---|---|")
        for item in result["invalid_citations"][:200]:
            lines.append(f"| {item.get('card_id') or item['chunk_id']} | `{item['citation']}` | {item['reason']} |")
        if len(result["invalid_citations"]) > 200:
            lines.append(f"| … | 其余 {len(result['invalid_citations']) - 200} 条见 JSON | |")
    else:
        lines.append("无无效引用。")
    lines.append("")
    lines.append("## L2 覆盖率")
    lines.append("")
    lines.append(f"- total_entities: {result['total_entities']}")
    lines.append(f"- referenced_entities: {result['referenced_entities']}")
    lines.append(f"- **coverage_rate: {_fmt_rate(result['coverage_rate'])}**")
    lines.append("")
    if result["entities_by_kind"]:
        lines.append("| 类型 | 总数 | 被引用 | 覆盖率 |")
        lines.append("|---|---|---|---|")
        for kind, stats in sorted(result["entities_by_kind"].items()):
            t = stats["total"]
            r = stats["referenced"]
            lines.append(f"| {kind} | {t} | {r} | {_fmt_rate(r / t) if t else 'n/a'} |")
        lines.append("")
    missing = result["missing_entities"]
    if missing:
        lines.append(f"### 未被引用的实体（前 200 / 共 {len(missing)}）")
        lines.append("")
        lines.append("| 类型 | 名称 | 文件:行 |")
        lines.append("|---|---|---|")
        for ent in missing[:200]:
            lines.append(f"| {ent['kind']} | {ent['name']} | `{ent['file']}:{ent['start_line']}` |")
    else:
        lines.append("全部实体均被引用。")
    lines.append("")
    if result["warnings"]:
        lines.append("## 警告")
        lines.append("")
        for w in result["warnings"][:100]:
            lines.append(f"- {w}")
        lines.append("")
    return "\n".join(lines)


def print_human(result: dict) -> None:
    print(f"[mechanical] cards={result['cards']}  kb={result['kb']}  root={result['root']}")
    print(
        f"[L0] total_citations={result['total_citations']} "
        f"invalid={result['invalid_citations_count']} "
        f"invalid_citation_rate={_fmt_rate(result['invalid_citation_rate'])}"
    )
    for item in result["invalid_citations"][:10]:
        print(f"     - {item.get('card_id') or item['chunk_id']}: {item['citation']} -> {item['reason']}")
    print(
        f"[L2] total_entities={result['total_entities']} "
        f"referenced={result['referenced_entities']} "
        f"coverage_rate={_fmt_rate(result['coverage_rate'])}"
    )
    for kind, stats in sorted(result["entities_by_kind"].items()):
        t = stats["total"]
        r = stats["referenced"]
        print(f"     - {kind}: {r}/{t} ({_fmt_rate(r / t) if t else 'n/a'})")
    for w in result["warnings"][:10]:
        print(f"     ! {w}", file=sys.stderr)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _reconfigure_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        except (AttributeError, ValueError):  # pragma: no cover
            pass


def run(kb: str, root: str, scope: Optional[Sequence[str]] = None) -> dict:
    cards, warnings = parse_kb(kb)
    l0 = check_citations(cards, root)
    entities, inv_warnings = build_inventory(root, scope)
    l2 = compute_coverage(cards, entities, root)

    warnings = list(warnings) + list(inv_warnings)
    if not cards:
        warnings.append(f"no knowledge cards found under {kb}")
    if not entities:
        warnings.append(f"no code entities inventoried under {root}")

    return {
        "script": "mechanical",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "kb": kb,
        "root": root,
        "scope": list(scope) if scope else None,
        "cards": len(cards),
        # --- L0 (flat, exact metric names) ---
        "total_citations": l0["total_citations"],
        "valid_citations": l0["valid_citations"],
        "invalid_citations_count": l0["invalid_citations_count"],
        "invalid_citation_rate": l0["invalid_citation_rate"],
        "invalid_citations": l0["invalid_citations"],
        # --- L2 (flat, exact metric names) ---
        "total_entities": l2["total_entities"],
        "referenced_entities": l2["referenced_entities"],
        "coverage_rate": l2["coverage_rate"],
        "entities_by_kind": l2["entities_by_kind"],
        "missing_entities": l2["missing_entities"],
        # --- extras ---
        "warnings": warnings,
        "details": {"l0": l0, "l2": l2},
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    _reconfigure_stdout()
    parser = argparse.ArgumentParser(
        description="L0 citation validity + L2 coverage, no LLM (docs/FORMATS.md §3)."
    )
    parser.add_argument("--kb", required=True, help="knowledge base directory, e.g. docs/biz")
    parser.add_argument("--root", required=True, help="source code root, e.g. benchmark/killbill")
    parser.add_argument("--json", action="store_true", help="print a single JSON object to stdout")
    parser.add_argument("--write-report", action="store_true", help="write markdown report to <kb>/verification/")
    parser.add_argument(
        "--scope",
        default=None,
        help="comma-separated path prefixes under --root used to scope the L2 entity "
             "inventory (e.g. invoice,overdue).  Pass this when only a subset of modules "
             "was extracted, otherwise coverage is measured against the whole repository.",
    )
    args = parser.parse_args(argv)

    scope = [s.strip() for s in args.scope.split(",") if s.strip()] if args.scope else []
    result = run(args.kb, args.root, scope)

    if args.write_report:
        path = write_verification_report(args.kb, "L0-L2-mechanical.md", build_report(result))
        if path:
            result["report_path"] = path
            if not args.json:
                print(f"[report] wrote {path}")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_human(result)

    if not result["cards"]:
        print(f"[mechanical] no knowledge cards under {args.kb}; metrics reported as 0/empty.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
