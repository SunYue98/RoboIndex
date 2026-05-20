#!/usr/bin/env python3
"""Extract the final <json>...</json> block from an agent transcript file
and write a clean JSON batch file. Handles HTML entity escaping.

Usage:
    python3 extract_batch.py <task_output_file> <out_batch_file>
"""
import sys
import json
import html
import re
from pathlib import Path

if len(sys.argv) != 3:
    print("usage: extract_batch.py <task_output_file> <out_batch_file>", file=sys.stderr)
    sys.exit(2)

src = Path(sys.argv[1])
dst = Path(sys.argv[2])

raw = src.read_text(encoding="utf-8", errors="replace")

# The transcript is JSONL; the final assistant message contains <json>...</json>.
# We scan the whole raw text for the LAST occurrence of <json>...</json> (the agent's
# final compiled output). Multiple may exist if the agent showed drafts; we take the last.

# Look for both literal and HTML-escaped variants
patterns = [
    re.compile(r"<json>\s*(\[.*?\])\s*</json>", re.DOTALL),
    re.compile(r"&lt;json&gt;\s*(\[.*?\])\s*&lt;/json&gt;", re.DOTALL),
]

matches = []
for pat in patterns:
    matches.extend(pat.findall(raw))

if not matches:
    print(f"FAIL: no <json> block found in {src}", file=sys.stderr)
    sys.exit(1)

json_text = matches[-1]
# Unescape HTML entities (some agent outputs include &amp; &lt; &gt; &quot; inside the JSON)
json_text = html.unescape(json_text)

# Validate
try:
    data = json.loads(json_text)
except json.JSONDecodeError as e:
    # Try a more forgiving fix: agent may have used smart quotes or unescaped slashes
    print(f"FAIL: JSON parse error in {src}: {e}", file=sys.stderr)
    # Save raw extract for debugging
    debug_path = dst.with_suffix(".raw.txt")
    debug_path.write_text(json_text, encoding="utf-8")
    print(f"Raw extract written to {debug_path}", file=sys.stderr)
    sys.exit(1)

dst.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OK: extracted {len(data)} entries to {dst}")
