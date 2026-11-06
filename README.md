# Lifecycle Center: Promotion Mechanics

How Salesforce Lifecycle Center (formerly next-generation DevOps Center) actually uses Git, and how to recover when promotions
conflict or get stuck. Unofficial. Based on experiments with a real pipeline in October–November 2026. Covers Lifecycle Center with GitHub; the managed-package DevOps Center version differs.

[Read the published manual](https://bdvorachek.github.io/lifecycle-center-recovery/).

## Read it locally

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/mkdocs serve        # http://127.0.0.1:8000
```

Pages are in `docs/`; the normalized experiment notebook is in `docs/lab/`. This repository is self-contained: it does not need the original Salesforce project, org configuration, or lab checkout.

## Shareable recovery skill

See [usage and installation](docs/agent-skill.md). The source is in `skills/lifecycle-center-recovery/`; every MkDocs build packages it into `docs/downloads/lifecycle-center-recovery.zip`. Update the skill alongside the guide when recovery evidence changes.

## Privacy

See [sharing and privacy](PRIVACY.md) for the export boundaries and repeatable checks. Build output and generated downloads are ignored; build the site to generate a shareable skill ZIP.

## Publishing

Pushes to `main` run privacy checks, build the manual and skill ZIP, and deploy to GitHub Pages. The workflow can also be started manually from Actions. Only the generated `site-build/` directory is deployed.
