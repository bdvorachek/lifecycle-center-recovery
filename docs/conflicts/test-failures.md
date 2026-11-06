# Test failures from combined work items

**Observed ([Exp 13](../lab/13-e1-combined-test-failure.md)).**

## What you see

Two work items each pass their tests on their own, and Git merges them cleanly (they change different lines). The
**combination** fails a test. For example, one work item raises a rate and updates the tests it knows about, while
another adds a new test that assumes the old rate.

Git can't see this, and neither can Lifecycle Center's merge-conflict checks. Only running the tests on the combined
code finds it.

!!! info "Needs Git? No"
    The way out is a normal forward-fix work item. See [When you need Git](when-you-need-git.md).

## Confirm the problem

**Who:** someone who can read deployment errors and compare the source-stage and prepared PR content.
The combined-branch repair also needs commit and push access.

| Promotion test option | What happens |
|---|---|
| **No tests** (the lab default where offered) | The promotion **succeeds**. The broken combination is now in the stage, and nothing warns you. |
| **Run specified tests** / local / all | The deploy **fails**. The org isn't changed and the branch isn't merged (the tested failure left the PR unmerged). The work item stays where it was. |

!!! note "Lab org types matter"
    The final stage here is a Developer Edition org. The successful no-test promotions in this lab do not
    establish that Apex can be deployed without tests to a business production org. Salesforce’s
    [promotion options](https://help.salesforce.com/s/articleView?id=platform.devops_center_promotion_options.htm&language=en_US&type=5)
    describe production test requirements. Verify the options and enforced test level for your target org.

When the deploy fails:

- The card or stage turns red: *"We couldn't deploy your work items. Try again later, or ask your Salesforce admin for
  help."*
- **View Details** opens an Activity History record whose *Error Details* name the failing test and assertion, e.g.
  `DEPLOYMENT_FAILURE … Test: MyClassTest - System.AssertException: Assertion Failed: Expected: 150.00, Actual: 180.00`.
- The request log has an `ERROR` record with the same details.

## Choose a recovery

| Where does the failing content exist? | Route |
|---|---|
| Already in the source stage | Forward-fix through a new work item, then retry with tests |
| Only in the prepared/combined result, while the source is correct | Promote Stage if all source-stage work can move; otherwise repair the combined branch or use the revert route below |

Inspect the actual failing assertion and final PR before choosing. A clean Git merge says nothing about runtime
correctness. In a four-environment pipeline, a forward-fix may need to travel through Integration before reaching
Staging; the lab's first-stage Back Sync is not a sync from an arbitrary later stage.

## The way out

The work items that caused it may already be Promoted, so they can't be set to Never. Fix forward:

1. **Back Sync** a dev environment from the stage. It now has the broken combination, so the failure reproduces there.
2. Fix the code or the test in that dev org and run the tests.
3. New work item → commit only the fixed files → promote **with tests** to the stage, then **Promote Stage with tests**.

## When the broken version only exists in a combined work item

**Observed ([Exp 14](../lab/14-e6-fix-broken-combine.md)).** Here Staging is fine and only the custom promotion is broken. Two work items changed the same
SOQL line, the conflict was hand-resolved in Git (both fields), and Staging passed its tests. A custom promotion with
**Combine** rebuilt the work item from `main` and dropped the resolution, so one field was missing and a test failed:
`System.SObjectException: SObject row was retrieved via SOQL without querying the requested field`. Other work was
pending in Staging, so Promote Stage wasn't wanted.

Merging a fix into `staging` doesn't touch the combined work item: its branch is rebuilt from `main`, not from
`staging`. And the obvious Lifecycle Center fix fails:

- **Combining a fix-up ("carrier") work item into the combined one doesn't work.** Lifecycle Center refuses
  (`WORKITEM_UPDATE_FAILED`, "Combining work items failed") and its half-finished rebuild drops the absorbed work
  items' code. See [Combining](../how-it-works/combining.md#why-its-dangerous).

**Your options, in order of preference:**

1. **Promote Stage**, if the pending work can ship too. It merges `staging`, so Production gets Staging's tested
   version. No Git needed.
2. **Git: fix the combined branch, then promote with tests** (**Observed**, [Exp 15](../lab/15-e6a-git-fix-for-broken-combine.md)). Production never sees the broken
   version, and it works with a provenance check on. See [the Git fix](#the-git-fix) below.
3. **Take the pending work out of Staging, then Promote Stage** (**Observed**, [Exp 16](../lab/16-e6b-revert-pending-then-promote-stage.md)). No Git, Production never sees
   the broken version or the pending work. Costs two extra work items. See [the revert route](#the-revert-route) below.

!!! warning "Revert everything you're holding back, or don't use Promote Stage"
    Promote Stage, in either "Changes to promote" mode, ships **everything** in Staging. "All changes in the … stage
    branch" deploys the whole branch, so it's even broader. The revert route only works if **every** held-back work
    item is reverted first. If any held-back work can't be reverted (someone is still testing it in Staging, or it's
    too big to redo), Promote Stage is out. The only Lifecycle Center option left is a custom promotion, which rebuilds
    the broken version. That case is **Only tested recovery uses Git**: use [the Git fix](#the-git-fix). (*Hypothesis:* a deletion
    revert left in Staging also makes the next default Promote Stage fail, so ship a deletion revert together with
    everything else.)

**Which one to pick:**

| Held-back work in Staging | Verdict | Use |
|---|---|---|
| None, or it can ship | No Git needed | Promote Stage |
| Can all be reverted | **Git recommended** | The Git fix is two commits and leaves Staging alone. The revert route costs a revert + redo per held-back item, interrupts testing in Staging, and for a new component adds a full-branch redeploy ([Exp 17](../lab/17-e6c-revert-added-component.md)). |
| Some of it can't be reverted | **Only tested recovery uses Git** | The Git fix |

### The Git fix

**Observed ([Exp 15](../lab/15-e6a-git-fix-for-broken-combine.md)).** Every Lifecycle Center rebuild (Prepare, Combine) replays only the work items' **original**
commits, so a fix has to go in **after the last rebuild**:

1. Custom promotion → **Prepare** each work item. If a prepared PR is blocked (e.g. by the provenance check), commit
   Staging's version of the affected files onto that branch so you can get past **Next**:
   ```bash
   git fetch
   git switch -C fix origin/WI-xxxxxx
   git checkout origin/staging -- <affected files>
   git commit -m "Match Staging" && git push origin HEAD:WI-xxxxxx
   ```
2. Select the work items → Next → **Combine**. Combine throws that commit away and rebuilds the broken version again.
3. Repeat the same commit on the **combined** work item's branch. Wait for the PR's checks to pass.
4. Promote the combined work item **with tests**. Lifecycle Center merges the branch as you left it, fix included.

Don't click Prepare again after step 3: it would rebuild the branch and drop your fix.

- **No Combine, one commit (Observed, [Exp 20](../lab/20-d1c-commit-on-prepared-branch.md)).** If the custom promotion doesn't Combine (no other selected or
  staged work item shares the files, so no dialog appears), the commit from step 1 is enough: Lifecycle Center
  promotes the prepared branch as you left it, with Promotion Options (tests) offered as normal.
- **Afterwards, repair the history (Observed, [Exp 20](../lab/20-d1c-commit-on-prepared-branch.md)).** If the fix leaves conflicting edits in `main` and `staging`,
  the next Promote Stage can be blocked. Different file content alone does not prove a conflict. Follow up with Reconcile stage branches (merge `main` into `staging`) or a work item
  that makes Staging match, then one Promote Stage. See [Stuck stage](stuck-after-combine.md).

### The revert route

**Observed ([Exp 16](../lab/16-e6b-revert-pending-then-promote-stage.md), [Exp 17](../lab/17-e6c-revert-added-component.md)).** Lifecycle Center only. Promote Stage merges `staging`, so any hand resolution survives; the
only problem was the pending work item, so take it out first.

1. **Back Sync** a dev environment. Put **Production's version** of every file the pending work item changed into
   that dev org (from the Production org, or the work item's PR diff). Change Management shows it as an ordinary
   Modify.
2. New work item (the **revert**) → commit those files → promote to Staging **with tests**. Staging now differs from
   Production only by the work you want to ship.
3. **Promote Stage** with tests.
4. Redo the pending work as a **new** work item (Back Sync, re-apply the change, commit, promote to Staging).

Things to know:

- The reverted work item ends up **Closed**, as if it shipped. Its change didn't. Note that on the work item.
- Check the stage merge is clean first (no leftover split history from an earlier combine or custom promotion). If
  Promote Stage is blocked, fix that first: see [Stuck stage](stuck-after-combine.md).
- **If the pending work item added a component** (Observed, [Exp 17](../lab/17-e6c-revert-added-component.md)): delete it in the dev org; Change Management lists
  it as **Delete** and Lifecycle Center deletes it from the Staging org. But the default Promote Stage then **fails**
  (*"destructiveChanges.xml: No ApexClass named: … found"*): it sends the revert's deletion to Production, which never
  had the component. Nothing deploys; retry Promote Stage with **"All changes in the Production stage branch"**. That
  deploys the branch contents with no deletions, so name tests covering **every** Apex class in the branch (or Run
  local tests). It's a full redeploy of the branch.
- **"All changes in the … stage branch" never deploys deletions** (Observed, [Exp 18](../lab/18-e6d-all-changes-and-deletions.md)). A real deletion that should
  reach Production needs the default option. So a revert by deletion and a real deletion can't ship in the same
  Promote Stage: ship one, then the other.

!!! danger "Historical result: shipping a failing version is not a recovery recipe"
    In [Exp 14](../lab/14-e6-fix-broken-combine.md), choosing **Continue with custom promotion** bypassed the test-options screen and deployed a
    version whose tests failed in the lab release org. A later carrier work item repaired it. This left the
    release org broken in between and was blocked by the provenance guardrail when enabled. Use the tested
    Git fix or revert route above. The [notebook](../lab/14-e6-fix-broken-combine.md) retains the full sequence
    as evidence of the failure mode.

!!! warning "Needs Git? Only tested route when held-back work cannot be reverted"
    Lifecycle Center only: revert **all** the held-back work, Promote Stage, redo it ([Exp 16](../lab/16-e6b-revert-pending-then-promote-stage.md), 17). Two extra work items
    per held-back item, but Production never sees a broken version. If any held-back work can't be reverted, the lab has no verified
    UI-only recovery preserving that scope: **Only tested recovery uses Git**. With Git: two small commits ([Exp 15](../lab/15-e6a-git-fix-for-broken-combine.md)). Shipping the broken version and
    fixing forward ([Exp 14](../lab/14-e6-fix-broken-combine.md)) isn't an acceptable way out. Possible prevention (**Hypothesis B2**, not yet tested): put the resolution into the newer work item’s
    own commit from its dev org. Do not treat this as a verified recovery recipe.

## Verify success

- Rerun the previously failing test against the final content, with the applicable deployment test level.
- Confirm the final prepared/combined PR still contains the fix after any rebuild.
- Confirm the target org received the intended components and held-back changes did not ship.
- Inspect the next stage merge for remaining history conflicts after a custom promotion.
- If using the revert route, track the replacement work item separately: Closed status on the original does not
  mean its reverted change reached the target.

## Practical implications

- **Don't rely on the default "No tests".** Choose *Run specified tests* (or local tests) when promoting, at least
  into the last stage before Production. Promote Stage also offers **Run validate-only deploy**, a dry run.
- Assigning a **test plan** to a stage may make this automatic. *(Hypothesis, not tested; the pipeline shows "No
  test plan assigned".)*
