# Experiment 15: Git fix for a combine that breaks the tests (E6a, applies D4)

## Question
Exp 14's situation: two work items (C, D) change the same SOQL line, D's conflict is hand-resolved in Git, both pass in
Staging, and an unrelated work item (WI-P) is pending in Staging and must not ship. Custom promotion with Combine
drops the hand resolution. Exp 14's only Lifecycle Center-only exit shipped a failing version to Production.

Can Git fix it without breaking Production?
1. With the staging provenance check **on**, where does the broken version first show up (D's Prepare, as in Exp 14)?
2. If we commit Staging's version of the files onto the **prepared** branch, does the check pass and does **Combine
   keep that commit**?
3. If the **combined** branch is broken and we commit the fix onto it, does Lifecycle Center promote the branch as we
   left it, or rebuild it?
4. End state: Production = Staging minus WI-P, never a broken version in Production?

## Design
Starting point: AccountSummary query `Id, Name, Phone, Industry` everywhere; WI-P (WI-000032) pending in Staging.
- **WI-C** (dev): query `+ Website`; `website()` + test in Dev A's sections. → Staging with Run specified tests.
- **WI-D** (dev2): query `+ Fax`; `fax()` + test in Dev B's sections. PR conflicts with Staging on the query line →
  **hand-resolve in Git** (merge `staging` into WI-D, query `…, Website, Fax`) → Staging with tests.
- Custom promotion: Prepare C, Prepare D. Expect D' = `…, Industry, Fax` (no Website) + provenance check failure.
- **Git fix:** on the broken branch, `git checkout origin/staging -- <AccountSummary files>`, commit, push. Wait for the
  check. Continue the custom promotion (Combine); repeat the fix on the combined branch if needed; promote with
  Run specified tests (AccountSummaryTest).
- Provenance check stays on throughout.

## Steps / Actual
Lifecycle Center UI steps were automated in Chrome. Provenance check required on `main` throughout.

### Before snapshot
- `main` = `7961e94`, `staging` = `a681b95`, differ only in LabPing (WI-P = WI-000032 pending). Merge-base `3599bb6`.
- AccountSummary `Id, Name, Phone, Industry` everywhere. Open PRs: stage PR #61 only.

### Setup
1. **WI-C** = WI-000034 (dev): commit `7fb6714` (DORI-124) → Staging with Run specified tests (DORI-126), `staging` =
   `9089bf4`. Side effect: stage PR #61 became **CONFLICTING**. C changed the query line that `main` and `staging`
   had each changed separately since `3599bb6` (Exp 14's combine left that split history: the trap, as in Exp 06).
2. **WI-D** = WI-000035 (dev2; Change Management needed "Show All Changes"): commit `98051f3` (DORI-125). PR #73
   conflicted with Staging on the query line → **hand-resolved in Git**: merged `staging` into WI-000035, query
   `…, Website, Fax`, commit `4926d54`. Validate-only on staging (AccountSummary classes only): 6/6 tests pass.
3. D → Staging with tests (DORI-127), `staging` = `6e4448f`. Staging branch and org: `…, Industry, Website, Fax`.

### Custom promotion
4. Prepare C (DORI-128, PR #74, `50f973e`): `…, Industry, Website`, check **passes**, CLEAN.
   Prepare D (DORI-129, PR #75, `a8c38eb`): `…, Industry, Fax`, **no Website**: the hand resolution was dropped again.
   Provenance check **fails**, PR **BLOCKED**. (Q1: with the check on, the broken version first shows up at D's Prepare.)
5. **Git fix #1 on the prepared branch:** `git checkout origin/staging -- AccountSummary.cls AccountSummaryTest.cls`,
   commit `9d2a373`, push to WI-000035. Check re-ran and passed; PR #75 CLEAN.
6. Select C + D → Next → passed validation → "Resolve Shared Components" → **Combine into WI-000035** (DORI-130 SUCCESS).
   Combined branch: `main` + C (`a5067a4`) + D (`dabd7b0`), **our fix commit gone**. Query `…, Industry, Fax` again
   (website() present, field not queried). New PR #76 **BLOCKED** by the provenance check. (Q2: Combine does **not**
   keep a commit pushed to a prepared branch; it replays the original work-item commits only.)
7. **Git fix #2 on the combined branch:** same checkout from `staging`, commit `130d252`, push. Check passed; PR #76 CLEAN.
8. Select WI-000035 → Next → Promotion Options (offered) → Run specified tests: AccountSummaryTest → Promote.
   DORI-131 **SUCCESS**. `main` = `ee99b8c` = merge of PR #76 **including `130d252`**. release:
   `…, Industry, Website, Fax`, both methods; `sf apex run test -n AccountSummaryTest` on release: **100%**.
   WI-000034 COMBINED, WI-000035 CLOSED, WI-P still PROMOTED in Staging. (Q3: Lifecycle Center promotes the combined
   branch **as left**, extra commits included, as long as nothing re-prepares it.)

## After snapshot
- `main` = `ee99b8c`, `staging` = `6e4448f`: differ only in LabPing (WI-P). Stage merge **clean** again (`git
  merge-tree`); merge-base still `3599bb6`.
- AccountSummary `Id, Name, Phone, Industry, Website, Fax` in release, staging, both branches.
- Open PRs: #61 only.

## Findings
1. **The Git fix works and Production never sees the broken version.** Commit Staging's version of the affected files
   onto the **combined** work item's branch (after Combine, before Promote), wait for checks, promote with tests.
   Lifecycle Center merges the branch head as-is. Works with the provenance check on (the fix makes the PR pass it).
2. **Fix after the last rebuild, not before.** A fix pushed to a *prepared* branch is thrown away by Combine (and,
   by Exp 01/05, would be by a re-Prepare). Every Lifecycle Center rebuild replays only the work items' original commits.
   Order: Prepare all → fix any prepared PR the check blocks (needed to get past Next) → Combine → fix the combined
   branch → promote.
3. **With the check on, you need the fix twice**: once on the prepared branch to get past Next, once on the combined
   branch. Without a blocking check on the prepared PRs, only the second fix should be needed (*Hypothesis*).
4. **The split history from Exp 14 bit again (step 1):** a later work item on the combined line made the stage PR
   CONFLICTING until this promotion brought `main` back in line. Exp 16 must start from a clean stage merge.
