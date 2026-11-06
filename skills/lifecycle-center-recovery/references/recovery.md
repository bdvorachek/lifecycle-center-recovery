# Recovery routes

Evidence IDs refer to `experiments/NN-*.md` in the lab and `lab/NN-*.md` in the MkDocs manual. The guide paths below are relative to that manual's content root. These are observed lab results unless identified as hypotheses. Adapt roles and validate behavior in the current pipeline; the lab did not test a four-environment topology.

## Work item conflicts with the first stage

**Evidence:** Exp 01, 05, 07; `conflicts/work-item-conflict.md`.

Merge the first-stage branch into the work item branch in a clean checkout. Resolve the actual conflicting files, keeping code and tests consistent; validate the intended components with relevant tests. Push the resolution to the existing work item PR and promote through Lifecycle Center. Refresh the development org after promotion so its next commit cannot restore stale content. A later Prepare/Combine may discard the manual resolution.

Lifecycle Center-only alternative: preserve the change, set an eligible unpromoted work item to Never, Back Sync its dev environment, redo the change, and create a new work item. Never closes the PR and deletes its branch and cannot be undone. Back Sync can overwrite the developer's change and is blocked by open work items; commit only the intended redone files afterward. Promoted work items no longer offer Never. Do not choose this route without authorization for those consequences.

## Stage promotion conflicts after custom promotion or Combine

**Evidence:** Exp 02, 06, 08–12; `conflicts/stuck-after-combine.md`.

When the source-stage version is the intended release, reconcile history: create a repair branch from the source stage, merge the target into it, and resolve to the agreed content. If preserving the entire source tree, verify the diff against the original source tip is empty. Merge the repair PR back into the source stage **with a merge commit**, preserving target ancestry. Check the stage PR is mergeable, then Promote Stage with tests only when the entire source-stage scope is authorized to ship. Content changes during reconciliation require bringing the source org into agreement and testing; a Git merge alone does not deploy it.

Alternatives:

- Custom-promote the stuck work items only if the prepared files reproduce the intended source content. Include overlapping stuck changes together and inspect Combine's final result. Promoting an older item after a newer one silently rolled the target back (Exp 10). Custom promotion may leave split history; complete an authorized, clean stage promotion or reconcile the branches afterward.
- Accept the target version through a new work item only if that version is desired. Verify the target org agrees with its branch, bring those components through the dev/first-stage path, test in the source stage, then Promote Stage. This sacrifices the previous source resolution.

If the source version came from a manual merge or branch-only commit, do not assume custom promotion reproduces it. Compare actual prepared content. A cached conflict banner can persist after the PR becomes mergeable.

## Tests fail or a combined result loses a resolution

**Evidence:** Exp 13–16, 20; `conflicts/test-failures.md`.

Locate the failure first:

- If the source stage already contains the bug, fix forward through a dev environment/new work item and promote with tests. Back Sync only from the applicable first stage; later-stage fixes may need to traverse earlier stages.
- If only the prepared/combined result is broken and the source is tested, Promote Stage preserves its content **only if all source work may ship**.
- If work must stay behind, repair the final prepared/combined branch using the intended source versions of affected files, then promote with tests. Prepare each selected item; if a check blocks Next, it may need a preliminary repair. Combine rebuilds again, so repeat the repair on the final combined branch after the last rebuild. Do not Prepare again afterward. Without Combine, one post-Prepare repair sufficed (Exp 20). Verify checks and the final diff immediately before promotion; then inspect history for subsequent stage conflicts.

Do not combine a fix-up work item into an already combined item: this failed with `WORKITEM_UPDATE_FAILED` and dropped absorbed code during the rebuild (Exp 14). Do not use Continue with custom promotion to bypass the test-options screen and ship known broken code.

Lifecycle Center-only alternative when *all* held-back work can be reverted: restore target versions through revert work items, test/promote them to the source, Promote Stage with tests, then redo the held-back work as new items. This interrupts testing and makes original items Closed even though their changes did not ship. If any held-back work cannot be reverted, the only tested scope-preserving recovery uses Git.

## Deletions and full-branch deployment

**Evidence:** Exp 17–19; `conflicts/test-failures.md`, `how-it-works/git-model.md`.

A revert deleting a newly added component can make the default promotion fail with `destructiveChanges.xml: No ApexClass named...` because the target never had it. The lab recovered with “All changes in the target stage branch,” with tests covering all Apex in that branch. This is a full-branch redeploy, so review its scope first.

That option did **not** deploy deletions. Real deletions need the default mode; separate them from a revert deletion of a component the target never had. Validate other metadata types rather than generalizing the Apex result.

Branch-only changes are another drift source: default Promote Stage can merge them into Git without deploying them unless a promoted work item touches the same file. Full-branch deployment or a suitable work item can reconcile scoped content, but verify both source and target orgs separately. Do not treat a full-branch deploy as an org reset.

## Apparently clean pipeline, wrong target content

**Evidence:** Exp 10–12, 19; `conflicts/stuck-after-combine.md`.

Compare affected org components with the intended source and final PR, not statuses alone. Check for out-of-order custom promotions, stale dev-org commits, or branch-only content. Historical provenance passing does not establish current content equality. Restore the intended content with a scoped tested promotion, accounting for default versus full-branch deployment, then repair history if needed. Matching branch trees without deployment evidence is incomplete recovery.

## Checks or opaque Next failures

**Evidence:** Exp 03, 04, 14; `guardrails/branch-protection.md`.

Inspect the stage or prepared PR's actual checks, base/head and mergeability. Fix what the gate reports; do not disable protection to make the promotion pass. Recheck after changes, then retry the authorized operation. A stage preflight refusal may leave no request log. If failure repeats, collect fresh state rather than repeatedly rebuilding or promoting unchanged content.
