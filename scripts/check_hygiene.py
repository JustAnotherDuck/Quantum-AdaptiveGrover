#!/usr/bin/env python3
"""Code hygiene checker for AdaptiveGrover-QCA.

Strictly verifies that:
1. Zero emojis exist in source code, tests, configs, scripts, documentation, and metadata.
2. No decorative non-ASCII symbols exist where clean ASCII or standard LaTeX should be used.
Exits with code 0 if hygiene passes, non-zero if violations are found.
"""

import os
import sys
from typing import List, Tuple

# Paths to ignore during scanning
EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
}
EXCLUDE_EXTS = {".png", ".jpg", ".jpeg", ".ico", ".svg", ".pyc", ".lock", ".pdf"}


def is_emoji(char: str) -> bool:
    cp = ord(char)
    # Emoji and decorative symbol ranges
    return (
        0x1F600 <= cp <= 0x1F64F  # Emoticons
        or 0x1F300 <= cp <= 0x1F5FF  # Misc Symbols and Pictographs
        or 0x1F680 <= cp <= 0x1F6FF  # Transport and Map
        or 0x1F1E0 <= cp <= 0x1F1FF  # Flags
        or 0x2700 <= cp <= 0x27BF  # Dingbats
        or 0x1F900 <= cp <= 0x1F9FF  # Supplemental Symbols and Pictographs
        or 0x1FA00 <= cp <= 0x1FA6F  # Chess, symbols
        or 0x1FA70 <= cp <= 0x1FAFF  # Symbols and Pictographs Extended-A
        or 0x2600 <= cp <= 0x26FF  # Misc symbols (warning, checkmark, atom, etc.)
        or 0x2B50 <= cp <= 0x2B55  # Stars and shapes
    )


def scan_file(filepath: str) -> List[Tuple[int, str, str]]:
    violations = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_no, line in enumerate(f, 1):
                for ch in line:
                    if is_emoji(ch):
                        violations.append((line_no, ch, line.strip()))
                        break
    except Exception as exc:
        print(f"Warning: could not read {filepath}: {exc}", file=sys.stderr)
    return violations


def main() -> int:
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    total_violations = 0

    target_dirs = ["src", "tests", "experiments", "scripts", "docs", "paper_support", "dashboard"]
    files_to_check = ["README.md", "Makefile", "pyproject.toml", "requirements.txt"]

    all_paths = []
    for t_dir in target_dirs:
        full_t = os.path.join(root_dir, t_dir)
        if not os.path.exists(full_t):
            continue
        for r, dirs, files in os.walk(full_t):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext not in EXCLUDE_EXTS:
                    all_paths.append(os.path.join(r, f))

    for fname in files_to_check:
        full_f = os.path.join(root_dir, fname)
        if os.path.exists(full_f):
            all_paths.append(full_f)

    for path in all_paths:
        v = scan_file(path)
        if v:
            rel = os.path.relpath(path, root_dir)
            for line_no, ch, text in v:
                print(
                    f"[HYGIENE ERROR] {rel}:{line_no}: Found emoji/decorative symbol {repr(ch)}: {text[:60]}"
                )
                total_violations += 1

    if total_violations > 0:
        print(
            f"\nFailed: Found {total_violations} hygiene violation(s). Absolute zero-emoji policy enforced."
        )
        return 1

    print("Hygiene check passed: 0 emojis or decorative unicode found across repository.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
