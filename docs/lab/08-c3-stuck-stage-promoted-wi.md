# Experiment 08: Stage vs Production conflict with the stuck work item already in Staging (C3)

## Question
Exp 07 showed a work item vs stage conflict can be fixed without Git (Never → Back Sync → redo). But once a work item
has been **promoted into Staging**, can it still be set to Never? If the Staging → Production merge conflicts, is
there any Lifecycle Center-only way out, or is this a **Git required** case?

## Design (no combine, just an ordinary custom promotion)
- **WI-A** (dev, Back Synced first): GOLD_RATE 0.13 → **0.14**. Promote to Staging.
- **WI-B** (dev2, started after A is in Staging): GOLD_RATE 0.14 → **0.15**. Promote to Staging.
- **Custom promotion of WI-A only** to Production. Prepare rebases A's commit onto `main` → Production 0.14.
- Then Promote Stage with B waiting.

Local simulation (worktree, 2026-11-04):
- `main` after A-only = 0.14. Promote Stage (staging 0.15, merge-base 0.13) → **CONFLICT**.
- Possible escape: custom promotion of **WI-B alone** = rebase B's commit (0.14 → 0.15) onto main (0.14) → **clean**,
  main tree == staging tree. But histories stay split: the next GOLD edit would **conflict** (latent trap); a work item
  touching an unrelated line would merge cleanly and heal the history.

## What to observe once stuck
1. Is **Never** offered for WI-B (status PROMOTED)?
2. Is **Back Sync** allowed (B is PROMOTED, not In Progress/Review/Ready)?
3. Can WI-B be custom-promoted on its own, and does it ship 0.15?
4. Fallbacks: Fix A (work item copying Production's line into Staging), Fix B (Git merge).

## Before snapshot
- `main` = `abaa99c`, `staging` = `884729e`, same content, merge-base = staging tip. No open PRs.
- DiscountCalculator 900 / 0.13 in all four orgs (dev after Back Sync DORI-51 [time omitted]; it listed the dev2-origin
  WIs 16, 12, 9, 3, not the NEVERED ones).
- Back Sync dialog showed dev2 **"In Sync"** (after its WI-000016 shipped), dev "Not in Sync" (before DORI-51).

## Steps / Actual
Lifecycle Center UI steps were automated in Chrome.

1. **Back Sync dev** (DORI-51, [time omitted]): offered the dev2-origin WIs 16, 12, 9, 3. dev → 900 / 0.13.
2. **WI-A** = WI-000017 "c3 A GOLD 0.14" (dev, created from the dev org top bar). DiscountCalculator **was** listed
   under the default filter in dev. Commit `fd18d85` (parent `884729e`, GOLD only). Review → ready → promoted.
   `staging` = `2e81bcf` (0.14).
3. **WI-B** = WI-000018 "c3 B GOLD 0.15" (dev2, CLI deploy of staging's file + 0.15). Default filter **hid**
   DiscountCalculator again (F1); Show All Changes. Commit `ce1c4ec` (parent `2e81bcf`, GOLD 0.14 → 0.15). Promoted →
   `staging` = `72ec362` (0.15). Stage PR #34 opened. Both WIs PROMOTED.
4. **Custom promotion of WI-A only.** Staging column menu: Open Environment / View Branch in Source Control /
   **Select Work Items to Promote** / Replace Environment. Custom Promotion dialog: *"Promote selected work items to the
   next stage without promoting the entire stage. … Use this option sparingly to avoid merge conflicts."* Prepare
   WI-000017 → PR #36, `aa263e6` on `main` (0.14), `staging-provenance` pass.
   Selected only WI-000017 → Next → **"Resolve Shared Components"** (WI-000017, WI-000018 / DiscountCalculator), default
   "Combine work items into WI-000018", or "Continue with custom promotion: *Promote WI-000017. Other work items might
   have merge conflicts or promotion failures.*" → chose Continue → went **straight to "Initiating promotion"** (no
   Promotion Options dialog). DORI-57 SUCCESS, release deployed [time omitted] (0.14), `main` = `71f9091`. WI-000017 CLOSED.
   → **The dialog appears with only one prepared WI** when another WI in the stage shares the same line (Exp 04: no
   dialog for different lines). Refines B3b/B3c.
5. **Stuck.** PR #34 **CONFLICTING**. Pipeline view: no warning. Promote Stage → "Can't validate promotion: Cannot
   initiate the promotion due to merge conflicts" (Close / Resolve using Agentforce).
6. **Can WI-B be Nevered? No.** The PROMOTED work item's status panel has **no menu at all** (just "Promoted to Staging on
   … View Details"). The record header menu only has New Contact, New Recurring Donation (the org's own actions) and
   Change Development Environment. Never is only offered before promotion.
7. **Escape: custom promotion of WI-B alone.** Prepare WI-000018 (DORI-58 REBASE): PR #37 appeared at [time omitted],
   `5f39703` on `main`, 0.15, no markers, **tree == staging**, check pass. But the request stayed `NEW` and the dialog
   said "Preparing…" until [time omitted] (~3½ min, vs seconds for WI-A). Then Next → **no** shared-components dialog →
   Promotion Options ("Only changes missing from Production (recommended)") → Promote. release deployed [time omitted] (0.15),
   `main` = `bb92dba`. WI-000018 CLOSED.

## After snapshot
- `main` = `bb92dba`, `staging` = `72ec362`, **same content**, but merge-base still `884729e` (split history).
- Stage PR #34 still OPEN, now MERGEABLE (no-op). No WIs in Staging, so Promote Stage is disabled.
- Simulated next edits against the real branches: GOLD → **CONFLICT**, PLATINUM (adjacent) → **CONFLICT**,
  MAX_DISCOUNT → clean. **The latent trap (Exp 06) is in place.**
- DiscountCalculator 0.15 in staging and release; dev2 0.15 (our deploy); dev 0.14 (behind).

## Findings
1. **A work item that's been promoted into a stage can't be set to Never.** The status menu disappears once it's
   PROMOTED. Exp 07's Never → Back Sync → redo path is closed.
2. **An ordinary custom promotion (no combine) causes a stuck stage**: promoting the older of two same-line WIs left
   Staging and Production conflicting. H2 confirmed for the "older WI only" case.
3. **Lifecycle Center-only escape: custom-promote the stuck work item itself.** Prepare rebases its own commit onto
   `main`. Here that reproduced Staging exactly, so Production got the tested version and the provenance check passed.
   Nothing in the UI suggests this: the popup only offers Agentforce.
4. **The escape doesn't repair history.** The stage PR stays open and the next edit to those (or adjacent) lines will
   block Promote Stage again. Repairing it needs a successful stage merge (a WI touching other lines + Promote Stage,
   hypothesis) or a Git merge of `main` into `staging` (Fix B, Exp 06).
5. The shared-components dialog appears even when only **one** WI is prepared, if another WI in the stage changes the
   same line. Choosing Continue skips the Promotion Options dialog.

## When would Git really be required? (Hypothesis)
The escape works because WI-B's **own commit** contains the final Staging version of every conflicting line. It would
not if Staging's version lives somewhere the work item's commits don't carry, such as a hand-resolved merge commit
(Exp 01) or a direct commit to `staging`. Then custom-promoting the stuck WI ships a version Staging never had: the
provenance check blocks it (or, without the check, untested code ships). With Never gone and Promote Stage blocked,
the only Lifecycle Center-only path left is Fix A (a work item copying **Production's** lines into Staging), which
discards Staging's tested version. Keeping it needs Git (Fix B). Not yet tested.
