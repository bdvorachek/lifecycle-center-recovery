"""Check tracked files and commit identities for accidental identifying material.

Run alongside `gitleaks git . --redact` and `gitleaks dir . --redact`.
Patterns are a guardrail, not proof that every kind of private information is absent.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "email address": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "Salesforce org ID": re.compile(r"\b00D[A-Za-z0-9]{12}(?:[A-Za-z0-9]{3})?\b"),
    "local home path": re.compile(r"/(?:Users|home)/[A-Za-z0-9_.-]+/"),
    "Salesforce org hostname": re.compile(r"[A-Za-z0-9-]+\.(?:my\.salesforce|lightning\.force)\.com"),
}
ALLOWED_EMAILS = {"noreply@salesforce.com", "29205460+bdvorachek@users.noreply.github.com"}


def check(text, label):
    failures = []
    for kind, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            if kind == "email address" and match.group() in ALLOWED_EMAILS:
                continue
            line = text.count("\n", 0, match.start()) + 1
            failures.append(f"{label}:{line}: possible {kind} (value redacted)")
    return failures


def main():
    names = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    failures = []
    for name in filter(None, names):
        path = ROOT / name
        if path.is_symlink():
            failures.append(f"{name}: symlink not permitted in standalone export")
        else:
            content = path.read_text(encoding="utf-8")
            failures.extend(check(content, name))
            if name.startswith("docs/lab/") and re.search(
                r"\d{4}-\d{2}-\d{2}T\d|(?<!\d)\d{1,2}:\d{2}(?::\d{2})?", content
            ):
                failures.append(f"{name}: experimental clock time or partial ISO timestamp")
    history = subprocess.check_output(
        ["git", "log", "--all", "--format=%an <%ae>%n%cn <%ce>%n%B"], cwd=ROOT
    ).decode()
    failures.extend(check(history, "commit metadata"))
    if failures:
        print("\n".join(failures))
        return 1
    print(f"Privacy patterns passed for {len(list(filter(None, names)))} tracked files and commit metadata.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
