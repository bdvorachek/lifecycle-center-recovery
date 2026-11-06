# Experiment 21: Custom promotion of one of two independent work items (C1)

## Question
Does an ordinary custom promotion (Prepare → Promote) split `main`'s history from `staging`'s even when nothing
overlaps: two work items on **different** files, no Combine dialog, no hand resolution? And does a later Promote Stage
repair it?

## Design
- **WI-A** (dev): a comment line in `LabCarrierTest`. **WI-B** (dev): a header comment in `DiscountCalculator`. Both →
  Staging together.
- Custom-promote **WI-A only** (Prepare → Next → Promote with tests). Then check `git merge-base`, the `main`/`staging`
  diff, and whether the stage merge is clean.
- Simulate locally (no push) a later edit on `staging` next to A's line, and one 3 lines away, and merge each with
  `main` (`git merge-tree`).
- **Promote Stage** to ship WI-B. Check the merge-base again and re-run the adjacent-edit simulation.

## Before snapshot
- Exp 20's after state: `main` = `bcf2efc`, `staging` = `952b23b`, merge-base = `952b23b` (staging's tip, shared
  history), identical content. No open PRs.

## Steps / Actual
1. **WI-A** = WI-000048: commit `0428c57` (DORI-170). **WI-B** = WI-000049: commit `d606d25` (DORI-171). Both → Staging
   in one promotion with LabCarrierTest + DiscountCalculatorTest (DORI-172). `staging` = `8642af0`; merge-base still
   `952b23b`.
2. Staging menu → Select Work Items to Promote → **Prepare** WI-000048 (DORI-173 `REBASE`): prepared branch `0e48c25` =
   A's change **replayed** onto `main` (new commit). PR #99 CLEAN.
3. Select WI-000048 → Next: **no Combine dialog**, straight to Promotion Options → LabCarrierTest → Promote. DORI-174
   **SUCCESS**. release: LabCarrierTest has A's line, DiscountCalculator doesn't have B's.
4. Afterwards:
   - `git merge-base main staging` = **`952b23b`, unchanged**. A's change is on `main` as `0e48c25` and on `staging` as
     `0428c57`: same content, different commits.
   - `git diff main staging` = DiscountCalculator only (B, waiting). Content is right.
   - Stage merge: **CLEAN** (both sides made the identical change to LabCarrierTest).
5. **Simulation (local commits, not pushed):** a later `staging` edit to the line **next to** A's line → `git merge-tree`
   with `main`: **CONFLICT**. An edit **3 lines away**: CLEAN.
6. **Promote Stage**: first click showed *"Can't validate promotion: … your source control is checking the pull
   request. Try again later"* (the stage PR's provenance check was still running). After it passed, Promote Stage with
   DiscountCalculatorTest, DORI-175 **SUCCESS**. `main` = `7467976`, merge-base = **`8642af0` (staging's tip)**.
   release has A and B.
7. Re-ran the step 5 adjacent-edit simulation: **CLEAN**.

## After snapshot
- `main` = `7467976`, `staging` = `8642af0`, merge-base = staging's tip; identical content. No open PRs.
- LabCarrierTest has A's comment, DiscountCalculator has B's comment, in release, staging and both branches.

## Findings
1. **Yes: even a plain, non-overlapping custom promotion splits the history.** Prepare replays the work item's commit
   onto `main` as a new commit, and nothing merges `staging` into `main`, so the merge-base stays where the last Promote
   Stage left it. No Combine, dialog or hand resolution is needed.
2. **It's invisible at first.** Content is right and the stage merge stays clean, because both sides made the identical
   change.
3. **It becomes a trap for that file.** A later change on either side to the custom-promoted lines **or the lines next
   to them** conflicts at the next Promote Stage (simulated here; observed for real after a Combine in Exp 06 and a
   custom promotion in Exp 08). Edits a few lines away merge fine.
4. **One successful Promote Stage repairs it completely** (merge-base moves to Staging's tip; the same edit then merges
   cleanly), as in Exp 12.
5. So with custom promotion only, the divergence keeps growing: every custom-promoted change adds trap lines until the
   next Promote Stage goes through. Rule: **after a custom promotion, get a Promote Stage through before anyone edits
   those lines again** (or merge `main` into `staging` in Git).
6. Minor: Promote Stage can refuse with *"source control is checking the pull request"* while a required check on the
   stage PR is still running. Just retry.
