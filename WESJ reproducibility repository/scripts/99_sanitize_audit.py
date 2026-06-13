from __future__ import annotations

"""Audit the public package for private data and identifying information.

Inputs: all repository files plus an optional untracked sensitive-term list.
Parameters: private directories, text suffixes, and identifier patterns.
Outputs: pass/fail console report; no research result.
Paper/SI: repository-level reproducibility and data-governance support, not an
analytical method reported in the manuscript.
"""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".yml",
    ".yaml",
    ".txt",
    ".csv",
    ".gitignore",
}
PRIVATE_DIRECTORIES = {"data", "outputs", "logs", "scratch"}
PATTERNS = {
    "Windows absolute path": re.compile(r"\b[A-Za-z]:[\\/]"),
    "UNC path": re.compile(r"\\\\[A-Za-z0-9_.-]+\\"),
    "email address": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),
}


def excluded(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if any(part in PRIVATE_DIRECTORIES for part in relative.parts):
        return True
    if relative.as_posix() in {
        "config/paths_local.yaml",
        "config/sensitive_terms.local.txt",
        "scripts/99_sanitize_audit.py",
    }:
        return True
    return False


def local_sensitive_terms() -> list[str]:
    path = ROOT / "config" / "sensitive_terms.local.txt"
    if not path.exists():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def main() -> None:
    findings: list[str] = []
    terms = local_sensitive_terms()

    for path in ROOT.rglob("*"):
        if not path.is_file() or excluded(path):
            continue
        relative = path.relative_to(ROOT)
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != ".gitignore":
            findings.append(f"Unexpected non-text file: {relative}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append(f"{relative}:{line}: {label}")
        lower_text = text.casefold()
        for term in terms:
            if term.casefold() in lower_text:
                findings.append(f"{relative}: local sensitive term: {term}")

    for private_directory in PRIVATE_DIRECTORIES:
        path = ROOT / private_directory
        if path.exists() and any(item.is_file() for item in path.rglob("*")):
            findings.append(f"Private directory contains files: {private_directory}/")

    if findings:
        print("Sanitization audit failed:")
        for finding in findings:
            print(f"  - {finding}")
        raise SystemExit(1)
    print("Sanitization audit passed: no flagged data or identifiers found.")


if __name__ == "__main__":
    main()
