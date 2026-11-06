---
name: lifecycle-center-recovery
description: Provide read-only diagnosis and human-executed recovery recommendations for stuck Salesforce Lifecycle Center promotions with GitHub, including work item conflicts, stage conflicts, broken combines, failed tests, silent rollbacks, and branch/org drift. Use for Lifecycle Center pipeline recovery, not managed-package DevOps Center or generic CI failures.
---

# Lifecycle Center recovery

Recommend how a human can move intended changes through the intended pipeline boundary, preserve held-back work, and verify the deployed result. This skill distills an unofficial lab's October–November 2026 experiments; observations are evidence for that configuration, not guarantees for every org or metadata type.

## Advisory-only operating boundary

Inspect evidence and provide recommendations only. The agent must not change repository state or the contents or configuration of any Salesforce org. A human must perform every state-changing action.

- Do not edit repository files or Git configuration; fetch, pull, checkout, create worktrees or branches, merge, commit, push, reset, or delete; create or modify PRs, checks, workflows, repository settings, or permissions.
- Do not execute deployments, promotions, Prepare, Combine, Back Sync, work-item changes, metadata/data writes, org setup changes, or anonymous Apex. Do not trigger tests, validation deployments, workflow runs, or other jobs; read existing results instead.
- Use only read-only tools and commands against existing evidence. Even `git fetch` changes local refs, and metadata retrieval can overwrite local files: give those steps to the human instead of running them. If local refs may be stale, say so and request fresh evidence or inspect current remote state with read-only APIs.
- Commands and UI steps that change state may be included in recommendations, clearly labeled **Human action — do not execute**. All repair procedures in the references are for the human, not executable agent instructions.
- Do not offer an approval-and-execute mode for recovery under this skill. If asked to perform a repair, provide the human-run procedure and explain this advisory-only boundary.

## Establish the boundary

Inspect available repository instructions, PRs and logs before asking for missing context. Identify:

- Repository, Lifecycle Center hub org, source/target stage branches and org aliases, and dev environment.
- Work items, failing PR/request, exact error, and path: work item promotion, Promote Stage, Prepare, or Combine.
- Intended final content, relevant tests, and work that must stay behind.

Never infer an org's role from its alias. The lab used one intermediate stage and a Developer Edition release org. Map roles explicitly in larger pipelines; Back Sync recipes start at the first stage, not an arbitrary later stage. Do not import lab credentials, org IDs, aliases, or destructive-operation permissions.

## Diagnose before choosing a recovery

Use [diagnostics](references/diagnostics.md) to compare four independent layers: Git history/content, GitHub PR/check state, Lifecycle Center records, and deployed org content. Collect only relevant components and records. If access is missing, state the missing evidence and give targeted read-only checks; do not claim a diagnosis is confirmed.

Read the relevant case in [recovery routes](references/recovery.md). Distinguish a text conflict from a failing check, deployment/test failure, semantic regression, or branch/org drift. A stale banner, Closed work item, passing provenance check, or merged PR alone does not prove success.

## Recommend a scoped repair

Explain the evidence, intended final diff, affected orgs/branches, release scope, risks, and verification. Give the human the ordered commands or UI steps, with explicit targets and expected results. Respect review/protection rules; never recommend bypassing failing checks or tests to ship known broken content.

For conflict resolution, recommend a clean isolated checkout that preserves uncommitted work. Prefer a normal PR/merge over resets or force pushes. For stage-history repair, the human must preserve merge ancestry: a squash/rebase of the reconciliation PR defeats the repair. Identify the exact file versions to keep rather than blindly recommending ours/theirs.

Prepare and Combine rebuild branches from original work item commits. Recommend inspecting the final PR after each human-executed rebuild and applying any needed branch repair after the last rebuild. After a failure or unexpected scope/content change, reassess fresh evidence before recommending another attempt.

## Verify and hand off

After the human performs the repair, inspect existing results to confirm checks and relevant deployment tests passed, the expected PR merged, and the affected target-org components match the intended release. Check that held-back work did not ship. After custom promotion, inspect the next stage merge for remaining conflicts; matching trees alone does not establish shared history. Account for development-org drift before another commit can restore stale content.

Report the cause with evidence, recommended human actions, human-reported or independently observed outcomes, and remaining history or sync work. Distinguish recommended steps from completed steps; do not claim to have executed the recovery. Label unsupported explanations as hypotheses. Evidence IDs and paths in the references point to the companion MkDocs manual or the original lab repository; the bundled recovery guidance also works without either checkout.
