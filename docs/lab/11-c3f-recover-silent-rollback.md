# Experiment 11: Recover from the silent rollback with Lifecycle Center only (C3f)

## Question
After Exp 10, Production has GOLD **0.18** and Staging **0.19**, with no work items in Staging and no warning anywhere.
Can we restore Production to exactly Staging's 0.19 using only Lifecycle Center? Simulated path: two throwaway work
items (0.19 → 0.20 → 0.19), then custom promotion with **Combine**. Also: what does the Promotion Options choice
"All changes in the … stage branch" deploy?

## Why Promote Stage is blocked but custom promotion isn't
Promote Stage merges `staging` into `main`; the branches changed GOLD differently since merge-base `884729e`, so the merge
conflicts. Custom promotion rebuilds each work item from its own commits on top of `main` and never merges `staging`,
so it isn't affected (and can ship versions Staging doesn't have, as in Exp 10).

## Design
- Back Sync dev (it has 0.18; Staging has 0.19).
- **WI-G** (dev): 0.19 → **0.20**. Promote to Staging.
- **WI-H** (dev2, after G): 0.20 → **0.19**. Promote to Staging. Staging ends at 0.19 again.
- Promote Stage → expect blocked (main 0.18 vs staging 0.19 since merge-base).
- Custom promotion: prepare G and H → Combine → promote the combined WI with **"All changes in the Production stage
  branch"**. Expect Production 0.19 = Staging; record what gets deployed.

## Before snapshot
- `main` = `1df9c24` (0.18), `staging` = `406f18b` (0.19), release 0.18. No WIs in Staging. Stage PR #34 open.

## Steps / Actual
Lifecycle Center UI steps were automated in Chrome.

1. Back Sync dev (offered only WI-000022). dev 0.18 → 0.19.
2. **WI-G** = WI-000023 "c3f G GOLD 0.20 (throwaway)" (dev): `52feedc` 0.19 → 0.20 → staging `d171154`.
3. **WI-H** = WI-000024 "c3f H GOLD back to 0.19" (dev2): `90b24fc` 0.20 → 0.19 → staging `4611106`. Staging's tree is
   now **identical to before the throwaways** (`406f18b`). Stage PR #34 CONFLICTING.
4. **Promote Stage → "Can't validate promotion"** (merge conflicts), before any Promotion Options. So Promote Stage's
   own "All changes" option can't be reached while the stage is stuck.
5. **Prepare both**: G' (DORI-84) = 0.20; H' (DORI-85) = **0.19**. H's rebuild on main (0.18) silently kept H's line, so
   H alone would have restored 0.19, but it would have left G in Staging, and custom-promoting G later would have
   rolled Production to 0.20 (the Exp 10 problem again).
6. **Select both → Combine into WI-000024** (DORI-86): rebuilt from main as G (`f97da78`) then H (`ca9963e`), **0.19,
   tree == staging**. WI-000023 COMBINED.
7. **Promote WI-000024 with "All changes in the Production stage branch"** (not the default): DORI-87 SUCCESS, `main` =
   `4a6154c`, release [time omitted] = **0.19**. DeployRequest: **4 components** (DiscountCalculator, DiscountCalculatorTest,
   LabPing, LabPingTest, i.e. every class in `main`), vs 1 component for the default option. WI-000024 CLOSED.

## After snapshot
- `main` = `4a6154c`, `staging` = `4611106`, **same content (0.19)**. Merge-base still `884729e` (trap still armed).
- Open PRs: stage PR #34 only. release 0.19, staging 0.19, dev2 0.19, dev 0.20 (G's value, behind).

## Findings
1. **The silent rollback can be undone with Lifecycle Center only**: two throwaway work items (0.19 → 0.20 → 0.19)
   promoted to Staging, then custom promotion with **Combine**. Production got exactly Staging's version and the
   provenance check passed. It costs two fake work items and two extra Staging deploys.
2. Promote Stage stays blocked throughout (the split history), so the recovery has to go through custom promotion.
3. **"All changes in the <stage> stage branch" = deploy the whole branch**, not only the promoted work items'
   components. That makes it a Lifecycle Center-only way to **resync an org with its branch** (useful after drift, or
   after a Git-only fix that changed the branch without deploying). In a real repo this is a full deploy, with the test
   requirements that come with it.
4. The trap (split history) is still there after every Lifecycle Center-only recovery so far. Only a successful stage
   merge, or a Git merge of `main` into `staging`, removes it.
