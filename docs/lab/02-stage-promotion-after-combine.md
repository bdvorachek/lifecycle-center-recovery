# Experiment 02: Stage promotion after a combine (A2) and reconciling Staging/Production (A3)

## Setup / before snapshot
- `main` = `f19b10f` (Production: GOLD 0.08 / MAX 2000). `staging` = `901fc39` (GOLD 0.12 / MAX 3000).
- `git diff origin/main origin/staging`: only DiscountCalculator.cls (2 lines) + DiscountCalculatorTest.cls (1 line).
- Merge-base of main/staging = `7c6b185` (before the combine). A local `git merge origin/staging` into `main`
  **conflicts** in DiscountCalculator.cls and DiscountCalculatorTest.cls.
- PR #5 `Promotion: staging → main`: OPEN, `mergeable=CONFLICTING`, head `901fc39`.
- WorkItems: WI-000001 CLOSED, WI-000002 COMBINED, WI-000003 CLOSED.
- Org values (Tooling API body): dev 0.12/3000, dev2 0.08/2000, staging 0.12/3000, release 0.08/2000.
- release DiscountCalculator LastModifiedDate = 2026-11-01 [time omitted]. Not a delayed deploy: PR #8 was *created* [time omitted]
  but *merged* [time omitted] (`gh pr list` shows created date). DORI-000000013 PROMOTE [time omitted] → [time omitted] SUCCESS.
  Deploy happened ~4s before the merge timestamp → Lifecycle Center deploys, then merges (or both near-simultaneously).

## A2: Unrelated work item, then Promote Stage

### Hypothesis
The new work item only adds `LabPing`, but the `staging → main` merge will still conflict on DiscountCalculator,
because `staging` and `main` were split apart by the combine (case C).

### Steps
1. Out-of-band setup (CLI): deployed new `LabPing` + `LabPingTest` classes to **dev** (2026-11-01).
2. In Lifecycle Center: new work item in `dev`, pull changes, commit LabPing/LabPingTest only.
3. Promote the work item to Staging.
4. Promote Stage (Staging → Production).

### Actual
- Steps 2–3 (WI-000004 "LabPing Dev"): commit `4fe3960` contained **only** LabPing/LabPingTest (DiscountCalculator not
  picked up, as expected since dev = staging). DORI-14 COMMIT [time omitted], PR #9 opened [time omitted], DORI-15 PROMOTE [time omitted],
  PR #9 merged [time omitted] → `staging` = `b1f46aa`. staging got LabPing at [time omitted] (again deploy ≈ 4s before merge).
  WI-000004 status = PROMOTED.
- Stale PR #5 updated automatically (head = `b1f46aa`, 7 commits) and is still **CONFLICTING**. No new PR.
- Pipeline view before step 4: WI-000004 in Staging, **Promote Stage button enabled, no conflict warning** even though
  PR #5 has been CONFLICTING since A1. Production "Latest Promotions" lists WI-000003 and WI-000001 only;
  WI-000002 (combined into WI-000003) is not shown.
- Step 4 (Promote Stage): **popup reporting a merge conflict.** Hypothesis confirmed: an unrelated work item can't
  promote, because `staging` and `main` were split by the combine.
- No back-end trace: no new DevopsRequestInfo after DORI-15, `main` still `f19b10f`, no new PR (PR #5 reused/untouched),
  no PR comments, LabPing not in release. → Conflict check runs before a request is created; nothing to clean up.
- Popup text: **"Cannot initiate promotion due to merge conflicts."** No work item and no file named.
  Only option: **"Resolve using Agentforce"** (AI + git conflict resolution in Salesforce's platform; Agentforce Vibes
  org not set up, so not usable here). No combine offered at the stage level.
- The files are only visible in GitHub PR #5: "This branch has conflicts that must be resolved":
  DiscountCalculator.cls, DiscountCalculatorTest.cls. PR #5 lists 7 commits: the pre-combine originals (07fcd55,
  658b910, af85dd5, b76c4c8, 901fc39) + 4fe3960/b1f46aa added "35 minutes ago" by DevOps Center. Files changed: 2 (+18 −5).
  → Lifecycle Center reuses the stale stage PR and appends to it; the combine's rewritten history never reached `staging`.

### Takeaway
After a combine, **every** future stage promotion is blocked until Staging and Production are reconciled, no matter
what the new work items touch. The pipeline view gives no warning until you click Promote Stage.

## A3: Reconcile

### Local simulation (before running it in Lifecycle Center)
Merge-base 7c6b185 has GOLD 0.10 / MAX 2500 (test asserts 2500). A new WI branch cut from `staging`, merged into
`staging`, then `staging → main`:
- WI sets **Production's values (0.08/2000 + matching test)** → **CLEAN**, and resulting `main` == `staging`.
  Git treats identical changes on both sides as no conflict.
- WI keeps **0.12/3000** (any other touch of the class) → **still CONFLICTS** on both files.

So path (a) can only clear the conflict by making Staging match Production. To ship 0.12/3000 the Lifecycle
Center way, first reconcile to 0.08/2000 (WI-A), promote the stage, then change it to 0.12/3000 (WI-B) on a clean history.
Path (b) (git merge outside Lifecycle Center) can pick either value directly.

### A3(a): Reconcile to Production's values via a work item
Steps:
1. Out-of-band setup (CLI, 2026-11-01): deployed `origin/main`'s DiscountCalculator.cls + DiscountCalculatorTest.cls to
   **dev** (`--ignore-conflicts`, RunSpecifiedTests: 4/4 pass). dev now 0.08/2000.
2. In Lifecycle Center: new work item in `dev`, pull changes, commit only DiscountCalculator + Test.
3. Promote the work item to Staging (expect a clean merge: staging → 0.08/2000, staging redeployed).
4. Promote Stage (prediction: no conflict; PR #5 merges; `main` == `staging`; Production gets LabPing).

Actual:
- Steps 2–3: WI-000005 "Reconcile", commit `a8a6bc6` = only DiscountCalculator.cls (2 lines) + Test (1 line).
  PR #10 merged → `staging` = `a7ff1b4`. `git diff origin/main origin/staging` = LabPing files only.
- PR #5 auto-updated to `a7ff1b4`; GitHub mergeability went UNKNOWN → **CLEAN / MERGEABLE**. Local merge sim: clean.
  Prediction confirmed on the git side.
- Pipeline view after step 3 **still showed** "We couldn't validate the promotion due to merge conflicts" +
  "Resolve Using Agentforce" under Promote Stage, even though git was already clean.
  → Banner is a cached result from the last Promote Stage click; not re-evaluated when new work items arrive.
- Step 4 (Promote Stage): **success**, no popup. DORI-18 PROMOTE [time omitted] → [time omitted]. PR #5 (stale since [time omitted], created
  by the first stage promotion attempt) **merged** at [time omitted] → `main` = `022b191` "Merge branch 'staging'".
  `git diff origin/main origin/staging` = **empty**. WI-000004 and WI-000005 → CLOSED.
- After snapshot:

  | Org | DiscountCalculator | LabPing |
  |---|---|---|
  | dev | 0.08/2000 ([time omitted], our CLI deploy) | yes |
  | dev2 | 0.08/2000 ([time omitted], untouched) | no (never promoted to dev envs) |
  | staging | 0.08/2000 ([time omitted], WI-000005 promote) | yes |
  | release | 0.08/2000 (**[time omitted], redeployed**) | yes  |

- release's DiscountCalculator was redeployed even though its content didn't change: the stage promotion deploys
  every component changed in the promoted work items, not a diff against the target org.
- Deploy again finished ~5s before the git merge ([time omitted] vs [time omitted]).

### Recovery summary
Path (a) cleared the stuck pipeline with no git surgery, but only by **giving up Staging's tested values** and
accepting the untested combine result (0.08/2000). Going back to 0.12/3000 now is a normal work item on a clean history.
Path (b) (git merge outside Lifecycle Center) is still untested; run it as a separate drill later.

## Findings
1. After a combine, `staging` and `main` diverge on the combined lines. **Every** later Promote Stage is blocked,
   including work items that don't touch those files.
2. Popup: "Cannot initiate promotion due to merge conflicts." No files or work items named. Only option: Resolve Using
   Agentforce. Files are only visible in the stale GitHub stage PR.
3. The pipeline view gives no warning before you click. After a click, the "couldn't validate … merge conflicts" banner
   is cached and stays even after the conflict is fixed in git; clicking Promote Stage again re-checks.
4. Lifecycle Center reuses the open `staging → main` PR (#5) for every later stage promotion and appends new commits to it.
5. Fix the Lifecycle Center way = a work item that makes Staging's lines **identical to Production's**; git then merges
   cleanly. A work item that changes the lines to anything else keeps the conflict.
6. Lifecycle Center deploys before it merges (deploy ~4–5s before the merge timestamp, every time).
7. Production's "Latest Promotions" never lists WI-000002 (COMBINED), though its changes shipped inside WI-000003.
