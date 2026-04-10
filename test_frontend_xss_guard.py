#!/usr/bin/env python3
# test_frontend_xss_guard.py
# Static regression checks to avoid reintroducing dangerous innerHTML patterns.

import re
import sys
from pathlib import Path


JS_FILES = [
    Path("static/js/app.js"),
    Path("static/js/members.js"),
    Path("static/js/visitors.js"),
]


INNERHTML_WITH_INTERP = re.compile(r"\.innerHTML\s*=\s*`[^`]*\$\{", re.MULTILINE)
INNERHTML_PLUS = re.compile(r"\.innerHTML\s*=\s*[^;]*\+", re.MULTILINE)


def main() -> int:
    repo = Path(__file__).resolve().parent
    failures = []

    for rel in JS_FILES:
        p = repo / rel
        if not p.exists():
            failures.append(f"Missing file: {rel}")
            continue

        s = p.read_text(encoding="utf-8")
        # We allow constant template literals (no ${}) for safe static HTML chunks (e.g. empty-state SVG).
        if INNERHTML_WITH_INTERP.search(s):
            failures.append(f"{rel}: innerHTML uses template interpolation (${{}}) — XSS risk")

        # Guard against concatenating strings into innerHTML (often fed by data).
        if INNERHTML_PLUS.search(s):
            failures.append(f"{rel}: innerHTML uses string concatenation (+) — likely unsafe")

    if failures:
        print("❌ Frontend XSS guard failed:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("✅ Frontend XSS guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

