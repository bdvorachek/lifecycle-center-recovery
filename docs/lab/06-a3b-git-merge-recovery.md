# Experiment 06: Fix a stuck stage with a plain Git merge (A3b)

## Question
Exp 02 fixed a stuck stage the Lifecycle Center way (Fix A: a work item that makes Staging match Production).
A3b tests **Fix B**: reconcile `staging` and `main` with an ordinary Git merge outside Lifecycle Center.
- Does Promote Stage work afterwards?
- Does Lifecycle Center notice or object to a commit on `staging` that it didn't create ("external merge")?
- Does anything get redeployed (Staging org, Production org)?

## Setup: the latent trap left by Exp 05
After Exp 05, `main` (`db7bc26`) and `staging` (`6209f4e`) have **identical content** but separate histories.
Their merge-base is `2040f70` (GOLD_RATE 0.08). Each branch changed GOLD_RATE 0.08 → 0.10 with its own commits
(staging: the original WI-A/WI-B commits; main: the combine's rebuilt commits). Stage PR #22 is MERGEABLE for now.

Local simulation (`git merge-tree origin/main <staging + one new commit>`):

| New work item in Staging changes… | Stage merge |
|---|---|
| GOLD_RATE 0.10 → 0.11 (line 15) | **CONFLICT** |
| PLATINUM_RATE (line 16, adjacent) | **CONFLICT** |
| SILVER_RATE (line 14, adjacent) | **CONFLICT** |
| MAX_DISCOUNT (line 19) | clean |
| SILVER_THRESHOLD (line 9) | clean |

**Hypothesis (H1):** a combine without hand resolution is safe *at the time*, but it leaves a latent trap. The
next ordinary work item that touches the combined lines (or lines next to them) makes Promote Stage stuck.

## Before snapshot
- `main` = `db7bc26`, `staging` = `6209f4e`, no content diff. Open PRs: #22 `Promotion: staging → main` (MERGEABLE).
- WorkItems: 001–009 CLOSED (002 COMBINED), 010 COMBINED, 011 NEVERED, 012 CLOSED.
- DiscountCalculator (GOLD / PLATINUM / MAX): dev 0.09/0.18/2000 (stale, from Exp 05 WI-A), dev2 0.10/0.18/2000,
  staging 0.10/0.18/2000, release 0.10/0.18/2000.

## Steps
1. (CLI, done) Deployed staging's DiscountCalculator with GOLD_RATE **0.11** to dev. Only line 15 differs. Tests 4/4.
2. (Lifecycle Center) New work item in `dev` → Pull changes → commit DiscountCalculator only → promote to Staging.
3. (Lifecycle Center) **Promote Stage.** H1 predicts "Cannot initiate promotion due to merge conflicts."
4. (Git, outside Lifecycle Center) Merge `origin/main` into `staging`, keep Staging's version (0.11), merge it into
   `staging` via a PR. Staging's tree doesn't change; only its history now includes `main`.
5. Check that stage PR #22 is MERGEABLE. **Promote Stage** again. Observe: success? warnings? what gets deployed?

## Actual
- Steps 2–3: WI-000013 "a3b GOLD 0.11" (dev), commit `4d38d62` (DiscountCalculator line 15 only). PR #27 merged [time omitted]
  → `staging` = `597d239`. staging redeployed [time omitted]. WI-000013 `PROMOTED`.
- Stage PR #22 auto-updated to `597d239` → **CONFLICTING**. Promote Stage → **merge conflict popup**.
  **H1 confirmed:** the clean-looking combine from Exp 05 left a latent trap, sprung by one ordinary work item.
- Step 4 (Git, outside Lifecycle Center): `staging` is **not protected**. Branch `a3b-reconcile` from `origin/staging`,
  `git merge origin/main` → conflict on line 15 (0.11 vs 0.10), resolved `--ours` (0.11). Commit `3a0dcc7`; its tree is
  **identical** to staging's. PR #28 → staging, merged in GitHub → `staging` = `36827d2`.
- PR #22 auto-updated to `36827d2` (8 commits) → **MERGEABLE**. `staging-provenance` check: **pass**.
- staging **not redeployed** (DiscountCalculator still [time omitted]). Expected: nothing in Lifecycle Center ran, and
  staging's content didn't change.
- Step 5: pipeline view **still showed the old merge-conflict banner** (cached, as in Exp 02). No sign that Lifecycle
  Center noticed the outside commit on `staging`. Promote Stage → **success, no popup, no warning**.
  DORI-43 [time omitted] → [time omitted] SUCCESS. release DiscountCalculator deployed [time omitted] (GOLD 0.11), PR #22 merged
  [time omitted] → `main` = `a0aeda8` "Merge branch 'staging'" (deploy before merge again, ~4s). WI-000013 → `CLOSED`.

## After snapshot
- `main` = `a0aeda8`, `staging` = `36827d2`, **no content diff**. No open PRs.
- Merge-base of main/staging is now **`36827d2` (staging's tip)**. Simulated next edit to GOLD_RATE: **clean**.
  The latent trap is gone for good, not just this one conflict.
- DiscountCalculator: dev 0.11 ([time omitted], CLI), dev2 **0.10** (behind, untouched), staging 0.11 ,
  release 0.11 .

## Findings
1. **The Git fix works and Lifecycle Center accepts it silently.** A merge of `main` into `staging` made outside
   Lifecycle Center (here via a GitHub PR) cleared the stuck stage. No "external merge" warning, no error, and the
   reconcile commit simply rode along in the stage PR.
2. Unlike Fix A, the Git fix **lets you keep Staging's tested version** (0.11) and needs no dev org, work item or
   extra deploy. Production got exactly what Staging had.
3. Nothing redeployed the Staging org (its content didn't change). Promote Stage deployed only the promoted work
   item's components to Production, as before.
4. The cached conflict banner survives an outside fix too. Clicking Promote Stage re-checks.
5. **Latent trap (H1 confirmed):** a combine leaves `main` with rewritten commits, which splits the histories even
   when content matches. Exp 05 ended "clean", yet the very next work item touching
   the combined lines **or adjacent lines** (Git's conflict hunks include neighbors) blocked Promote Stage.
6. What heals the history is the **successful stage merge**: once `main` contains staging's tip, the merge-base moves
   there and the trap is gone for all lines. Both fixes end that way (Fix A in Exp 02 also did). The difference is
   which version survives: Fix A forces Production's, Fix B lets you pick (Staging's here).

## Hypotheses raised
- **H2:** any custom promotion (Prepare = rebase onto `main`) splits the history the same way, not just combine. A
  later Promote Stage that merges cleanly heals it (as after Exp 04). The trap persists while no stage merge happens.
- **H3:** a no-content `main → staging` merge right after any custom promotion/combine prevents the trap (preventive Fix B).
