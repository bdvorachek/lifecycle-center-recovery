# Experiment 01: Two devs edit the same lines of `DiscountCalculator`

## Setup
| Role  | Org                    | Work item (create in Lifecycle Center) |
|-------|------------------------|----------------------------------------|
| Dev A | `dev` (scratch)     | WI "Make Gold easier and richer"       |
| Dev B | `dev2` (scratch) | WI "Tighten margins + loyalty bonus"   |

Pipeline: dev environments (`dev`, `dev2`) → Staging (`staging` branch, staging) → Production (`main` branch, **release**, a Developer Edition org).

Baseline `DiscountCalculator` + `DiscountCalculatorTest` (in `force-app/`) is deployed to **both** dev orgs
(dev and dev2, 2026-10-31) and passes its 3 tests. It is **not yet in git**. Step 0 puts it into the pipeline.

## Planned changes
| Line / item              | Base  | Dev A  | Dev B   | Expected merge     |
|--------------------------|-------|--------|---------|--------------------|
| `GOLD_THRESHOLD`         | 5000  | 4000   | –       | clean (A wins)     |
| `GOLD_RATE`              | 0.10  | 0.12   | 0.08    | **CONFLICT**       |
| `MAX_DISCOUNT`           | 2500  | 3000   | 2000    | **CONFLICT**       |
| `calculateLoyaltyDiscount` (new) | – | –   | added   | clean (B wins)     |
| Test: `getTier(5000→4000)` | 5000 | 4000  | –       | clean              |
| Test: cap assert         | 2500  | 3000   | 2000    | **CONFLICT**       |
| Test: `loyaltyBonus()` (new) | – | –      | added   | clean              |

A local `git merge-file` dry run confirmed this: 2 conflicts in the class, 1 in the test.

**Semantic trap:** the cap value in the class and the cap assertion in the test have to be resolved
*the same way*. If you take Dev A's class but Dev B's test (or the reverse), the merge is textually clean
but `discountAndCap` fails at promotion. Watch whether Lifecycle Center's validation/test run catches it.

## Steps
0. **Baseline.** In Lifecycle Center, create WI "Baseline DiscountCalculator" on `dev`, pull changes, commit both
   classes, and promote through Staging → Production. Afterwards run `git pull` locally.
   (dev2 already has the identical baseline, so Lifecycle Center should see no changes there. It was briefly deployed to release too, then removed before activation.)
1. **Dev A edits:** `experiments/01-same-lines-conflict/apply.sh dev-a` deploys to dev.
   In Lifecycle Center: WI A → pull changes → commit.
2. **Dev B edits:** `experiments/01-same-lines-conflict/apply.sh dev-b` deploys to dev2.
   In Lifecycle Center: WI B → pull changes → commit.
   (`force-app/` now holds Dev B's copy locally. The orgs and Lifecycle Center are the source of truth.)
3. Promote WI A to Staging. Should be clean.
4. Promote WI B to Staging. **Expect a conflict.** Record what Lifecycle Center shows, where it sends you to resolve
   (in-app UI vs. GitHub PR), and what ends up on `staging`.
5. Variants to try afterwards:
   - Promote A and B **together** in one bundle/promotion and see whether behavior differs.
   - Resolve with the "semantic trap" mismatch and see if tests catch it.
   - Promote A all the way to Production before B reaches Staging.

## Observations
- **Step 0 (2026-10-31):** Baseline promoted cleanly. Lifecycle Center created branch `WI-000001` (commit "Discount"),
  merged it into `staging` (`Merge branch 'WI-000001' into staging`), then merged `staging` into `main`
  (`Merge branch 'staging'`). Both promotions used **merge commits** (no fast-forward or squash), and a work item
  branch is named `WI-<number>`.
- Lifecycle Center commits files as retrieved from the org, and the org **strips the trailing newline** from `.cls` files.
  Local edits ending in `\n` show up as a 1-line diff against the committed version. Dev A/B files were normalized to match.
- **Steps 1–2 deployed (2026-10-31):** Dev A → dev (3/3 tests pass), Dev B → dev2 (4/4 tests pass).
  Committed as WI-000002 "Conflict Dev" (dev, commit `07fcd55`) and WI-000003 "Conflict Dev2" (dev2, `658b910`).
- **Work item branches are cut from the first stage branch** (`staging` @ `7c6b185`), not from `main`.
- **Under the hood, Lifecycle Center is DevOps Center plus GitHub PRs.** Each work item gets a PR into `staging`
  titled `[DevOps Center] Merge WI-xxxxxx to staging`. A stage promotion is a PR `staging → main` titled
  `Promotion: staging → main`. PRs #1–#2 were the baseline; #3 (WI-000002) and #4 (WI-000003) are open, and
  GitHub reports each one as MERGEABLE by itself.
- The UI showed **no conflict warning** on the approved work item cards, even though both change the same lines.
- **Promote both together → blocked before any merge** with a "resolve using Agentforce" prompt (needs an
  Agentforce Vibes org, which isn't set up). Afterwards: `staging` unchanged at `7c6b185`, staging classes unchanged
  (baseline timestamp), and both PRs still open. **The bundle failing left nothing to clean up.**
  So Lifecycle Center checks conflicts *between work items in a bundle* before it merges.

- **One at a time:** WI-000002 promoted cleanly (`af85dd5 Merge branch 'WI-000002' into staging`).

## Recovery notes
- **Resolved WI-000003 outside Lifecycle Center (2026-10-31):** checked out `WI-000003`, ran `git merge origin/staging`.
  Got 2 conflicts: one combined block in the class (`GOLD_RATE` + `MAX_DISCOUNT`, merged together because they're
  close) and one in the test (cap assertion). `GOLD_THRESHOLD` and the loyalty method/test merged cleanly.
- Resolved with `git merge-file --theirs` on the index stages. That favors staging only in conflict blocks and
  keeps the clean merges. Result = staging + loyalty method/test. Ran `sf project deploy validate` against staging
  (4/4 tests pass), then committed `b76c4c8` and pushed to `WI-000003`. PR #4 went MERGEABLE/CLEAN.
- **Leftover drift:** the dev2 org still has Dev B's original 0.08 / 2000, and the WI-000003 branch now says
  0.12 / 3000. Watch what Lifecycle Center does with that (on the work item, and on the next "pull changes" in dev2).

## Next: combine work items (from Lifecycle Center docs)
- The combine option shows up during a **custom promotion out of a stage** when other work items in that stage share
  metadata or dependencies. It doesn't show up when promoting Approved → first stage (that path gave the Agentforce prompt).
- Combine replays work items oldest to newest into the **newest** work item's branch, deletes the older branches, and
  promotes. It's **irreversible**. It isn't available if any of them was merged externally into the target branch.
- Setup on 2026-10-31: WI-000002 + WI-000003 both in Staging, both touch DiscountCalculator*. Branch heads saved as
  local tags `pre-combine/{WI-000002,WI-000003,staging,main}`.
- Plan: custom-promote **WI-000002 only** from Staging → expect a combine prompt → choose Combine.
- Gotcha to test later: WI-000003's branch already contains WI-000002 (from the manual conflict resolution), so
  promoting WI-000003 alone would quietly carry WI-000002's code to Production.

## Correction (2026-11-01, from the request log)
- "Prepare" = `REBASE` in DevopsRequestInfo. **Both** work items were prepared: WI-000002 at [time omitted] (DORI-10 → PR #6),
  then WI-000003 at [time omitted] (DORI-11 → PR #7). Combine = DORI-12 `REBASE_AND_COMBINE` at [time omitted] → PR #8.
  So the plan above ("custom-promote WI-000002 only") isn't what happened; both were in the custom promotion.
- The earlier conflict blocks **did** leave request records: DORI-6 `PROMOTE` ERROR "Promotion failed" at [time omitted] (bundle of
  both) and DORI-8 ERROR at [time omitted] (WI-000003 alone, conflicting with staging after WI-000002 merged at [time omitted]).
- WI-000003 was newest by number, commit time, staging arrival **and** prepare order, so "newest wins" can't tell which
  of these Lifecycle Center uses.

## Result: combine (2026-10-31)
- The "Resolve Shared Components" dialog listed WI-000003 + WI-000002 with shared `DiscountCalculator:ApexClass` and
  `DiscountCalculatorTest:ApexClass`. Options: "Combine work items into WI-000003 (latest versions of the shared
  components are used)" or "Continue with custom promotion". We chose Combine.
- **WI-000002 branch deleted.** WorkItem status: WI-000002 = `COMBINED`, WI-000003 = `PROMOTED`.
- **WI-000003 branch rewritten**, not merged: rebuilt from `main` (c90ae37) by replaying the original commits
  `8f1d811 conflict 1` then `4b30232 conflict dev 2` (both authored by `DevOps Center <noreply@salesforce.com>`).
  **The manual resolution commit b76c4c8 was discarded.**
- Conflicts were resolved **line by line, newest work item wins**: kept Dev A's clean GOLD_THRESHOLD=4000 and Dev B's
  loyalty method, but GOLD_RATE/MAX_DISCOUNT/cap assertion = **Dev B's 0.08 / 2000**.
- ⇒ **Staging (0.12/3000) and the combined branch headed for Production (0.08/2000) diverge.** Class and test agree,
  so tests can't catch it. This is drift that happens inside the pipeline itself, with nobody working outside it.
- PRs: #6 (WI-000002→main) and #7 (WI-000003→main) closed; #8 `WI-000003 → main` open (combined). The stale
  stage PR #5 `staging → main` is also still open. Merging it later would try to bring 0.12/3000 into main.

## A1 result: combined PR promoted (2026-11-01)
- PR #8 (`WI-000003 → main`) merged [time omitted] as `f19b10f Merge branch 'WI-000003'`. Deployed to the Dev Hub [time omitted].
  WorkItem statuses: WI-000003 = `CLOSED`, WI-000002 = `COMBINED`.
- **Production now has 0.08 / 2000** (+ GOLD_THRESHOLD 4000, + loyalty). **Staging still has 0.12 / 3000.** Drift confirmed.
- **PR #5 `staging → main` ("Promotion: staging → main", auto-created [time omitted] during the earlier promotion attempt) is still
  OPEN and now CONFLICTING/DIRTY** on DiscountCalculator.cls and DiscountCalculatorTest.cls. Lifecycle Center merged the
  work item PR but **never closed the stale stage PR it had opened itself**. That's case C from the simulation, which happened
  without any further action from us.
