# Stage conflict recovery

## What you see

- **Promote Stage** fails with *"Cannot initiate promotion due to merge conflicts."*
- The waiting work items may be unrelated to the conflicting files.
- The only option offered is **Resolve Using Agentforce**.
- In GitHub, the `Promotion: staging → main` PR is `CONFLICTING`, often an old PR that has been open for a while.
- The work items stuck in Staging **can't be set to Never**: once a work item is Promoted, its status menu is gone
  ([Exp 08](../lab/08-c3-stuck-stage-promoted-wi.md)). [Exp 07](../lab/07-b8-never-and-redo.md)'s Never → Back Sync → redo route isn't available here.

!!! warning "Needs Git? Recommended"
    Reconcile the stage branches when Git access is available: it keeps Staging’s tested version and repairs the history.
    Custom-promoting the source version is a Lifecycle Center-only alternative when the prepared branches reproduce the intended Staging content;
    follow it with a stage merge to repair history. Accepting the target version changes Staging to match Production. Finding the conflicting files needs GitHub either way. See
    [When you need Git](when-you-need-git.md).

## Confirm the problem

**Who:** someone who can inspect the stage PR; the Git route also needs merge and push access.
Confirm the PR's source and target branches and its conflicting files. The examples below use the lab's
`staging` → `main` boundary. For your pipeline, inspect Integration → Staging or Staging → Production separately.
The lab's dev-org/Back Sync alternatives start at the first stage; they are not verified shortcuts into a later stage.

```bash
git fetch
gh pr view <stage-PR> --json mergeable,mergeStateStatus
git diff --stat origin/main origin/staging
```

A content difference alone is not proof of a conflict. Look for `CONFLICTING` and inspect the affected files.
Before either stage-promotion route, confirm the entire source stage's scope can move to the target.

## Choose a recovery

| What must be preserved? | Use | Follow-up |
|---|---|---|
| Staging’s tested content and shared Git history | [Reconcile stage branches](#fix-b-merge-the-branches-in-git-outside-lifecycle-center) | Promote Stage with tests; verify the deployed components |
| Staging’s version, using Lifecycle Center only | [Custom-promote the source version](#fix-c-custom-promote-the-stuck-work-item-lifecycle-center-only), if the work items carry the full resolution | A successful Promote Stage once the merge is clean |
| Production’s current version is the version the team wants | [Accept the target version](#fix-a-a-work-item-that-makes-staging-match-production-lifecycle-center-only) | Test that version in Staging, then Promote Stage |

<span id="fix-b-merge-the-branches-in-git-outside-lifecycle-center"></span>

## Reconcile stage branches (Git)

**Verified in [Exp 06](../lab/06-a3b-git-merge-recovery.md).** Merge `main` into `staging` yourself and resolve the conflict in favor of the version you
want to ship (normally Staging's, since that's the one that was tested). Lifecycle Center accepts the result
without comment.

1. Merge `main` into a branch cut from `staging`, keeping Staging's lines:
   ```bash
   git fetch
   git switch -c reconcile-main origin/staging
   git merge origin/main            # conflicts on the combined files
   git checkout --ours -- <conflicting-files>   # keep Staging’s version
   git add <resolved-files>
   git commit --no-edit
   git diff origin/staging HEAD     # should be empty: Staging's content doesn't change
   git push -u origin reconcile-main
   ```
2. Open a PR `reconcile-main → staging` and merge it **with a merge commit**. Squashing or rebasing this PR
   would discard the ancestry this repair needs. Honor the branch’s normal review and protection rules.
3. Check that the stage PR is now `MERGEABLE`. The old conflict banner will still be
   [cached](where-conflicts-show-up.md#the-banner-is-cached) in the pipeline view.
4. Click **Promote Stage**. It runs normally and `main` ends up identical to `staging`.

**Observed ([Exp 06](../lab/06-a3b-git-merge-recovery.md)):**

- No "external merge" warning, error or prompt. The reconcile commit just rides along in the stage PR.
- The Staging org isn't redeployed (its content didn't change). Promote Stage deploys the waiting work items'
  components to Production as usual.
- A [staging provenance check](../guardrails/staging-provenance.md) passes, because Production gets exactly Staging's tree.

!!! tip "Reconcile stage branches vs Accept the target version"
    Reconciling the stage branches keeps **Staging's tested version** and needs no dev org or extra work item. Accepting the target version uses Production's
    (untested) version. Both repair this divergence: once the stage merge succeeds, `main` contains staging's
    tip and the branches share history again ([Exp 02](../lab/02-stage-promotion-after-combine.md), [Exp 06](../lab/06-a3b-git-merge-recovery.md)). If you pick `--theirs` in step 1 instead, Staging's
    content changes and the Staging org no longer matches its branch until something redeploys it (**Hypothesis**,
    not tested).

<span id="fix-c-custom-promote-the-stuck-work-item-lifecycle-center-only"></span>

## Custom-promote the source version (Lifecycle Center only)

**Verified in [Exp 08](../lab/08-c3-stuck-stage-promoted-wi.md).** Instead of Promote Stage, promote the stuck work items themselves with a custom promotion.
Prepare rebuilds each one from its **own commits** on top of `main`, without merging the stage branch, so the stage
conflict never comes up.

1. Staging column menu → **Select Work Items to Promote** → **Prepare** each stuck work item.
   Wait for **Created** in Lifecycle Center; the PR can exist while the UI still shows **Preparing…**
   ([Exp 08](../lab/08-c3-stuck-stage-promoted-wi.md)).
2. Fetch again after Prepare. Check the prepared `WI → main` PR in GitHub: the affected files should match
   Staging’s intended version. Compare them with `git diff origin/staging origin/<WI-branch> -- <affected-files>`.
   A full `force-app` diff may also show unrelated work intentionally held back. The
   [staging provenance check](../guardrails/staging-provenance.md) is weaker: it accepts historical Staging versions,
   so a passing check does **not** establish a match with the current Staging version.
3. Select them → Next → Promote.
4. **Several stuck work items that touch the same lines:** choose **Combine** in the "Resolve Shared Components"
   dialog. "Continue with custom promotion" fails, because each prepared branch was built on `main` separately and
   they conflict with each other. **Observed ([Exp 09](../lab/09-c3d-fix-c-two-stuck-wis.md)):** the failure is clean (nothing deployed, `ERROR` request with
   `MERGE_CONFLICT` in its details), but the UI shows no message, just "N work items are ready for custom promotion"
   again. Combine replayed both work items in order and matched Staging exactly.

!!! danger "Promote all the stuck work items together"
    **Observed ([Exp 10](../lab/10-c3e-silent-regression.md)):** we custom-promoted the newer of two same-line work items (0.19), then the older one on its
    own. The older one's Prepare silently kept its own line, and **Production went back to 0.18** while Staging kept
    0.19. There was no dialog or warning, the provenance check passed (0.18 had existed in Staging once), and afterwards
    the pipeline looked completely clean. See [Silent rollback](#silent-rollback-after-out-of-order-custom-promotions).

!!! danger "Custom-promote the source version leaves a trap"
    Production now matches Staging, but the histories are still split and the stage PR stays open. **The next work
    item that changes those lines, or the lines next to them, can block Promote Stage again** (simulated, [Exp 08](../lab/08-c3-stuck-stage-promoted-wi.md)).
    Repair the history before that happens, either way:

    - **Lifecycle Center only (Observed, [Exp 12](../lab/12-c3b-heal-split-history.md)):** promote an ordinary work item that touches **other files** into
      Staging, then **Promote Stage**. Because `main` and `staging` now have the same content, the stage merge is
      clean, `main` ends up containing staging's tip, and the trap is gone. (Click Promote Stage even if the old
      conflict banner is still showing; it's cached.)
    - **Git:** merge `main` into `staging` (Reconcile stage branches, with nothing to resolve).

!!! warning "When Custom-promote the source version doesn't help (Hypothesis)"
    Custom-promote the source version only reproduces Staging if the stuck work items' **own commits** contain Staging's final version of every
    conflicting line. If Staging's version came from somewhere else (a hand-resolved merge commit, as in [Exp 01](../lab/01-same-lines-conflict.md), or a
    direct commit to `staging`), the prepared PR differs from Staging. A provenance check will block it (good), and
    you're left with Accept the target version (lose Staging's version) or Reconcile stage branches (Git).

<span id="fix-a-a-work-item-that-makes-staging-match-production-lifecycle-center-only"></span>

## Accept the target version (Lifecycle Center only)

**Verified in [Exp 02](../lab/02-stage-promotion-after-combine.md).**

Git treats an **identical change on both sides** as no conflict. So a work item that sets Staging's lines to
exactly what Production has makes the stage merge clean.

1. Confirm the release org agrees with `main` for the affected components. In a separate local Salesforce project,
   retrieve those components from the release org, inspect the diff, and deploy them to the dev org. For example:
   ```bash
   sf project retrieve start -o <release-alias> -m ApexClass:MyClass -m ApexClass:MyClassTest
   sf project deploy start -o <dev-alias> -m ApexClass:MyClass -m ApexClass:MyClassTest \
     --test-level RunSpecifiedTests --tests MyClassTest
   ```
   If source tracking reports a conflict, compare the versions before choosing an overwrite.

2. In Lifecycle Center: new work item in that dev environment → **Pull changes** (only those files should appear)
   → commit → promote to Staging.
3. Check that GitHub now reports the stage PR as `MERGEABLE`. Expect the old conflict banner to still be
   showing (it's [cached](where-conflicts-show-up.md#the-banner-is-cached)).
4. Click **Promote Stage** again. The stale PR merges, and `git diff origin/main origin/staging` is empty.

!!! warning "This accepts Production's version"
    Production keeps the combine’s version. Run the relevant tests after accepting it in Staging; this does not
    restore the previously tested resolution. If that resolution was the right one, ship it **afterwards** as a normal work item. The history is clean by then, so it promotes normally.

    A work item that sets any *other* value (including keeping Staging's) **does not** fix the problem.
    Simulated in [Exp 02](../lab/02-stage-promotion-after-combine.md): still conflicting.

## Verify success

- The stage PR is mergeable, then merges when Promote Stage completes. A stale UI banner can remain until retry.
- The intended source-stage content is preserved or the accepted target version is explicitly verified.
- Relevant tests pass and the affected target-org components match the intended result.
- After custom promotion, complete a stage merge when the release scope permits, or reconcile the branches in Git.
  A successful custom promotion alone does not repair the shared history.
- If a Git-only change introduced content no promoted work item carries, check deployment scope; an updated branch
  is not proof that the org received it.

## Resync an org with its branch

**Observed ([Exp 11](../lab/11-c3f-recover-silent-rollback.md)):** the Promotion Options choice **"All changes in the <stage> stage branch"** deploys **every
component in the branch being deployed**, not just the promoted work items’ components (4 classes vs 1 in our lab). It's the
Lifecycle Center-only way to bring an org back in line with its branch, for example after drift or after a Git-only
fix. This does **not** remove components absent from the branch ([Exp 18](../lab/18-e6d-all-changes-and-deletions.md)), so it cannot repair deletion drift
on its own. In a real repo that’s a full deploy, so expect the matching test run and deploy time.

## Silent rollback after out-of-order custom promotions

**Symptoms:** no work items in Staging, Promote Stage disabled, no warnings, but `git diff origin/main origin/staging`
isn't empty and Production has an older value than Staging. **Observed ([Exp 10](../lab/10-c3e-silent-regression.md)).**

You can't simply re-commit Staging's value (there's no diff to commit from a synced dev org). Lifecycle Center-only
ways back:

- Ship a **new** value: a work item that changes the line again, then Custom-promote the source version. (Simulated.)
- **Restore the exact value (Observed, [Exp 11](../lab/11-c3f-recover-silent-rollback.md)):** two throwaway work items, Staging's value → anything → Staging's
  value, both promoted to Staging. Then custom promotion → Prepare both → **Combine**. Production gets exactly
  Staging's version, and the provenance check passes.

Promote Stage stays blocked the whole time, so all of this goes through custom promotion. The split history (and the
trap) is still there afterwards.

## Prevention

- **A combine can look clean and still leave a trap.** **Observed ([Exp 05](../lab/05-b3c-combine-dialog-trigger.md) → [Exp 06](../lab/06-a3b-git-merge-recovery.md)):** a combine with no manual
  resolution left `main` and `staging` with identical content, so the stage PR was mergeable. But their histories had
  split. The next ordinary work item that changed one of the combined lines, **or a line next to one**, blocked
  Promote Stage. Check with `git merge-base origin/main origin/staging`: an older merge-base is a reason to inspect the history, not proof of a conflict.
  Compare the affected files and simulate the merge as described in [Inspecting pipeline state](../recipes/inspecting-state.md).
- **Any custom promotion leaves the same trap, even with no overlap.** **Observed ([Exp 21](../lab/21-c1-custom-promotion-independent.md)):** custom-promoting one of
  two work items on different files left the merge-base unchanged; a simulated later edit next to the promoted line
  conflicted. Using only custom promotion keeps adding trap lines.
- After any combine or custom promotion, get **one successful Promote Stage** through (any work item on other files)
  before anyone edits those lines again, or merge `main` back into `staging` in Git. Either moves the merge-base forward.
  (**Observed**: [Exp 12](../lab/12-c3b-heal-split-history.md) and [Exp 21](../lab/21-c1-custom-promotion-independent.md) for Promote Stage, [Exp 06](../lab/06-a3b-git-merge-recovery.md) for Git.)
- **Practical implication:** a whole-stage promotion retains source-stage history when the entire release scope
  can move forward. If work must stay behind, inspect the prepared and combined content instead.
- If a combine happens, run `git diff origin/staging origin/main` straight after it reaches Production. A
  non-empty diff on the combined files warrants a merge simulation; conflicting edits can block Promote Stage. Fix it then (Reconcile stage branches, or Accept the target version).
  An empty diff isn't enough (see the first point).

??? info "Supporting evidence: why stage histories conflict"

    ## Why it happens

    A [combine](../how-it-works/combining.md) rebuilt a work item from `main` and sent it to Production, but
    `staging` kept the original version. Now both branches have changed the same lines **in different ways** since
    they last agreed:

    ```text
    merge-base (0.10 / 2500)
    ├── staging: 0.12 / 3000   (hand-resolved, tested in Staging)
    └── main:    0.08 / 2000   (combine result, newest-wins)
    ```

    Any `staging → main` merge hits those lines, whatever new work is in Staging. Every Promote Stage is blocked
    until the conflicting branch histories are reconciled.

    **It doesn't take a combine. Observed ([Exp 08](../lab/08-c3-stuck-stage-promoted-wi.md)):** two work items changed the same line one after the other (A then
    B) and both reached Staging. A [custom promotion](../how-it-works/combining.md) of **only A** rebuilt A's commit on
    `main`, so Production got A's value and Staging kept B's. Lifecycle Center did warn first, with the "Resolve Shared
    Components" dialog, but "Continue with custom promotion" went straight through. The next Promote Stage was blocked,
    with B stuck in Staging.
