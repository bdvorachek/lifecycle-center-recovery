# Sharing and privacy

This is a standalone export of the Lifecycle Center recovery manual and agent skill. Its history starts fresh; the original lab repository and its commit metadata are not included.

Included: maintained guide pages, normalized experimental observations, portable skill, and local build tooling. Excluded: Salesforce authentication/configuration caches, original repository history, local environment files, publishing checkout, virtual environment, and machine-specific publishing script.

The experiment notes retain lab work-item/PR numbers, abbreviated commit hashes, experiment dates, test class names, and failure messages as evidence. Environment names are normalized. Exact experimental clock times and local-time-zone notes are removed; event order and useful elapsed durations remain. Git commit dates and GitHub activity timestamps are separate platform metadata. A public Salesforce service-account email remains in a quoted Git-author example. These are not live credentials. The repository owner and GitHub activity remain visible to people with repository access.

Before sharing changes:

```bash
python3 scripts/check_privacy.py
gitleaks dir . --redact --max-archive-depth 2
gitleaks git . --redact --log-opts=--all
.venv/bin/mkdocs build --strict
```

The pattern check covers tracked text files and commit metadata. Gitleaks checks common secret formats. Review added content and links as well: automated scanners cannot certify the absence of all confidential information. Keep real org details, business data and credentials out of screenshots and examples.

The repository and GitHub Pages site are public. Changes pushed to `main` publish automatically after the workflow checks and build succeed. Review content before pushing.
