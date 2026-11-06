# Experiment 20: Commit on a prepared branch, then promote without Combine (D1c)

## Question
Exp 15 showed Combine throws away a commit pushed to a **prepared** branch, so the Git fix needed two commits. When no
Combine happens, is a commit on the prepared branch promoted as-is? If so, the Git fix needs only one commit in that
case.

## Design
- **WI-S** (dev): adds a header line `d1c S` to DiscountCalculator → Staging.
- Custom promotion of WI-S **alone** (no other work item shares the file, so no Combine dialog). Prepare.
- Push one commit to the prepared branch `WI-000046`: DiscountCalculator = an **earlier staging version** (`e7cac4f`,
  without the `d1a` and `d1c S` lines). An earlier staging version keeps the provenance check passing.
- Promote with tests. If Production and `main` lack both lines, the prepared branch went through as left.
- Cleanup (Lifecycle Center only): a work item putting Production's version into Staging, then Promote Stage.

## Before snapshot
- Exp 19's after state: `main` = `667386d`, `staging` = `282e5e3`, identical, shared history, no open PRs.
  DiscountCalculator has the `d1a` header line everywhere except dev (which never got Exp 19's direct commit).

## Steps / Actual
1. dev's DiscountCalculator **lacked** the `d1a` line (a direct commit never reaches dev orgs). Deployed Staging's
   version + the S line to dev (`--ignore-conflicts`). **WI-S** = WI-000046: commit `5ca8033` (DORI-163), diff = the
   S line only. → Staging with DiscountCalculatorTest (DORI-164), `staging` = `635189c`.
2. Staging stage menu → **Select Work Items to Promote** → **Prepare** WI-000046 (DORI-165 `REBASE`): branch rebuilt as
   `cfff173` on `main`; PR #94 `WI-000046 → main`.
3. Pushed `d4fadd6` to `WI-000046`: DiscountCalculator = `e7cac4f`'s version (removes the `d1a` and S lines).
   Provenance check **passed** (blob existed on staging), PR #94 CLEAN.
4. Selected WI-000046 → **Next**: no Combine dialog, straight to Promotion Options. Run specified tests
   DiscountCalculatorTest → Promote. DORI-166 **SUCCESS**. PR #94 merged as `82859d6` **including `d4fadd6`**. release
   deploy: DiscountCalculator only; release DiscountCalculator has **neither** line (the prepared branch's version).
   staging still has both. WI-000046 CLOSED.
5. Side effect: `git merge-tree main staging` **CONFLICT** on DiscountCalculator (merge-base `282e5e3`): `main` removed
   the `d1a` line, `staging` added a line next to it. The split-history trap (Exp 06/08), so the next Promote Stage
   would have been blocked.

### Cleanup
6. Deployed `main`'s DiscountCalculator to dev. **WI-S2** = WI-000047, commit `deca165` (DORI-167, removes the two
   lines) → Staging (DORI-168). Stage merge now **clean** (both sides end at the same content).
7. **Promote Stage** (default, DiscountCalculatorTest), DORI-169 **SUCCESS**. `main` = `bcf2efc`, merge-base =
   `staging` tip `952b23b`: history repaired (as in Exp 12).

## After snapshot
- `main` = `bcf2efc`, `staging` = `952b23b`: identical content, shared history. No open PRs.
- DiscountCalculator without the `d1a` / `d1c S` lines in release, staging, dev and both branches.

## Findings
1. **Yes: without Combine, a commit on a prepared branch is promoted as-is.** Lifecycle Center merged the prepared PR at
   its head (our commit included) and deployed the work item's component from it. Promotion Options (tests) were
   offered as normal.
2. So the Git fix (guide: Test failures → The Git fix) needs **one** commit when the custom promotion
   doesn't Combine. When work items share a component (the Exp 14/15 case), the Combine dialog appears and Combine drops
   the commit, so you still need the second commit on the combined branch. (*Hypothesis:* choosing **Continue** instead
   of Combine would keep it, but Continue skips Promotion Options, so no tests (Exp 08), and fails on same-line
   overlaps (Exp 09).)
3. **Any Git fix on a prepared or combined branch splits the history** when it makes `main` differ from `staging`:
   the next Promote Stage will conflict on that file. Follow it with Fix B (merge `main` into `staging`) or a work item
   that makes Staging's content match, then one Promote Stage (Exp 12).
4. Confirms D6b's premise: a dev org never receives a direct commit (dev lacked Exp 19's `d1a` line). A work item
   built from it would revert the line.
