# Experiment 12: Can an ordinary Promote Stage clear the split-history trap? (C3b)

## Question
Every Lifecycle Center-only recovery so far (Exp 08–11) left `main` and `staging` with the same content but **split
history** (merge-base `884729e`), so the next edit to those lines blocks Promote Stage again. Only a Git merge of `main`
into `staging` (Exp 06) has removed the trap. Can Lifecycle Center remove it on its own, with an ordinary work item on a
**different file** pushed through **Promote Stage**?

## Design
- **WI-K** (dev): add a comment to LabPing (no behavior change). Commit only LabPing. Promote to Staging.
- **Promote Stage.** Prediction: the `staging → main` merge is clean (both branches have identical DiscountCalculator),
  so PR #34 merges, `main` then contains staging's tip, and the merge-base moves forward.
- Then simulate a new GOLD edit against the real branches: expect **clean** (trap gone).

## Before snapshot
- `main` = `4a6154c`, `staging` = `4611106`, same content, merge-base `884729e`. Stage PR #34 open.
- Simulated stage merge with a LabPing-only WI: **clean**.

## Steps / Actual
Lifecycle Center UI steps were automated in Chrome.

1. CLI deploy to dev: staging's LabPing + a comment line. **WI-K** = WI-000025 "c3b K LabPing comment" (dev).
   Change Management (default filter) listed LabPing first; dev's stale DiscountCalculator (0.20) was hidden, so
   it couldn't be committed by accident. Commit `cfb15f3` (LabPing only) → staging `b640771`.
2. Stage PR #34 → **MERGEABLE**, `staging-provenance` pass. Pipeline view still showed the **cached** "couldn't validate …
   merge conflicts" banner (as in Exp 02).
3. **Promote Stage** → pre-check passed → Promote Stage's Promotion Options: **"Promote Now" / "Run validate-only
   deploy"**, "Only changes missing from Production (recommended)" / "All changes in the Production stage branch",
   test options. Defaults → DORI-90 SUCCESS. release LabPing [time omitted] (DiscountCalculator untouched, [time omitted]).
   PR #34 merged [time omitted] → `main` = `7d8b6e9` "Merge branch 'staging'". WI-000025 CLOSED.

## After snapshot
- `main` = `7d8b6e9`, `staging` = `b640771`. **Merge-base = `b640771` = staging's tip** (was `884729e` since Exp 05).
- Simulated next edits against the real branches: GOLD 0.19 → 0.21 **clean**, PLATINUM **clean** (both conflicted before).
- No open PRs. release / staging / dev2 GOLD 0.19; dev 0.20 (behind; Back Sync before use).

## Findings
1. **Lifecycle Center can clear the split-history trap without Git.** Once `main` and `staging` have the same content
   (after Fix C / Combine), an ordinary work item on **any other file** pushed through **Promote Stage** merges cleanly;
   `main` then contains staging's tip and the merge-base moves forward. The next edit to the formerly conflicting lines
   merges cleanly.
2. So every situation we've entered with Lifecycle Center only (Exp 07–12) has a **complete** Lifecycle Center-only
   way out, including repairing the history. Git is never strictly required.
3. The cached conflict banner survived until Promote Stage was clicked again.
4. Promote Stage has a **"Run validate-only deploy"** option that custom promotion doesn't show.
