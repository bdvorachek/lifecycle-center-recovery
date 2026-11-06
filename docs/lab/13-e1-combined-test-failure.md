# Experiment 13: Two work items that combine into a test failure (E1)

## Question
Two work items each pass their tests on their own, and Git merges them cleanly, but the combination fails a test (a
semantic conflict). Where does Lifecycle Center catch it, if at all? Does it merge before or after the failing deploy
(is the branch left out of step with the org)? What's the way out, and does it need Git?

(E3 rollback dropped 2026-11-04: a rollback is just a new work item that reverts, promoted normally. E4 dropped too.)

## Design
Both work items start from the same Staging version (`b640771`, SILVER_RATE 0.05):
- **WI-1** (dev) "raise Silver rate": class SILVER_RATE 0.05 → **0.06**; test assertions updated to match
  (100 → 120, 1900 → 1880, 160 → 180, 200 → 220). Passes alone (validate on staging: 4/4).
- **WI-2** (dev2) "add Silver test": new test method `silverLargeOrder` asserting `calculateDiscount(3000) == 150`
  (Silver at 0.05). Test file only. Passes alone (5/5).
- Git merge of the two: **clean** (different lines). Combined validate: **FAILED**, `silverLargeOrder` expected 150.00,
  actual 180.00.

Steps: commit both before promoting either. Promote WI-1 to Staging with **Run specified tests
(DiscountCalculatorTest)**, then WI-2 the same way. Observe the failure. Variant if useful: promote with the default
**No tests** to see whether the broken combination reaches Staging silently.

## Before snapshot
- `main` = `7d8b6e9`, `staging` = `b640771`, merge-base = staging tip. No open PRs. SILVER_RATE 0.05 everywhere.

## Steps / Actual
Lifecycle Center UI steps were automated in Chrome.

1. CLI deploys (the developers' edits): WI-1 package → dev (tests 4/4), WI-2 package → dev2 (5/5).
2. **WI-1** = WI-000026 "e1 WI-1 raise Silver rate 0.06" (dev): DiscountCalculator + DiscountCalculatorTest, commit
   `be7545f`. **WI-2** = WI-000027 "e1 WI-2 add Silver test" (dev2, Show All Changes): DiscountCalculatorTest only,
   commit `dd96bf9`. Both parents `b640771`. `git merge-tree` WI-1 + WI-2: **clean**. PRs #54 / #53 MERGEABLE.
   (With two files selected the commit dialog is taller; the comment field moves.)
3. **Promote WI-1** to Staging, **Run specified tests: DiscountCalculatorTest**: DORI-93 SUCCESS. staging
   DeployRequest `RunTestsEnabled=true`, 4 tests, 0 errors. `staging` = `ec664d8`.
4. **Promote WI-2** the same way: "Initiating deployment" → DORI-94 **ERROR** "Promotion failed",
   `ErrorDetails` = `{"errorType":"DEPLOYMENT_FAILURE","errorMessage":"Test: DiscountCalculatorTest - System.AssertException:
   Assertion Failed: Expected: 150.00, Actual: 180.00"}`. staging DeployRequest **Failed** (5 tests, 1 error), org
   **unchanged** (no silverLargeOrder). **No merge**: `staging` still `ec664d8`, PR #53 OPEN/MERGEABLE. WI-2 stays
   READY_TO_PROMOTE.
   UI: Approved column "1 work item requires attention"; red card *"We couldn't deploy your work items. Try again later,
   or ask your Salesforce admin for help. View Details"* + Resolve Using Agentforce. **View Details** opens an Activity
   History record (DOAL-000000421, type "Promotion Completed", status Error) whose **Error Details show the failing test
   and assertion**.
   → Deploy-then-merge keeps branch and org consistent on a test failure: nothing half-applied.
5. **Variant: promote WI-2 again with the default "No tests"**: DORI-95 SUCCESS, staging DeployRequest
   `RunTestsEnabled=false`, 0 tests. `staging` = `29273eb`. Both WIs PROMOTED. Running DiscountCalculatorTest in staging
   afterwards: `silverLargeOrder` **fails** (150 vs 180), pass rate 80%. **The broken combination reached Staging
   silently.** The pipeline view showed nothing.
6. **Promote Stage with Run specified tests**: Promote Stage's options include "Promote Now / Run validate-only deploy".
   DORI-96 **ERROR**, `DEPLOYMENT_FAILURE`, same assertion. release DeployRequest Failed (5 tests, 1 error), release
   unchanged, `main` unchanged, stage PR #55 opened. Staging column then shows the red "We couldn't deploy your work
   items… View Details" banner.
7. **Way out (Lifecycle Center only, forward fix)**: WI-1 and WI-2 are PROMOTED (no Never). **Back Sync dev2**
   (DORI-97 `BACK_SYNC` SUCCESS; offered the dev-origin WIs incl. WI-000026) → dev2 now has the broken combination and
   reproduces the failure. Fix the test (150 → 180), tests 5/5 in dev2. **WI-000028** "e1 fix silverLargeOrder expects
   180" (dev2, Show All Changes), commit `963c03e` (one line). Promote to Staging with tests: DORI-99 SUCCESS (5/0),
   `staging` = `5fa6490`. **Promote Stage with tests**: DORI-100 SUCCESS (5 tests, 0 errors), `main` = `e41fbae`.
   WI-000026/27/28 CLOSED.

## After snapshot
- `main` = `e41fbae`, `staging` = `5fa6490`, same content, merge-base = staging tip. No open PRs.
- SILVER_RATE 0.06 + silverLargeOrder (180) in staging, release, dev2. dev has WI-1's version (no new test).

## Findings
1. **A semantic conflict passes Git and the merge-conflict checks.** Two work items that each pass alone, merged cleanly,
   produced a failing test.
2. **With tests on, Lifecycle Center catches it cleanly at deploy time**: `ERROR` request with `DEPLOYMENT_FAILURE`
   naming the test and assertion; the org isn't changed and the branch isn't merged (deploy-then-merge). The UI shows a
   red banner, and **View Details** (Activity History) shows the exact assertion.
3. **With the default "No tests", the combination reaches Staging silently.** Nothing warns you; only a later
   promotion with tests (or running tests yourself) finds it.
4. **The way out is Lifecycle Center only**: Back Sync a dev org (which then reproduces the failure), fix, new work item,
   promote with tests through both stages. No Git needed, and no history problems (no custom promotion was used).
5. Promote Stage's options include **Run validate-only deploy** (a dry run with tests) and **Run specified tests**.
