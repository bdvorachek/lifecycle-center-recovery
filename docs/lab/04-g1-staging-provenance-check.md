# Experiment 04: "Staging provenance" CI check (G1)

## Goal
A required GitHub check on `main` that blocks any promotion that would put a file version on `main` that `staging` never
had. Targets the combine problem (Exp 01): combine sent Production a DiscountCalculator that never existed in Staging.
E5 (Exp 03) showed Lifecycle Center respects required checks and blocks **before deploying**, so a check is enough.

## The check
`.github/scripts/staging-provenance.sh <base> <result> <staging> [pathspec]` + `.github/workflows/staging-provenance.yml`
(job `staging-provenance`, on `pull_request` to `main`, `fetch-depth: 0`).
For every file under `force-app` that differs between the PR base (main) and GitHub's test merge (`refs/pull/N/merge`):
- changed/added → its blob must equal the file's blob at some commit on **staging's first-parent chain** (versions staging
  itself held; commits that only lived on work item branches don't count);
- deleted → must not exist on staging's tip.

## Offline validation against real history (2026-11-01)
| PR | Kind | base → result, staging | Expected | Result |
|---|---|---|---|---|
| #2 | baseline stage promotion | 40c7528 → c90ae37, 7c6b185 | pass | pass (4 files) |
| #8 | **combined** WI-000003 → main | c90ae37 → f19b10f, 901fc39 | **fail** | **fail**: DiscountCalculator.cls (blob 361ae99), DiscountCalculatorTest.cls (71de021) never on staging |
| #5 | stage promotion after reconcile | f19b10f → 022b191, a7ff1b4 | pass | pass (LabPing ×4) |
| #12 | stage promotion (E5) | 022b191 → c788e7f, c592ddc | pass | pass (LabPing ×2) |

## Rollout (out-of-band, also a Group D data point)
- Committed workflow + script **directly to `staging`** (`8356096`, pushed 2026-11-01). Lifecycle Center can't commit
  non-metadata files. It reaches `main` with the next Promote Stage.
- Lifecycle Center reaction after 20s: **none**. No stage PR opened, no DevopsRequestInfo. (Stage PRs are pre-opened only
  after Lifecycle Center's own promotions into the stage.)
- Pipeline view after the push: Staging shows **"No Work Items in Staging"** and **Promote Stage is disabled**, even
  though `staging` is 1 commit ahead of `main`. No warning about the commit made outside Lifecycle Center.
  → Lifecycle Center tracks stage content by work items, not by branch diff. An out-of-band commit on a stage branch
  can't be promoted by itself. It rides along with the next work item's Promote Stage (unseen in the UI).
- Branch protection on `main`: required check changed `lab-gate` → **`staging-provenance`** (enforce_admins still on).

## Live test 1: normal promotion should pass
1. Out-of-band: LabPing → `'pong v3'` (+ test) deployed to dev.
2. Lifecycle Center: WI-000007, commit, promote to Staging. Watch: pipeline view after the out-of-band staging commit,
   whether the WI branch (cut from staging) contains `.github/`, and the stage PR's check run.
3. Promote Stage → expect success; `main` gets LabPing v3 **and** the workflow files.

Actual:
- WI-000007 "provenance", commit `f4b935c` (LabPing + Test). PR #13 merged → `staging` = `a83e494`.
  WI-000007's branch **contains `.github/`** (cut from staging after the out-of-band commit).
- Stage PR #14 auto-opened [time omitted]. Workflow run 41363714584 triggered by LC's PR (pull_request event works with LC's
  OAuth token), started [time omitted], **7s**, success: LabPing.cls + LabPingTest.cls "matches staging @ a83e494".
  PR #14 `CLEAN`. Diff main..staging = LabPing ×2 + the two `.github` files (the out-of-band commit rides along).
- Promote Stage: **success**. DORI-24 PROMOTE [time omitted]–[time omitted], release LabPing deployed [time omitted] (`'pong v3'`),
  PR #14 merged [time omitted] → `main` = `1cbe303`, now contains `.github/`. main == staging. WI-000007 CLOSED.
  The out-of-band commit reached `main` without ever showing in the Lifecycle Center UI.

## Live test 2: out-of-order custom promotion should be blocked (C2)
Scenario = **C2** (out-of-order custom promotion, overlapping but non-conflicting work items):
- WI-X (dev): DiscountCalculator `PLATINUM_RATE` 0.15 → 0.18 (line 16).
- WI-Y (dev2): DiscountCalculator header comment line 2 `... lab.` → `... lab (G1 test 2).`
- Local `git merge-file`: X + Y merge cleanly. No test changes needed (4/4 pass for each).
- Setup (2026-11-01, CLI): deployed X to dev, Y to dev2. Y's file is built on `main`'s version, so this also
  **resynced dev2** (it had Exp 01's GOLD_THRESHOLD 5000). That retires A4/D6 as originally planned.

Steps:
1. Commit WI-X (dev) and WI-Y (dev2) **both before promoting either**, so both branches start from the same `staging`.
2. Promote WI-X → Staging, then WI-Y → Staging. Staging versions: base, base+X, base+X+Y.
3. Custom-promote **only WI-Y** to Production → expect "Resolve Shared Components" → choose **Continue** (not Combine).
4. Prediction: `main` would get base+Y (never on staging) → `staging-provenance` fails → Lifecycle Center blocked
   before deploy (per E5). Watch which PR is opened (`WI-Y → main`?) and the check result.
5. Then (variant) choose **Combine** instead → combined result should be base+X+Y = staging's version → check passes.

Actual (2026-11-01/02 UTC):
- Committing WI-Y in dev2: Change Management's default **"Show Uncommitted Changes"** filter hid DiscountCalculator
  and DiscountCalculatorTest (the only listed components this environment had committed before, in Exp 01) while
  showing Admin, fragment_space etc. **"Show All Changes"** listed them. Before that, I'd deployed main's version and
  then Y's again to bump SourceMember RevisionCounter. It didn't help. Redeploying identical content reports "Unchanged"
  and doesn't bump the counter. Hypothesis: "uncommitted" ≈ never committed from this environment, not "changed
  since the last commit".
- WI-000008 = X (`995c31a x`), WI-000009 = Y (`43f143e y`, DiscountCalculator only). Promoted to Staging: X merged
  [time omitted] (PR #16), Y [time omitted] (PR #15). `staging` = `2040f70` = base+X+Y (header "(G1 test 2)", 0.18).
  Stage PR #17 auto-opened.
- Custom promotion, **Prepare only WI-000009**: **no "Resolve Shared Components" dialog** (answers B3b: with one
  prepared WI, shared components with an unprepared WI in the same stage are not flagged). WI-000009 rebuilt on
  `main` as one commit `aed6a9b`, PR #18 `WI-000009 → main` opened [time omitted]. Content = base+Y (header, **0.15**), a
  version staging never had.
- `staging-provenance` run 41373223941: **FAILURE**: "DiscountCalculator.cls: this version never existed on staging
  (blob be7a3c1)". PR #18 `MERGEABLE` but `BLOCKED`.
- Promote WI-000009: *"We couldn't merge the changes because of branch protection rules in your source control
  repository. Review the pull request, resolve the issue, then try again."* `main` still `1cbe303`. release
  DiscountCalculator LastModifiedDate unchanged ([time omitted], Exp 02), still 0.15 and no header. **Blocked before deploy.**
- (Correction, Exp 05) The "sObject type 'DevopsRequestInfo' is not supported" error was my `-t` flag, which means
  `--use-tooling-api` in `sf data query`, not "table". Without it the query works. Exp 04's prepares and promotes are in the log.

- Variant: also **Prepare WI-000008** → rebuilt on main as `7e06e67 x`, PR #19 `WI-000008 → main` (main+X: old header,
  0.18). `staging-provenance` **SUCCESS** (correct: staging held main+X between the two merges). **No combine dialog**
  even with both prepared. Exp 01's work items changed the *same lines*; X and Y change different lines of the same
  file. Hypothesis: the "Resolve Shared Components" dialog appears only when the prepared branches conflict in Git,
  not whenever they share a component.
- Custom promotion of WI-000008 + WI-000009 together: same branch protection message. **All-or-nothing**: #19 (CLEAN)
  was not merged either; `main` still `1cbe303`, release unchanged.
- Limitation noted: the check evaluates each WI PR against the current `main`. In a sequential merge, #19 then #18 would
  produce main+X+Y (= staging), which is fine, but #18's check ran against the old base, so the bundle is blocked anyway.
  The way out is Promote Stage (#17).

- Recovery: cancelled the custom promotion and clicked **Promote Stage**. PR #17 `staging → main` check SUCCESS,
  merged [time omitted] → `main` = `6ca14eb`, tree == staging. release DiscountCalculator deployed [time omitted] (0.18 + "(G1 test 2)"
  header). DiscountCalculatorTest **not** redeployed (neither WI contained it).
- Leftovers: Lifecycle Center left the prepared PRs #18/#19 **open** and branches WI-000008/9 in place after the
  work items shipped via Promote Stage. Closed #18/#19 by hand.

**Result: G1 works.** Without it, Lifecycle Center would have silently shipped a never-staged version (no dialog, no
warning).
