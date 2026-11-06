# Experiment 09: Fix C with two stuck work items on the same line (C3d)

## Question
Exp 08's Lifecycle Center-only escape from a stuck stage (Fix C: custom-promote the stuck work item) worked with one
stuck work item. Does it still work when **two** stuck work items changed the same line one after the other? This is
the best remaining candidate for a stuck state entered with Lifecycle Center only that **needs Git to get out**.

(Scope note: cases that start with a Git action, such as a hand-resolved merge commit or Agentforce resolution, are out of
scope. Recovering work after Never is out of scope too; remaking the work item is acceptable.)

## Design
Start from Exp 08's end state: `main` and `staging` same content (GOLD 0.15), split history (trap armed).
- **WI-C** (dev, after Back Sync): GOLD 0.15 → **0.16**. Promote to Staging.
- **WI-D** (dev2, after C is in Staging): GOLD 0.16 → **0.17**. Promote to Staging.
- Promote Stage → expect blocked (trap).
- Fix C: custom promotion, **prepare both**, select both → Promote → "Resolve Shared Components" →
  **Continue with custom promotion** first. If that fails, try **Combine**.

Local simulation (2026-11-04):
- Promote Stage: **CONFLICT**.
- Prepared C' = main + C = 0.16. Prepared D' = main + D: rebase conflict (0.16→0.17 onto 0.15), WI lines kept → 0.17.
- "Continue" = merge C' PR then D' PR into main: after C', **D' PR conflicts with main**.
- Combine (Exp 05): rebuild D from main replaying C then D → 0.17 = Staging, expected clean.

## Before snapshot
- `main` = `bb92dba`, `staging` = `72ec362`, same content (0.15), merge-base `884729e`. Stage PR #34 open.
- dev 0.14 (behind), dev2 / staging / release 0.15.

## Steps / Actual
Lifecycle Center UI steps were automated in Chrome.

1. **Back Sync dev**: offered only WI-000018 this time (incremental since the last sync). dev → 0.15.
2. **WI-C** = WI-000019 "c3d C GOLD 0.16" (dev): commit `f892ce6` (GOLD 0.15 → 0.16) → staging `bec72c2`.
3. **WI-D** = WI-000020 "c3d D GOLD 0.17" (dev2, CLI deploy of staging's file + 0.17, Show All Changes): commit
   `167fedc` (0.16 → 0.17) → staging `55385c3`. Both PROMOTED. Stage PR #34 **CONFLICTING** (trap sprung). The Staging
   column already showed the cached "couldn't validate … merge conflicts" banner from Exp 08.
4. **Prepare both** (custom promotion): DORI-65 C' = `122a38e` on main (0.16), PR #40. DORI-66 D' = `2ed61f1` on main,
   **0.17, tree == staging** (rebase conflict silently resolved to D's line), PR #41. Each PR MERGEABLE against main.
5. **Select both → Next → "Resolve Shared Components"** (default Combine into WI-000020) → **Continue with custom
   promotion** → DORI-67 PROMOTE **ERROR** "Promotion failed", `ErrorDetails`:
   `{"errorType":"MERGE_CONFLICT","errorMessage":"CONFLICTS: force-app/main/default/classes/DiscountCalculator.cls:content"}`.
   **Clean failure:** nothing deployed (last release DeployRequest [time omitted]), `main` unchanged, PRs #40/#41 still open, both
   WIs PROMOTED. The pipeline view showed **no failure message**: just "2 work items are ready for custom promotion.
   View" next to the old conflict banner. (The browser extension disconnected during this click; the back end confirmed
   it ran.)
6. **Same selection → Combine** (default): "Combining work items…" → DORI-68 REBASE_AND_COMBINE SUCCESS. WI-000020 rebuilt
   from main: `78e2b00` C, `d9b8ab6` D (0.17), **tree == staging**, PR #42; PRs #40/#41 closed; WI-000019 `COMBINED`.
7. **Promote WI-000020** (View → select → Next → Promotion Options → Promote): DORI-69 SUCCESS, release [time omitted] = 0.17,
   `main` = `a47c132`. WI-000020 `CLOSED`.

## After snapshot
- `main` = `a47c132`, `staging` = `55385c3`, same content (0.17), merge-base still `884729e` (trap still armed).
- Open PRs: stage PR #34 only. DiscountCalculator 0.17 in staging, release, dev2; dev 0.16.

## Findings
1. **Fix C with two same-line stuck work items: "Continue" fails, "Combine" works.** Each prepared branch is built on
   `main` separately, so they conflict with each other. Lifecycle Center detects this before deploying and records a
   `MERGE_CONFLICT` error; nothing is half-applied. Combine replays both work items' commits in order and reproduces
   Staging exactly. Still **no Git needed**.
2. The failed custom promotion is **only visible in the request log** (`ErrorDetails` names the file). The UI just goes
   back to "ready for custom promotion".
3. Combine is safe here for the same reason as in Exp 05: every line's final version is in some work item's own commit,
   so replaying them in order rebuilds Staging.
4. Combine/custom promotion still doesn't repair the split history. The stage PR stays open and the trap stays set.

## Not tested: a possible silent regression (Hypothesis)
If you custom-promote **only D** (0.17, matches Staging) and later custom-promote **C** on its own, Prepare would rebase
C's commit (0.15 → 0.16) onto main (0.17), silently keep C's line, and ship **0.16**, undoing D. A provenance check would
**not** stop it, because 0.16 did exist in Staging (after C, before D). Production would then be behind Staging, with
no work item left to fix it. Lifecycle Center-only recovery would still be possible (a new work item setting 0.17), but
nothing would warn you.
