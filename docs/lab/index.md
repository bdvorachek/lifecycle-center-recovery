# How we tested

## Pipeline

| Lifecycle Center role | Branch | Org |
|---|---|---|
| Dev environment `dev` (Dev A) | work item branches | scratch org |
| Dev environment `dev2` (Dev B) | work item branches | scratch org |
| Stage: Staging | `staging` | scratch org |
| Stage: Production | `main` | Developer Edition org (also the Dev Hub) |

The test metadata is deliberately small: an Apex class `DiscountCalculator` with a few constants and
its test class. Two devs change the same constants to different values, so the conflicts are easy to follow.

Names in this guide are normalized: `dev` and `dev2` are development scratch orgs, `staging` is the
staging scratch org, and `release` is the Developer Edition org used for the Production stage. These are
documentation aliases, not instructions to rename connected environments. The Production stage in this lab
is not a business production org. Work item numbers, commit hashes, PR numbers, and event order are retained
so observations can be traced. Exact clock times and local-time-zone notes have been removed;
`[time omitted]` marks a removed timestamp where it supported an observation. Reported elapsed
durations are retained. Snapshot headings retain their before/after roles without absolute times. Environment names inside quoted UI messages are normalized too.

## Method

The experiments used Claude-assisted browser automation for Lifecycle Center UI actions, with CLI and Git
commands for setup, inspection, and the explicitly identified manual recovery steps.

- Changes in dev orgs are made with `sf project deploy start` (simulating a developer's edits), then committed
  and promoted **through the Lifecycle Center UI**.
- Before and after each step we take a [snapshot](../recipes/inspecting-state.md): branch heads, PRs,
  `WorkItem` and `DevopsRequestInfo` records, and deployed class bodies and timestamps.
- Predictions are simulated in a throwaway Git worktree first, then compared with what Lifecycle Center does.

## Experiments

- [Exp 01: Same-lines conflict](01-same-lines-conflict.md): bundling, manual resolution, combine.
- [Exp 02: Stage promotion after a combine](02-stage-promotion-after-combine.md): stuck Promote Stage and recovery.
- [Exp 03: Branch protection gate](03-e5-branch-protection-gate.md): does a required GitHub check stop a promotion?
- [Exp 04: Staging provenance check](04-g1-staging-provenance-check.md): a CI check that blocks versions never in Staging, tested against an out-of-order custom promotion.
- [Exp 05: What triggers the combine dialog](05-b3c-combine-dialog-trigger.md): Prepare vs Promote, silent rebase resolution, a combine that matches Staging.
- [Exp 06: Fix a stuck stage with a Git merge](06-a3b-git-merge-recovery.md): the latent trap a clean combine leaves, and fixing it outside Lifecycle Center.
- [Exp 07: Never, Back Sync and redo](07-b8-never-and-redo.md): fixing a work item vs stage conflict without Git, and the Back Sync feature.
- [Exp 08: Stuck stage with the work item in Staging](08-c3-stuck-stage-promoted-wi.md): no Never once promoted; custom-promoting the stuck work item as the way out.
- [Exp 09: Fix C with two stuck work items](09-c3d-fix-c-two-stuck-wis.md): Continue fails cleanly, Combine gets you out.
- [Exp 10: Silent rollback](10-c3e-silent-regression.md): out-of-order custom promotions roll Production back with no warning.
- [Exp 11: Recover from the silent rollback](11-c3f-recover-silent-rollback.md): two throwaway work items + Combine; "All changes" deploys the whole branch.
- [Exp 12: Clear the split-history trap](12-c3b-heal-split-history.md): one ordinary work item through Promote Stage repairs the history.
- [Exp 13: Two work items that combine into a test failure](13-e1-combined-test-failure.md): caught only if tests run; fixed forward.
- [Exp 14: Fix a broken combine without Promote Stage](14-e6-fix-broken-combine.md): a combined work item can't be combined again; the Lifecycle Center-only way out ships the broken version first.
- [Exp 15: Git fix for a broken combine](15-e6a-git-fix-for-broken-combine.md): commit Staging's files onto the combined branch, promote with tests; Production never broken.
- [Exp 16: Revert pending work, then Promote Stage](16-e6b-revert-pending-then-promote-stage.md): Lifecycle Center-only exit that never breaks Production; costs a revert and a redo.
- [Exp 17: Revert a pending new component](17-e6c-revert-added-component.md): the deletion works, but Promote Stage needs "All changes in the Production stage branch".
- [Exp 18: All changes and deletions](18-e6d-all-changes-and-deletions.md): "All changes" never deploys deletions; the default option does.
- [Exp 19: Direct commit on staging](19-d1ab-direct-commit-on-staging.md): accepted silently; reaches `main` but no org unless a work item touches the file.
- [Exp 20: Commit on a prepared branch](20-d1c-commit-on-prepared-branch.md): promoted as-is when nothing is combined; the Git fix needs one commit then.
- [Exp 21: Custom promotion without overlap](21-c1-custom-promotion-independent.md): still splits the history; one Promote Stage repairs it.

These are chronological lab notes with normalized environment names. Early entries include hypotheses and
recovery advice superseded by later experiments; the other sections are the maintained guide.
