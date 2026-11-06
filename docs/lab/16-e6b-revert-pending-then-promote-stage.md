# Experiment 16: Take pending work out of Staging, then Promote Stage (E6b)

## Question
Exp 14's situation: work items X and Y change the same line, Y's conflict is hand-resolved in Git, and Staging is
correct. WI-P is pending in Staging and must not reach Production. A custom promotion of X + Y would drop the hand
resolution (Exp 14/15). Promote Stage merges `staging` and so keeps it, but it would also ship P.

Can a Lifecycle Center-only route avoid both a broken Production and shipping P?
1. Can a **revert work item** (R) take P's change back out of Staging (commit the old version from a dev org)?
2. Does **Promote Stage** then ship X + Y with the hand resolution, and leave P's file as it is in Production?
3. What do the work item records say afterwards? P will be marked as promoted although its change didn't ship.
4. Can P be redone afterwards as a new work item without trouble?

## Design
- **Setup (Git, not part of the test):** Exp 14's combine left split history on AccountSummary, which would block
  Promote Stage for an unrelated reason (Exp 15 step 1). Healed with Fix B: merged `main` into `staging`
  (`git merge origin/main`, content unchanged), so merge-base = `main`'s tip.
- **WI-X** (dev): query `+ AccountNumber`, `accountNumber()` + test (Dev A sections). → Staging with tests.
- **WI-Y** (dev2): query `+ Site`, `site()` + test (Dev B sections). Conflicts with Staging → **hand-resolve in Git**
  (both fields) → Staging with tests.
- **WI-R** (dev, after Back Sync): LabPing back to `main`'s version (`// c3b: ordinary work item on another file`).
  → Staging with LabPingTest.
- **Promote Stage** with Run specified tests (AccountSummaryTest, LabPingTest).
  Expect: Production AccountSummary = Staging's (both fields), LabPing unchanged.
- **WI-P2** (dev2, after Back Sync): redo P's LabPing comment → Staging. Staging ends with P's change pending again.

## Before snapshot
- After the setup merge: `main` = `ee99b8c`, `staging` = merge of `main` into `6e4448f`; merge-base = `ee99b8c`.
  Only difference: LabPing (P). Open PRs: #61 (stage PR).
- AccountSummary `Id, Name, Phone, Industry, Website, Fax` in release, staging, both branches. WI-P (WI-000032)
  PROMOTED in Staging.

## Steps / Actual
Lifecycle Center UI steps were automated in Chrome. Provenance check required on `main` throughout.

### Setup
0. Healed split history with Fix B: merged `main` into `staging` (`a4e7ce2`), content unchanged, merge-base = `ee99b8c`.
1. **WI-X** = WI-000036 (dev): commit `e1135c8` → Staging with tests (DORI-134), `staging` = `264d3d2`. Stage merge
   still clean (the heal worked; compare Exp 15 step 1).
2. **WI-Y** = WI-000037 (dev2, Show All Changes): commit `bf65791`; conflicts with Staging on the query line →
   **hand-resolved in Git**: merged `staging` into WI-000037, query `…, AccountNumber, Site`, commit `5dbc551`.
   Validate-only on staging: 8/8.
3. Y → Staging with tests (DORI-135), `staging` = `26b0e2c`. Staging now = X + Y (hand-resolved) + P.
   (A custom promotion of X + Y here would drop the hand resolution, as in Exp 14/15.)

### The revert route
4. Back Sync `dev` (DORI-136; offered only WI-000037 and WI-000035: dev already had P because P was built there).
5. **WI-R** = WI-000038 (dev): deployed `main`'s LabPing to dev; Change Management showed it as an ordinary
   **Modify** on LabPing. Commit `43a45bd` (DORI-137): the exact inverse of P's diff. → Staging with LabPingTest
   (DORI-138), `staging` = `36cccb2`, staging LabPing = Production's. `git diff main staging` = AccountSummary only.
6. **Promote Stage** → Promotion Options (Promote Now, Run specified tests: AccountSummaryTest, LabPingTest).
   DORI-139 **SUCCESS**, `main` = `d9e3251` (= `staging`). release: AccountSummary `…, AccountNumber, Site` (Staging's
   **hand-resolved** version), LabPing **unchanged** (`// c3b…`). Stage PR #61 merged; no open PRs.
   **WI-000032 (P), 36, 37, 38 all CLOSED**: P's record says it reached Production, though its change didn't.

### Redo P
7. **WI-P2** = WI-000039 (dev2, already had Production's LabPing): deployed P's LabPing, commit `e98d55a` (DORI-140,
   Show All Changes needed), → Staging with LabPingTest (DORI-141). `staging` = `7c18946`.

## After snapshot
- `main` = `d9e3251`, `staging` = `7c18946`: differ only in LabPing (P2 pending). Merge-base = `36cccb2` (shared
  history), stage merge clean. Open PRs: #81 (new stage PR).
- AccountSummary `Id, Name, Phone, Industry, Website, Fax, AccountNumber, Site` in release, staging, both branches.
- release LabPing = `// c3b…`; staging LabPing = P's comment.

## Findings
1. **The revert route works, Lifecycle Center only, and Production never gets a broken version or P.** Revert the pending
   work item with a new work item (Back Sync → put Production's version in the dev org → commit → Staging), then
   **Promote Stage** with tests. Promote Stage merges `staging`, so the hand resolution survives.
2. **Reverting is an ordinary commit.** Change Management shows the reverted file as a normal Modify; nothing
   special is needed or offered. You need Production's version of the file (here deployed from `main`; without Git,
   copy it from the Production org or the work item's PR diff).
3. **Cost:** two extra work items (revert + redo), two extra Staging deploys, and P's developer redoes P.
4. **The records lie a little:** the reverted work item (P) ends up **CLOSED** as if it shipped. Note it in the work
   item, or track the redo (P2) explicitly.
5. **Only safe on clean history.** A leftover split history from an earlier combine/custom promotion will block Promote
   Stage (Exp 15 step 1). Check `git merge-base` / the stage PR first; if it's blocked you're back to Exp 06/12 fixes.
6. **Also works if P's change isn't a single file:** revert every component P touched. (*Hypothesis*: not tested with
   new components, which would need a destructive change rather than a revert.)
