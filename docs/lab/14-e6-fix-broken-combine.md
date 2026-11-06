# Experiment 14: Fix a combined work item that fails its tests, without Promote Stage (E6)

## Question
Two work items are in Staging and Staging is fine, but combining them for a custom promotion produces a build that
fails its tests (the combine drops a hand-resolved line, here a field in a SOQL query). Other work is pending in Staging,
so **Promote Stage isn't an option**. How do you get a working version of the two work items to Production?

Sub-questions:
1. Does a combined promotion offer test options (Run specified tests)?
2. What state does a failed combined promotion leave (work items, branches, PRs)?
3. Can an already-combined work item be combined again with a new "carrier" work item?
4. Does the carrier's own line win, so Production gets Staging's full field list?

## Design
New class `AccountSummary` with one shared query, `[SELECT Id, Name FROM Account WHERE Id = :accountId]`.
- **Baseline WI** (dev2): AccountSummary + AccountSummaryTest. Promote to Staging and Production first.
- **WI-A** (dev): query adds `Industry`; new method `industry()` + test, in Dev A's section.
- **WI-B** (dev2): query adds `Phone`; new method `phone()` + test, in Dev B's section.
- A → Staging. B now conflicts with Staging on the query line → **hand-resolve in Git** (merge `staging` into `WI-B`,
  query = `Industry, Phone`, push), then B → Staging with tests (should pass).
- **WI-P** (pending, unrelated: LabPing) → Staging. Not to be promoted.
- Custom promotion: prepare A and B → Promote → **Combine** → promote the combined WI with Run specified tests
  (AccountSummaryTest). Expected: fails, `Account.Industry` not queried.
- **Carrier WI-F** (dev, after Back Sync): reorder the query to `Phone, Industry` (a real change on the same line that
  keeps both fields) → Staging with tests. Custom promotion: prepare F (+ the combined WI) → Combine → promote with tests.
  Expected: passes, Production = Staging's fields; WI-P stays in Staging.

Local simulation (2026-11-04): replaying A then B onto `main` with newest-wins keeps `SELECT Id, Name, Phone` and A's
`industry()` method, so A's test should fail. Staging has `Industry, Phone`.

## Before snapshot
- `main` = `e41fbae`, `staging` = `5fa6490`, same content, shared history, no open PRs. WI-000026/27/28 CLOSED.
- No AccountSummary anywhere. dev still has its stale DiscountCalculator (not used here).

## Steps / Actual
Lifecycle Center UI steps were automated in Chrome.

### Setup
1. **Baseline** WI-000029 (dev2): AccountSummary + Test, commit `df90189` → Staging with Run specified tests
   (DORI-102) → Promote Stage with Run specified tests (DORI-103), `main` = `f12555e`.
   (The first Promote Stage click hit "Can't validate promotion … branch protection": the provenance check on stage PR
   #58 was stuck *pending* although its run had finished. GitHub glitch; `gh run rerun` fixed it.)
2. **WI-A** = WI-000030 (dev): commit `4311515` (query `+ Industry`, `industry()` + test). **WI-B** = WI-000031 (dev2,
   Show All Changes): commit `1966798` (query `+ Phone`, `phone()` + test). Both parents = staging `3599bb6`.
   `git merge-tree`: conflict in AccountSummary.cls only (the query line); the test file merges cleanly.
3. A → Staging with tests (DORI-106), `staging` = `ac3de8e`. B's PR #60 now conflicts.
4. **Hand resolution in Git** (outside Lifecycle Center): merged `staging` into `WI-000031`, query =
   `Id, Name, Industry, Phone`, commit `b1c367e`, pushed. Validate-only on staging: 4/4 tests. PR #60 MERGEABLE.
5. B → Staging with tests (DORI-107), `staging` = `2dd2a27`. Staging branch **and** staging org: `Industry, Phone`.
6. **WI-P** = WI-000032 (dev): LabPing comment, commit `84af4da` → Staging with Run specified tests (LabPingTest).
   DORI-109, `staging` = `c897b6a`. Staging now holds A, B (hand-resolved) and P.

### The custom promotion (A + B only)
7. Staging column → Select Work Items to Promote → **Prepare A** (DORI-110 `REBASE`, PR #63, `69c170e` on `main`:
   `Industry`) → **Prepare B** (DORI-111 `REBASE`, PR #64, `ee8854b` on `main`: **`Phone` only**). The hand-resolution
   merge commit `b1c367e` is gone from B': Prepare replays only B's own commit. (Only one Prepare runs at a time; the
   other links are disabled until it finishes, ~20 s each here.)
8. Select A + B → Next → "Validating promotion…" → **"Can't validate promotion: We couldn't merge the changes because
   of branch protection rules"**. PR #64 fails the **staging provenance check** (G1): B's `Phone`-only AccountSummary
   never existed on `staging`. (PR #63 showed no check at all: same stuck-Actions glitch as step 1.)
   → With the provenance guardrail on, the broken version is blocked **before the combine dialog even appears**. The
   custom promotion of A + B can't proceed at all: B' alone is a version Staging never had.
9. User approved removing the requirement: `required_status_checks` deleted from `main`'s protection (backup kept).
   PR #63 → CLEAN, PR #64 → **UNSTABLE** (its failed check run is still attached, just not required).
10. Select A + B → Next again → toast **"Promotion Failed: We couldn't complete this task. Try again later, or ask your
    Salesforce admin for help."** No request record, no combine dialog. The page's `postValidatePromotion` call returned
    `{"errorType":"CHANGE_REQUEST_VALIDATION","errorDetails":[{"reviewReference":"64","reason":"UNKNOWN","workItem":"WI-000031"}]}`.
    → Lifecycle Center blocks a prepared PR whose GitHub merge state isn't CLEAN, even when the failing check is **not
    required**. A failing non-required check is enough to stop a custom promotion, and the UI says nothing about why.
11. The operator disabled the workflow and deleted the failed run for this isolated test.
    PR #64 → CLEAN.

### The combine and the failing promotion
12. Select A + B → Next → "Resolve Shared Components" (AccountSummary, AccountSummaryTest) → **Combine into WI-000031**
    (DORI-112 `REBASE_AND_COMBINE`, ~40 s). WI-000031 rebuilt from `main` as A (`ba2c445`) then B (`f3fa9bd`):
    query **`Id, Name, Phone`**, but A's `industry()` method and test are there. PR #65 (WI-000031 → main) CLEAN;
    #63/#64 closed. WI-000030 COMBINED. Exactly the local simulation.
13. Promote the combined WI → **Promotion Options are offered** (same as a normal custom promotion): Run specified tests
    = AccountSummaryTest. DORI-113 **ERROR** `DEPLOYMENT_FAILURE … Test: AccountSummaryTest - System.SObjectException:
    SObject row was retrieved via SOQL without querying the requested field: Account.Industry`. The pipeline showed a
    "Couldn't deploy work items" dialog with that text (View Details / Resolve using Agentforce).
    State afterwards: `main` unchanged (`f12555e`), release unchanged, WI-000031 still PROMOTED in Staging and
    still "ready for custom promotion", PR #65 still open. Same clean failure as Exp 13.

### The carrier
14. Back Sync `dev` from Staging (DORI-114): dev now has Staging's `Industry, Phone`.
15. **WI-F** = WI-000033 (dev): query reordered to `Id, Name, Phone, Industry` (deployed to dev, committed in
    Change Management, DORI-115, `69bf6ac`) → Staging with Run specified tests (DORI-116, `staging` = `a681b95`).
16. Prepare F (DORI-117, PR #67): F' on `main` = `Phone, Industry`, nothing else.
17. Select WI-000031 (combined) + F → Next → "Resolve Shared Components" → **Combine into WI-000033** → toast
    **"Combining work items failed. We couldn't combine the work items. Try again, promote the impacted work items
    together, or promote the entire stage."** DORI-118 `REBASE_AND_COMBINE` **ERROR**
    `WORKITEM_UPDATE_FAILED:workitem bpo update failed`.
    But the Git half had already run: WI-000033 was force-pushed as `main` + **B's own commit** + F, with **no A
    commit**, so no `industry()` method or test. PR #67 closed, PR #68 opened. In Lifecycle Center F showed "Creation
    Failed" with Prepare offered again; WI-000031 stayed PROMOTED.
18. Retried once (Prepare F again DORI-119, Combine again DORI-120): **identical failure**, same A-less branch.
    → **An already-combined work item can't be combined again.** The rebuild only knows the work item's *own*
    commit (B), not the commits it absorbed (A). If the record update had succeeded, the result would have passed
    AccountSummaryTest (A's test was gone too) and silently dropped A's feature.

### The way out that worked: ship the broken combine, then the carrier
19. Select WI-000031 only → Next → "Resolve Shared Components" (F shares AccountSummary) → **Continue with custom
    promotion**. This path went **straight to deployment, without the Promotion Options dialog**, so with no tests.
    DORI-121 SUCCESS, `main` = `fd24537` (`Phone` only + `industry()`), release the same. WI-000031 CLOSED.
    `sf apex run test -n AccountSummaryTest` on release: **75%, `industry` fails** (Account.Industry not queried).
20. Staging menu → Select Work Items to Promote → **Prepare F again** (DORI-122, PR #71): rebuilt on the new `main`,
    the diff is exactly the one query line `Phone` → `Phone, Industry`.
21. Promote F with Run specified tests (AccountSummaryTest): DORI-123 **SUCCESS**, `main` = `7961e94`, release =
    `Id, Name, Phone, Industry`. WI-000033 CLOSED. WI-P still in Staging.
22. Restored the guardrail: workflow re-enabled; branch protection PUT back from the backup (the PATCH on
    `required_status_checks` 404s once the check has been removed).

## After snapshot
- `main` = `7961e94`, `staging` = `a681b95`. `git diff origin/main origin/staging` = **LabPing.cls only** (WI-P,
  pending). AccountSummary identical.
- Merge-base still `3599bb6` (split history), but `git merge-tree` of the stage merge is **clean**, stage PR #61
  MERGEABLE: the AccountSummary lines now agree on both sides.
- Open PRs: #61 only. Work items: WI-000030 COMBINED, WI-000031/33 CLOSED, WI-000032 PROMOTED (in Staging).
- release, staging, dev and both branches: AccountSummary = `Id, Name, Phone, Industry` + both methods.
- `main` protection: `staging-provenance` required again, enforce_admins on.

## Findings
1. **A combined promotion offers the normal Promotion Options** (Run specified tests etc.) and a failing test fails it
   cleanly: nothing merged, nothing deployed, the combined work item stays in Staging ready to retry.
2. **A combined work item can't be combined again.** Combining it with a carrier fails with
   `WORKITEM_UPDATE_FAILED` (deterministic, twice). Worse, the Git half runs first and rebuilds the branch from the
   combined work item's **own original commit only**, dropping the work items it had absorbed. The "carrier + Combine"
   recipe does not work.
3. **What does work without Promote Stage: ship it, then fix forward.** Custom-promote the broken combined work item
   (it ships failing code to Production), then re-Prepare the carrier on the new `main` and promote it with tests. The
   carrier's own one-line change lands cleanly. Cost: **Production runs the broken version in between**, and the first
   step can't run tests (it would fail them).
4. **"Continue with custom promotion" skips the Promotion Options dialog**: no test choice, deploy starts immediately.
5. **A failing *non-required* check blocks custom promotion** (step 10): `CHANGE_REQUEST_VALIDATION`, reason
   `UNKNOWN`, generic "Promotion Failed" toast. Removing the requirement isn't enough; the failed run has to go.
6. **Prepare drops a hand resolution** (step 7) and **with the staging provenance check on, the broken combine is
   never built** (step 8): the custom promotion stops at Next. The only Lifecycle Center ways out are then Promote
   Stage (ships the pending work too) or the ship-then-fix sequence above (which the provenance check also blocks).
7. **Better options, if you have them:**
   - Promote Stage, if the pending work can go too (ships Staging's tested hand resolution).
   - Git: commit the fix to the combined work item's branch (or resolve in it before promoting).
   - Prevention: resolve conflicts **in the dev org inside the newer work item** (B2) so the combine keeps it, and never
     hand-resolve with a merge commit on a work item branch.
