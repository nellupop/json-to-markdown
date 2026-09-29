#!/usr/bin/env python3
"""
json_to_markdown.py

Dependency-free local command: renders a JSON array of job/service
records into a Markdown table.

Usage:
    python3 json_to_markdown.py <input.json>

Exit codes:
    0  success, Markdown table printed to stdout
    1  validation or read/parse error, nothing printed to stdout,
       one or more "error: ..." lines printed to stderr
    2  usage error (wrong number of arguments)

No network calls, no shell execution, no external dependencies, and
the input file is opened read-only (never modified).
"""

import json
import sys

REQUIRED_FIELDS = ["id", "title", "description", "rewardAtoms", "status"]
STRING_FIELDS = ["title", "description", "status"]
ATOMS_PER_USDC = 1_000_000  # USDC uses 6 decimal places


def escape_cell(value: str) -> str:
    """Make a value safe as a single Markdown table cell: pipes,
    newlines and angle brackets become literal text instead of
    breaking the table structure or injecting raw HTML."""
    s = value
    s = s.replace("\\", "\\\\")
    s = s.replace("|", "\\|")
    s = s.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")
    s = s.replace("<", "&lt;").replace(">", "&gt;")
    return s


def format_reward(atoms: int) -> str:
    whole, frac = divmod(atoms, ATOMS_PER_USDC)
    return f"{whole}.{frac:06d} USDC"


def validate(data):
    errors = []
    seen_ids = {}

    if not isinstance(data, list):
        return ["top-level JSON must be an array of job records"]

    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"record {idx}: not an object")
            continue

        missing = [f for f in REQUIRED_FIELDS if f not in item]
        if missing:
            errors.append(
                f"record {idx} (id={item.get('id', '?')!r}): "
                f"missing required field(s): {', '.join(missing)}"
            )
            continue

        rid = item["id"]
        if not isinstance(rid, str) or not rid:
            errors.append(f"record {idx}: 'id' must be a non-empty string")
        elif rid in seen_ids:
            errors.append(
                f"record {idx}: duplicate id {rid!r} "
                f"(already used by record {seen_ids[rid]})"
            )
        else:
            seen_ids[rid] = idx

        for field in STRING_FIELDS:
            if not isinstance(item[field], str):
                errors.append(
                    f"record {idx} (id={rid!r}): field {field!r} must be a string"
                )

        reward = item["rewardAtoms"]
        if isinstance(reward, bool) or not isinstance(reward, int):
            errors.append(
                f"record {idx} (id={rid!r}): rewardAtoms must be a canonical "
                f"non-negative JSON integer (no decimals, no string), "
                f"got {reward!r}"
            )
        elif reward < 0:
            errors.append(
                f"record {idx} (id={rid!r}): rewardAtoms must be non-negative, "
                f"got {reward}"
            )

    return errors


def render(data) -> str:
    lines = [
        "| Title | Description | Job ID | Reward | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in data:
        title = escape_cell(item["title"])
        desc = escape_cell(item["description"])
        jid = escape_cell(item["id"])
        reward = format_reward(item["rewardAtoms"])
        status = escape_cell(item["status"])
        lines.append(f"| {title} | {desc} | {jid} | {reward} | {status} |")
    return "\n".join(lines)


def main(argv):
    if len(argv) != 2:
        print("usage: json_to_markdown.py <input.json>", file=sys.stderr)
        return 2

    path = argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as e:
        print(f"error: cannot read file: {e}", file=sys.stderr)
        return 1

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 1

    errors = validate(data)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1

    print(render(data))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
