# Pipeline recovery agent skill

Use the **Lifecycle Center Recovery** skill to help an agent diagnose a stuck promotion, recommend a recovery that preserves your release scope, and inspect evidence of what actually reached the target org.

**Advisory only:** the agent must not modify repository state or any Salesforce org. It provides commands and UI instructions for a human to execute. This includes leaving Git operations such as fetch, all promotions/deployments, Prepare, Combine, Back Sync, and test or workflow execution to the human. The agent reads existing evidence and results.

[Download the skill ZIP](downloads/lifecycle-center-recovery.zip)

The ZIP contains a portable `lifecycle-center-recovery/` folder with `SKILL.md`, focused diagnostic and recovery references, and Codex display metadata. It includes no credentials, environment bindings, or lab-specific permissions. You can share the ZIP with teammates; the recovery instructions do not require this repository or access to the manual.

## Use it

Extract the ZIP and install the entire folder in your agent's skills directory. For Codex, the personal directory is `$CODEX_HOME/skills`, or `~/.codex/skills` when `CODEX_HOME` is unset. Keep the bundled `references/` alongside `SKILL.md`. For another agent that supports Markdown skills, use its documented installation location; you can also supply `SKILL.md` and its references as context.

Example request:

```text
Use $lifecycle-center-recovery to diagnose our blocked Staging → Production
promotion. Inspect the stage PR and request logs. The invoice work must stay
in Staging. Identify a recovery that preserves the tested source version;
provide diagnosis and human-run repair steps only. Do not execute changes.
```

For a broken custom promotion:

```text
Use $lifecycle-center-recovery to investigate why this combined work item's
tests fail even though Staging passes. Compare the prepared PR with Staging
and identify where the manual resolution was lost.
```

Provide the repository/PR and relevant environment roles when available. The skill uses the connected tools or CLI access your agent already has; it does not configure Salesforce or GitHub authentication. The skill does not provide an agent-executed repair mode; all state-changing steps are performed by a human.

## What it knows

- Work item conflicts versus stage-history conflicts.
- Prepared/combined branch repair after the final rebuild.
- Failed tests, held-back work, deletion reverts, and full-branch deployment scope.
- Silent rollbacks and discrepancies between branches and org content.
- How to verify checks, tests, deployed content, and remaining history conflicts.

The guidance is based on the [lab experiments](lab/index.md), with the same limitations as this manual: Lifecycle Center with GitHub, a single intermediate stage, and a Developer Edition release org. It is not a verified runbook for managed-package DevOps Center. It distinguishes observed recoveries from hypotheses and requires checking the current pipeline's evidence.

## Maintain and share

The maintained source lives in `site/skills/lifecycle-center-recovery/` in the lab project, or `skills/lifecycle-center-recovery/` in the published manual repository. Update it when a new experiment changes a recovery decision. MkDocs builds regenerate the ZIP from that source through `hooks/package_skill.py`, so the site's download follows the version being built.

For the full explanations and experiment links, see [Recovery options](conflicts/when-you-need-git.md), [Inspecting pipeline state](recipes/inspecting-state.md), and [Detailed recovery comparison](conflicts/recovery-matrix.md).
