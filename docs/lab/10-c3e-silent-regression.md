# Experiment 10: Silent regression from out-of-order custom promotions (C3e)

## Question
With two same-line work items stuck in Staging (E then F), what happens if you custom-promote the **newer** one (F)
first and the **older** one (E) later? Hypothesis: E's Prepare silently keeps E's line, so Production goes **back**
to E's value, and the staging-provenance check can't catch it because that version did exist in Staging once.
Then: is there a Lifecycle Center-only way to get Production back to Staging's value?

## Design
Start: `main` = `a47c132`, `staging` = `55385c3`, same content (GOLD 0.17), split history (trap armed).
- **WI-E** (dev, after Back Sync): GOLD 0.17 → **0.18**. Promote to Staging.
- **WI-F** (dev2, after E is in Staging): GOLD 0.18 → **0.19**. Promote to Staging. (Stage is now stuck.)
- Custom promotion of **F only** (Continue) → Production 0.19 (= Staging).
- Custom promotion of **E only** → Production **0.18** predicted.

Local simulation (2026-11-04): F-only → main 0.19. Then E-only → main **0.18** (staging 0.19). The resulting file
**existed on staging** (after E's merge), so the provenance check passes. A later stage merge **conflicts**.

## Steps / Actual
Lifecycle Center UI steps were automated in Chrome.

1. Back Sync dev (offered only WI-000020, incremental). **WI-E** = WI-000021 (dev), commit `50d76d8` 0.17 → 0.18 →
   staging `1eaec28`.
2. **WI-F** = WI-000022 (dev2, Show All Changes), commit `6537a33` 0.18 → 0.19 → staging `406f18b`. Both PROMOTED.
   Stage PR #34 CONFLICTING (trap from Exp 08/09 sprung again).
3. **Custom promotion of F only**: Prepare (DORI-75) → `d2f75dc` on main, 0.19, tree == staging. Shared-components
   dialog (default Combine into WI-000022) → Continue → release [time omitted] = **0.19**, `main` = `f49bf8e`. WI-000022
   CLOSED. Now `main` and `staging` both 0.19 → **Promote Stage would merge cleanly** (PR #34 MERGEABLE). The safe next
   step is the obvious one.
4. **Custom promotion of E alone**: Prepare (DORI-77) → `68717f8` on main, **0.18**, no markers. PR #46 diff:
   DiscountCalculator **+1 −1 (0.19 → 0.18)**. `staging-provenance` **pass** (that exact file existed on staging after
   E's merge). No shared-components dialog (no other WI in the stage), plain Promotion Options → Promote. DORI-78
   SUCCESS, release [time omitted] = **0.18**, `main` = `1df9c24`. WI-000021 CLOSED.
5. **After**: Production 0.18, Staging 0.19, all WIs CLOSED. Pipeline view: "No Work Items in Staging", Promote Stage
   disabled, **no warning**. Latest Promotions shows "c3e E GOLD 0.18" on top. Stage merge (simulated) **conflicts**.

## LC-only recovery (simulated against the real branches)
| Attempt | Result |
|---|---|
| Re-commit 0.19 from a synced dev org | Nothing to commit (Staging already has 0.19) |
| WI on another line → Promote Stage | Blocked (conflict). Custom-promoting it ships main + that line (GOLD still 0.18); provenance check **blocks** it |
| WI changing GOLD to a new value (0.20) | Fix C works, Production = Staging = 0.20 |
| Two throwaway WIs 0.19 → 0.20 → 0.19, **Combine** | Production 0.19 = Staging, provenance passes |

Git (Fix B) doesn't make this easy either: after merging `main` into `staging`, `main` would get 0.19 at the next
Promote Stage, but Promote Stage only deploys the promoted work items' components (Exp 02). The org gets 0.19 only if
that work item includes DiscountCalculator, which again means changing it.

## Findings
1. **Confirmed: out-of-order custom promotions silently roll Production back.** Custom-promoting the newer of two
   same-line work items and then the older one shipped the older value over the newer one. No dialog, no warning,
   and the provenance check passed.
2. Afterwards Lifecycle Center shows a clean pipeline. Nothing tells you Production is behind Staging. Only a Git diff
   (`git diff origin/main origin/staging`) or comparing the orgs reveals it.
3. **Recovery doesn't strictly need Git**, but restoring the exact tested value takes two throwaway work items and a
   Combine (or shipping a new value). This is the most contorted Lifecycle Center-only path so far.
4. Prevention: when several stuck work items touch the same lines, promote them **together with Combine** (Exp 09), or
   make sure a later Promote Stage covers the rest. Never custom-promote an older one on its own after a newer one.
   A stronger provenance check would compare against Staging's **tip**, not any version that ever existed there.
