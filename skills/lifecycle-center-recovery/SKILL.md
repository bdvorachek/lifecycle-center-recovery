---
name: lifecycle-center-recovery
description: Diagnose and recover stuck Salesforce Lifecycle Center promotions with GitHub, including work item conflicts, stage conflicts, broken combines, failed tests, silent rollbacks, and branch/org drift. Use for Lifecycle Center pipeline recovery, not managed-package DevOps Center or generic CI failures.
---

# Lifecycle Center recovery

Get the intended changes through the intended pipeline boundary, preserving held-back work and verifying the deployed result. This skill distills an unofficial lab's October–November 2026 experiments; observations are evidence for that configuration, not guarantees for every org or metadata type.

## Establish the boundary

Inspect available repository instructions, PRs and logs before asking for missing context. Identify:

- Repository, Lifecycle Center hub org, source/target stage branches and org aliases, and dev environment.
- Work items, failing PR/request, exact error, and path: work item promotion, Promote Stage, Prepare, or Combine.
- Intended final content, relevant tests, and work that must stay behind.

Never infer an org's role from its alias. The lab used one intermediate stage and a Developer Edition release org. Map roles explicitly in larger pipelines; Back Sync recipes start at the first stage, not an arbitrary later stage. Do not import lab credentials, org IDs, aliases, or destructive-operation permissions.

## Diagnose before choosing a recovery

Use [diagnostics](references/diagnostics.md) to compare four independent layers: Git history/content, GitHub PR/check state, Lifecycle Center records, and deployed org content. Collect only relevant components and records. If access is missing, state the missing evidence and give targeted read-only checks; do not claim a diagnosis is confirmed.

Read the relevant case in [recovery routes](references/recovery.md). Distinguish a text conflict from a failing check, deployment/test failure, semantic regression, or branch/org drift. A stale banner, Closed work item, passing provenance check, or merged PR alone does not prove success.

## Choose and carry out the scoped repair

Explain the evidence, intended final diff, affected orgs/branches, release scope, and verification before remote changes. Work within the user's authorization; a request to diagnose does not authorize a deployment, abandonment, deletion, or release of held-back work. Reuse existing authorization without asking again. Respect review/protection rules and do not bypass failing checks or tests.

Use a clean isolated checkout for conflict resolution and preserve the user's uncommitted work. Prefer a normal PR/merge over resets or force pushes. For stage-history repair, preserve merge ancestry: a squash/rebase of the reconciliation PR defeats the repair. Confirm the exact file versions to keep rather than blindly applying ours/theirs.

Prepare and Combine rebuild branches from original work item commits. Inspect the final PR after each rebuild; apply any needed branch repair after the last rebuild. Never ship a known failing combined version as a recovery technique. Do not repeatedly retry a mutation: after a failure or unexpected scope/content change, collect fresh evidence and revise the plan before another attempt.

## Verify and hand off

Confirm checks and relevant deployment tests pass, the expected PR merged, and the affected target-org components match the intended release. Check that held-back work did not ship. After custom promotion, inspect the next stage merge for remaining conflicts; matching trees alone does not establish shared history. Account for development-org drift before another commit can restore stale content.

Report the cause with evidence, actions actually taken, tests/content verified, and remaining history or sync work. Label unsupported explanations as hypotheses. Evidence IDs and paths in the references point to the companion MkDocs manual or the original lab repository; the bundled recovery guidance also works without either checkout.
