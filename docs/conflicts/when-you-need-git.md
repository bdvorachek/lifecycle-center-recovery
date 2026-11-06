# Recovery options: UI actions and Git repairs

Start with the symptom, then decide whether the repair changes a branch or can be completed with Lifecycle Center
UI actions. Reading a PR is diagnosis; merging or committing is a repair. AI assistance in an IDE can help perform
a Git repair, but doesn't change which branch or content must be corrected.

## Choose a route

| Situation | Start with | Git involvement |
|---|---|---|
| A work item conflicts with the first stage | [Resolve on its branch, or abandon and redo](work-item-conflict.md) | A merge preserves the work; the tested UI alternative requires redoing it |
| Stage promotion conflicts after custom promotion | [Reconcile stage history](stuck-after-combine.md) | Git repair preserves source-stage content directly; conditional UI alternatives exist |
| Tests fail in content already present in the source stage | [Forward-fix work item](test-failures.md#the-way-out) | No manual Git repair needed in the tested route |
| Only the combined result fails; some source-stage work must stay behind | [Repair the combined branch](test-failures.md#the-git-fix) | If held-back work cannot be reverted, the only tested recovery uses Git |
| Pipeline looks clean but the target has an older value | [Diagnose rollback](stuck-after-combine.md#silent-rollback-after-out-of-order-custom-promotions) | Compare branch and org content before choosing a recovery |
| Generic failure, missing files, or unexpected scope | [Inspect PRs and deployment state](../recipes/inspecting-state.md) | Read-only Git/GitHub diagnosis first |

## What “uses Git” means here

- **Git repair recommended:** tested UI alternatives exist, but require redoing work or extra promotions. The
  recommendation describes a recovery tradeoff, not a team access policy.
- **Only tested recovery uses Git:** the lab has no verified UI-only recovery that preserves the stated release
  scope. This is a limit of the evidence, not proof that another recovery is impossible.
- **GitHub to diagnose:** inspect the PR, checks, or history; the correction may still happen in Lifecycle Center.

Salesforce's [Agentforce-assisted flow](where-conflicts-show-up.md#about-resolve-using-agentforce) opens an IDE with
conflict context. Treat it as tooling for the same investigation and repair, much like using desktop VS Code with
an AI coding agent. The lab did not test that integration, and does not assume it repairs every scenario automatically.

## Confirm the repair

Verify both the next promotion and the underlying state: intended content, passing tests, merged PR, deployed
components, and—when history was the problem—a clean stage merge. A successful selective promotion can fix content
while leaving stage history unreconciled.

See the [detailed recovery comparison](recovery-matrix.md) for experiment citations and less common cases, or
[open questions](../lab/open-questions.md) for unverified alternatives.
