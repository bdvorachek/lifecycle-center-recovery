# Experiment 07: Get out of a work item vs stage conflict without Git (B8)

## Question
Exp 01's "work item PR conflicts with its stage branch" is the only **Git required** case in the guide
(`site/docs/conflicts/when-you-need-git.md`). Can it be fixed inside Lifecycle Center by setting the conflicting
work item to **Never** and redoing the change as a new work item?

Sub-questions:
- What exactly does Lifecycle Center show when the single-WI promotion conflicts (message, request log, PR)?
- Does Lifecycle Center offer any way to bring a dev org up to date with Staging (a "sync" option)? If not, how
  does a developer get Staging's version into the dev org without Git or the CLI?
- What does a **naive** redo commit (from a dev org that's behind)?

## Design
Two developers start from the same Staging version (SILVER_THRESHOLD 1000, GOLD_RATE 0.11):
- **WI-X** (dev): SILVER_THRESHOLD 1000 → **900** (line 9) and GOLD_RATE 0.11 → **0.12** (line 15).
- **WI-Y** (dev2): GOLD_RATE 0.11 → **0.13** (line 15).
- Intended final result: X's threshold **900** + Y's GOLD **0.13**.

X reaches Staging first. Y's branch was cut before that, so Y's PR conflicts on line 15.

Local simulation (worktree, 2026-11-03):
- `Y → staging` after X: **CONFLICT** (line 15).
- Naive redo (new WI from dev2 as it is): diff vs staging = GOLD 0.12 → 0.13 **and SILVER_THRESHOLD 900 → 1000**.
  It would silently revert X's threshold (a D6-style revert). PR would be clean.
- Correct redo (dev2 first gets Staging's file, then 0.13): diff = GOLD line only.

## Before snapshot
- `main` = `a0aeda8`, `staging` = `36827d2`, no content diff, merge-base = staging tip. No open PRs.
- WorkItems: 001–013 all CLOSED / COMBINED / NEVERED (011). Latest DORI-43.
- DiscountCalculator: staging and release = threshold 1000 / GOLD 0.11.
- Setup deploys (CLI, tests 4/4):
  - dev [time omitted] = staging + X (900 / 0.12).
  - dev2 [time omitted] = staging + Y (1000 / 0.13). DiscountCalculatorTest also redeployed (same as staging's).

## Steps
1. (LC) In **dev**: new work item "b8 X", Pull changes, commit **DiscountCalculator only**.
2. (LC) In **dev2**: new work item "b8 Y", Pull changes, commit **DiscountCalculator only**.
   Both commits must happen **before** X is promoted, so Y's branch is cut from the old Staging.
3. (LC) Promote **WI-X alone** to Staging. Expect clean.
4. (LC) Promote **WI-Y alone** to Staging. Expect a failure (Exp 01: "Promotion failed", `ERROR` request, PR conflicts).
   Record the exact message and options.
5. (LC) Look for a Lifecycle Center-only way to update dev2 from Staging (environment sync / refresh / "pull from
   pipeline"). Note what exists.
6. (LC) Set WI-Y to **Never**. Expect: PR closed, branch deleted (Exp 05).
7. Redo, in two variants:
   - **7a (naive):** new work item in dev2 as it is, Pull changes, **stop before committing**. Look at what the
     diff shows (does the UI show the threshold revert?).
   - **7b (correct):** bring dev2 up to Staging's version (with the step 5 option if there is one, otherwise CLI
     deploy, and note that this is outside Lifecycle Center), re-apply GOLD 0.13, then commit and promote.
8. Check: `staging` = 900 / 0.13, no Git used. Then Promote Stage.

## Actual
Lifecycle Center UI steps were automated in Chrome from here on.

- How the UI works (dev org side): the top bar has a **work item selector** (Select / Create Work Item / Open in Lifecycle
  Center). **Change Management** opens from the ☰ icon. After a commit, the top bar shows **Create Review** → opens
  the `WI → staging` PR. Dev Hub WI page then offers **Mark as Ready to Promote** (= approval).
- Commit dialog says *"The branch is created after your first successful commit."* So the WI branch is cut from the stage
  branch at **first commit**, not at work item creation.
- Step 1: WI-000014 "b8 X" (dev). Change Management (default filter) listed DiscountCalculator. Commit `6021ae9`, parent
  `36827d2`. Diff = threshold 900 + GOLD 0.12. ✔
- Step 2: WI-000015 "b8 Y" (dev2). **DiscountCalculator was hidden** under the default "Show Uncommitted Changes"
  (dev2 had committed it before, WI-000012), although I'd deployed a change to it. Shown only with **Show All
  Changes** (F1 again). Commit `a6b7cf9`, parent `36827d2`. Diff = GOLD 0.13 only. ✔
- Reviews created for both (PR #29 X, PR #30 Y). X marked ready, promoted alone (Promotion Options defaults: "Only
  changes missing from Staging (recommended)", No tests). DORI-46 SUCCESS, PR #29 merged [time omitted] → `staging` =
  `df4db29`, staging [time omitted] = 900 / 0.12. Stage PR #31 opened.
- PR #30 (Y) → **CONFLICTING / DIRTY**. The WI-000015 record page showed **no warning**, and **Mark as Ready to
  Promote was allowed**.
- Step 4: Promote Selected (Y only) → blocked **before** the Promotion Options dialog:
  dialog **"Can't validate promotion"**: *"Cannot initiate the promotion due to merge conflicts"* / *"Resolve the merge
  conflict, using the Agentforce, then try the promotion again"*. Buttons: Close / Resolve using Agentforce. The Approved
  column then shows "1 work item requires attention" and a cached "We couldn't validate the promotion due to merge
  conflicts" banner on the card.
  **No DevopsRequestInfo record** (latest is still DORI-46), staging unchanged, PR #30 still open. Differs from Exp 01,
  which left an `ERROR` "Promotion failed" record. The pre-check now happens before a request is created.
- Step 5: **there is a sync feature.** Approved Work Items → "2 Development Environments · **View**" opens **Back Sync
  Options**: *"Select a development environment to sync with the latest changes from the Staging stage to avoid future
  conflicts."* Columns: Environment Name, Org Type (both SANDBOX), URL, **Sync Status**. Both dev and dev2 show
  **"Not in Sync"**, even though dev's content equals Staging. Button: Sync Options… (enabled after selecting a row).
  Not used yet. The dev org panel itself has no sync option (its menu only offers "Remove Lifecycle Center Connection").
- **Back Sync dev2 with WI-000015 still open** (before: dev2 1000 / 0.13 at [time omitted], WI-000015 = `a6b7cf9`).
  Second screen: *"Pull the latest changes from the Staging stage into dev2."* Test Options (Default / local / all /
  specified). Changes to Sync: **"Sync only work item changes missing from dev2. Deselect items to exclude them."**
  (default) or "Sync all changes from the Staging stage". Work Items to Sync = the 10 WIs that came from **dev**
  (1, 2, 4, 5, 6, 7, 8, 10, 13, 14). Everything from dev2 (3, 9, 11, 12, 15) is excluded, so "missing" is decided
  per work item (by origin), not by content.
  Clicked Sync → **"Can't back sync"**: *"The dev2 environment has work items that are in the In Progress, In Review,
  or Ready to Promote states. Promote them, then try again."* Nothing changed: no request record, dev2 and
  WI-000015 untouched.
  → **Catch-22:** the conflicting WI can't be promoted, and the org can't be synced while that WI is open. Back Sync
  only works once the dev org has no open work items. So it can't fix an open conflict directly; at best it helps
  **after Never** (or prevents the conflict if run before starting the work).
- **Never WI-000015** (Dev Hub WI page → status menu, which now also offered "Move back to In Review"). The approval stamp
  had advanced by 16 minutes around the refused sync (unexplained). Confirm text: *"WI-000015 becomes inactive
  and its committed metadata and data return to the list of available changes. You can't undo this action."* →
  `NEVERED`, PR #30 closed [time omitted], branch WI-000015 deleted (as in Exp 05).
- **Back Sync dev2** (same defaults, same 10 dev-origin WIs): accepted. "Back sync of dev2 in progress" on the
  Approved column. DORI-47 SUCCESS [time omitted]. dev2 at [time omitted]: DiscountCalculator = **900 / 0.12** (Y's 0.13
  **overwritten without warning**), DiscountCalculatorTest redeployed, **LabPing deployed** (never in dev2 before).
  No Git changes (`staging` still `df4db29`).
- Re-applied the change (CLI deploy, standing in for the developer's edit): staging's file + GOLD 0.13. Tests 4/4.
- New work item: with no active WI, the dev org top bar shows no selector, and the commit dialog lists nothing until a WI
  exists. Created WI-000016 "b8 Y redo" from the Dev Hub (Work Items → New, environment dev2).
- Change Management again hid DiscountCalculator under the default filter. "Show All Changes" listed it, plus
  **LabPing / LabPingTest as "Modify"** (from the sync). Easy to commit by accident.
- Commit `4863c1c` (parent `df4db29`): diff vs staging = **GOLD 0.12 → 0.13 only**. The branch appeared at staging's tip
  first and the commit was pushed ~1 min later. PR #32 MERGEABLE. Approved, promoted: Promotion Options dialog shown (no
  conflict pre-check failure). DORI-49 SUCCESS [time omitted] → `staging` = `884729e`, staging [time omitted] = **900 / 0.13**.
  WI-000014 and WI-000016 PROMOTED. Stage PR #31 MERGEABLE, `staging-provenance` pass.
- Step 8 (Promote Stage to release): completed manually by the operator.
  DORI-50 SUCCESS [time omitted], release DiscountCalculator deployed [time omitted] (900 / 0.13), PR #31 merged [time omitted] →
  `main` = `abaa99c`. WI-000014/16 `CLOSED`.

## After snapshot
- `main` = `abaa99c`, `staging` = `884729e`, **no content diff**, merge-base = staging tip. No open PRs.
- DiscountCalculator: staging and release = 900 / 0.13. dev2 = 900 / 0.13 ([time omitted], our redo deploy).
  **dev = 900 / 0.12 (behind).** Back Sync it before its next work item.
- WorkItems: 014 CLOSED, 015 NEVERED, 016 CLOSED. Latest request DORI-50.

## Findings
1. **A work item vs stage conflict can be fixed without Git**: Never → Back Sync the dev org → redo the edit → new work
   item. The result was exactly the intended version (X's 900 + Y's 0.13), with a clean PR.
2. **The developer has to redo their edit.** Back Sync overwrites the dev org with Staging's version, so the conflicting
   change is lost from the org, and Never deletes its branch. Fine for one line, costly for real work. (The old commit
   only survives in local clones and the closed PR.)
3. **Back Sync is refused while the dev org has open work items** (In Progress / In Review / Ready to Promote). It can't
   rescue an open conflicting work item, only follow a Never. Hypothesis: run before starting work, it prevents the
   conflict.
4. Back Sync picks **work items by origin** ("missing from <env>"), deploys all their components (LabPing arrived in
   dev2), and those components then show as changes in Change Management.
5. The conflict shows up only when you click Promote: no warning on the work item, approval allowed. The pre-check
   creates **no request record** (Exp 01's `ERROR` record isn't produced any more).
6. The default "Show Uncommitted Changes" filter hid DiscountCalculator in dev2 **twice** (before and after the sync).
7. A work item branch is created from the stage branch at **first commit**, not when the work item is created.
