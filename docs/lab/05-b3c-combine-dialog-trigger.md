# Experiment 05: What triggers the combine dialog (B3c)

## Question
Exp 01 (same-line conflict, both prepared) showed "Resolve Shared Components". Exp 04 (same file, different lines,
1 or 2 prepared) showed nothing. Hypothesis: the dialog keys on a **Git conflict between prepared branches**.

## Design
Sequential edits to the same line, so both reach Staging cleanly without any manual resolution:
- WI-A (dev): DiscountCalculator line 15 `GOLD_RATE` 0.08 → **0.09**. Promote to Staging.
- WI-B (dev2): starts from Staging's version *with A* and changes line 15 0.09 → **0.10**. Its branch is cut from
  staging (which already has A), so the promotion to Staging is clean.
- `GOLD_RATE` is not asserted by any test.

Then custom promotion from Staging:
1. **Prepare only WI-B.** Rebasing B's own commit (0.09 → 0.10) onto `main` (0.08) is a rebase **conflict**. Watch:
   dialog? Prepare ERROR? Or the result: does it keep B's line (0.10, as in Exp 01's "newest wins")?
2. **Also prepare WI-A.** Prepared A (0.09) and prepared B both change line 15 from main → conflict between
   prepared branches. Prediction: **dialog appears here**.
3. Don't promote. Cancel and **Promote Stage** (main gets 0.10 = staging).

## Setup (2026-11-02 UTC, CLI)
- Package A deployed to dev: staging's DiscountCalculator with GOLD_RATE 0.09 (tests 4/4 pass).

- WI-000010 "b3c WI-A" (dev): commit `121002a` took ~1 min on "Committing changes…" but succeeded (only line 15).
  The in-org panel then showed **"Review Created" linked to an old PR** (stale UI from the previous dev work item). WI record had
  `ReviewRemoteReference` = null, status IN_PROGRESS. A hard refresh fixed it. Review → PR #21, merged to staging
  2026-11-03 [time omitted] → `staging` = `7e9b5fa` (GOLD 0.09). Stage PR #22 auto-opened.

### Accidental D6: committing from a stale dev org
- Before I'd deployed B, WI-000011 "b3c WI-B" was created in dev2 and committed. dev2 still held Exp 04's Y version
  (main+Y, PLATINUM **0.15**). Commit `070bd54` therefore **reverts X's PLATINUM 0.18 → 0.15**. PR #20 to staging is
  `MERGEABLE/CLEAN`. Lifecycle Center would have merged it and undone a change already in Production, with no warning.
- WI-000011 is set aside (not promoted). Its branch is cut from staging before A, so reusing it would make B's net change
  0.08 → 0.10 against staging's 0.09, an Exp 01-style conflict. WI-B is redone as a fresh work item.
- Package B deployed to dev2: staging's current file (A, header, 0.18) with GOLD_RATE 0.10. Tests 4/4.

## Actual
- WI-000011 set to **Never** → status `NEVERED`. Lifecycle Center **closed PR #20**  and **deleted branch WI-000011**.
- WI-000012 "Base 0.10" (dev2, `02c9145`, cut from staging after A) → PR #23 merged [time omitted]. `staging` = `6209f4e`:
  versions 0.08 → 0.09 (A) → 0.10 (B).
- **Prepare WI-000012 only**: DORI-37 `REBASE` SUCCESS [time omitted]. **No dialog, no error**, even though replaying B's commit
  (0.09→0.10) onto main (0.08) is a textual conflict. Result `a1049d0`: 0.08 → **0.10**, no markers. The rebase took
  the work item's own lines. PR #24 `WI-000012 → main`, check pass (= staging tip).
- **Prepare WI-000010 too**: DORI-38 `REBASE` SUCCESS [time omitted], `12a48c2` 0.08 → 0.09, PR #25, check pass. **Still no
  dialog**, although the two prepared branches conflict (`git merge-tree` → conflict).
- **Click Promote** with both selected → **"Resolve Shared Components" dialog**: "These work items share components, which
  can cause merge conflicts or promotion failure." WI-000010, WI-000012 / DiscountCalculator:ApexClass. Options:
  "Combine work items into **WI-000012**" (default) / "Continue with custom promotion".
  → The dialog belongs to **Promote**, not Prepare. Survivor WI-000012 was **prepared first**, so prepare order does not
  pick the survivor (B7 narrowed: number / commit time / staging arrival still confounded).
  Exp 04's both-prepared Promote gave the branch protection error instead. Unclear whether that's because there was
  no line conflict there, or because the failing check is evaluated before the dialog.
- **Combine**: DORI-39 `REBASE_AND_COMBINE` SUCCESS [time omitted] ("Prepare branch with rebase and combine completed
  successfully."). WI-000012 rebuilt from main: `75bf79c b3c WI-A`, `3c55897 Base 0.10` (re-authored DevOps Center),
  0.08 → **0.10**. PRs #24 and #25 closed, **#26** `WI-000012 → main` opened. Branch WI-000010 deleted, WI-000010
  `COMBINED`. Combined tree == staging (force-app), check **pass**. Stage PR #22 left open.
  → With no manual resolution, a combine of sequential same-line edits reproduces Staging exactly (B1 counterpart).
- **Promote WI-000012**: DORI-40 `PROMOTE` SUCCESS [time omitted], release DiscountCalculator deployed [time omitted] (GOLD 0.10),
  PR #26 merged [time omitted] → `main` = `db7bc26`. WI-000012 `CLOSED`.
- After: `main` and `staging` **identical content**, different history (staging keeps A/B's original commits).
  `git merge-tree main staging` **clean**, so **no stuck stage**, unlike Exp 01. Stage PR #22 stays OPEN listing
  DiscountCalculator (a no-op merge). It will ride along with the next Promote Stage.

## Findings
1. The "Resolve Shared Components" dialog is shown when you click **Promote** on prepared work items, not during Prepare.
2. **Prepare never fails on a rebase conflict.** It silently keeps the work item's own lines (B: 0.10 over main's 0.08).
3. The survivor isn't the first-prepared work item (WI-000012 was prepared first and survived). Still consistent with
   higher number / later commit / later staging arrival (B7).
4. A combine with **no manual resolution** reproduces Staging's version and leaves `main`/`staging` mergeable. The Exp 01
   damage came from the hand resolution that combine threw away, not from combining as such.
5. "Never" on a work item closes its PR and deletes its branch.
6. Committing from a dev org that's behind the pipeline silently reverts shipped changes (accidental D6, WI-000011).
7. In-org Change Management can show a stale "Review Created" link from the previous work item. A hard refresh fixes it.
