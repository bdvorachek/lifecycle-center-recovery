# Experiment 03: Does a GitHub gate stop a Lifecycle Center promotion? (E5)

## Why
All mitigations for "untested code reaches Production" (e.g. a check that `main`'s new content already existed on
`staging`) depend on Lifecycle Center respecting GitHub branch protection. Lifecycle Center merges PRs as the
connected GitHub user (here: the repo owner/admin), so admin bypass matters.

## Setup (2026-11-01)
- Private GitHub repository with branch protection available.
- Before: `main` = `022b191`, `staging` = `a7ff1b4`, no content diff, no open PRs. WI-000001..5 CLOSED/COMBINED.
  Last DevopsRequestInfo = DORI-18.
- Branch protection on `main` (API PUT): required status check **`lab-gate`** (strict=false), **enforce_admins=true**,
  no required reviews. Nothing posts `lab-gate`, so it's missing unless we post it by hand.
- Out-of-band: deployed `LabPing` → `'pong v2'` (+ test) to **dev** (1/1 pass).

## Steps
1. Lifecycle Center: WI-000006 in `dev`, pull changes (LabPing + LabPingTest), commit, promote to Staging
   (`staging` is unprotected → should be normal).
2. Post a **failing** `lab-gate` status on the stage PR's head commit (`gh api repos/.../statuses/<sha> -f state=failure`).
3. Promote Stage.
4. Variants: (a) status missing instead of failing; (b) status `success` → promotion should go through.

## Hypotheses
- H1: Lifecycle Center's merge API call is rejected (405 "Required status check is failing"), so the promotion fails cleanly.
- H2: Because Lifecycle Center deploys **before** merging (Exp 02), Production may get the deploy even though the merge is
  refused → org ahead of `main`. This is the key thing to check.
- H3: Lifecycle Center checks mergeability first and refuses without deploying (like the merge-conflict popup).

## Actual
- Step 1: WI-000006 "Pong", commit `130d131` (LabPing + Test only). DORI-19 COMMIT [time omitted]. PR #11 opened [time omitted] (when
  Promote Selected was started), DORI-20 PROMOTE [time omitted]–[time omitted], staging deployed [time omitted], PR #11 merged
  [time omitted] → `staging` = `c592ddc`.
- **New finding:** Lifecycle Center opened the stage PR #12 `Promotion: staging → main` at **[time omitted], 1 second after**
  the work item merged into Staging, without anyone clicking Promote Stage. → Stage PRs are pre-created whenever a
  stage gets new content. (Probably how stale PR #5 came about.)
- Step 2: posted `lab-gate` = failure on `c592ddc` at [time omitted]. GitHub: PR #12 `MERGEABLE` but `BLOCKED`.
- Step 3 (Promote Stage): error **"We couldn't merge the changes because of branch protection rules in your source
  control repository. Review the pull request, resolve the issue, then try again."**
- After: **no DevopsRequestInfo** created, `main` still `022b191`, PR #12 OPEN/BLOCKED (no comments),
  WI-000006 still PROMOTED, **Production LabPing unchanged** (`'pong'`, [time omitted]).
- **H1/H3 confirmed, H2 refuted:** Lifecycle Center checks the PR's merge state (incl. branch protection) **before** it
  deploys. The gate protects the org too, not just the branch. Fails cleanly; nothing to clean up.
  The message names branch protection (unlike the merge-conflict popup, which names nothing).
- Variant (b): set `lab-gate` = success on `c592ddc`  → PR #12 `CLEAN`. Promote Stage again: **success, no
  cached failure** (re-checks each click). DORI-21 PROMOTE [time omitted]–[time omitted]. Production LabPing deployed [time omitted] →
  `'pong v2'`. PR #12 merged [time omitted] → `main` = `c788e7f`. `git diff origin/main origin/staging` empty.
  WI-000006 CLOSED. DiscountCalculator **not** redeployed (only the promoted work item's components).
- Variant (a) (status missing instead of failing) not run yet. Expected the same block, since GitHub treats a missing
  required check as not passing.

## Findings
1. Lifecycle Center **respects branch protection, including enforce_admins**, even though it merges as an admin.
2. The check happens **before the deploy**. A failing gate leaves the org, branch, PR and work item untouched.
3. Error text names the cause: "We couldn't merge the changes because of branch protection rules in your source
   control repository. Review the pull request, resolve the issue, then try again."
4. After the gate passes, clicking again works. The result isn't cached.
5. The stage PR is opened automatically ~1s after a work item merges into the stage, before anyone clicks Promote Stage.
   So a CI check on `main` PRs starts running as soon as Staging changes, and has time to finish before someone promotes.

## So what
A required GitHub check on `main` is a working, clean gate for Lifecycle Center promotions. That makes CI-based
mitigations practical, e.g. a check that fails if the PR's resulting content for any file never existed on `staging`
(catches the combine problem from Exp 01), or a test-run check.

## Cleanup / state after
Protection on `main` (required `lab-gate`, enforce_admins) **left in place**. Every future promotion to Production needs
`lab-gate` = success posted on the stage PR head:
`gh api -X POST repos/<owner>/<repo>/statuses/<sha> -f state=success -f context=lab-gate`
(or remove: `gh api -X DELETE repos/<owner>/<repo>/branches/main/protection`).
