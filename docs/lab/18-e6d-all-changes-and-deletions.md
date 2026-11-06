# Experiment 18: Does "All changes in the … stage branch" deploy deletions? (E6d)

## Question
Exp 17 showed that Promote Stage with "All changes in the Production stage branch" deploys the branch **contents**
and skipped a deletion that the default option sent (and failed on). So:
1. Does "All changes" ever deploy a **deletion**, even a real one that should reach Production?
2. Does the default "Only changes missing from Production" deploy that same deletion correctly?

## Design
- Ship WI-N2 (LabGadget + LabGadgetTest, pending from Exp 17) to Production with a normal Promote Stage, so
  Production has a component to delete.
- **WI-D** (dev): delete both classes in dev → commit → Staging.
- Promote Stage **validate-only** with "All changes", then read the validation deploy in release
  (`sf project deploy report`) to see whether it includes the deletes. Validate-only changes nothing.
- Real Promote Stage with the **default** option, so the deletion isn't left stranded in Production.

## Before snapshot
- Exp 17's after state: `main` = `f92ca45`, `staging` = `90cf167`, differing only by `LabGadget*` (WI-000042 pending).
  release has no LabGadget. Provenance check required on `main`.

## Steps / Actual
1. **Promote Stage** (default, LabGadgetTest), DORI-151 **SUCCESS**. `main` = `b5f36b4`, release has LabGadget +
   LabGadgetTest.
2. Deleted both classes from dev. **WI-D** = WI-000043 (dev): Change Management showed both as **Delete**. Commit
   `a32326a` (DORI-152), a plain Git delete. → Staging with LabPingTest (DORI-153): `staging` = `e7cac4f`, classes gone
   from staging.
3. **Promote Stage, Run validate-only deploy, "All changes in the Production stage branch"**, Run specified tests
   (LabPingTest, AccountSummaryTest, DiscountCalculatorTest). DORI-154 *"Validation completed successfully"*.
   release deploy `0Afg700000IPKxGCAX` (checkOnly): **6 components, all in the branch** (AccountSummary*,
   DiscountCalculator*, LabPing*), `deleted=false` on every one. **No delete for LabGadget.** release still had
   LabGadget, `main` unchanged.
4. **Promote Stage, Promote Now, default "Only changes missing from Production"**, LabPingTest. DORI-155 **SUCCESS**.
   release deploy `0Afg700000IPMz3CAH`: `LabGadget` and `LabGadgetTest` with **`deleted=true`**, nothing else.
   release no longer has LabGadget. `main` = `545c0ee`.

(Side note: while setting options, a keystroke landed on the pipeline page and opened **Edit Pipeline**. Cancelled
without saving. Lightning's `e` keyboard shortcut opens the record edit dialog.)

## After snapshot
- `main` = `545c0ee`, `staging` = `e7cac4f`, merge-base = `e7cac4f`: no content difference, shared history. No open PRs.
- release and staging: LabPing, LabPingTest (no LabGadget). dev: no LabGadget.
- WI-000043 CLOSED.

## Findings
1. **"All changes in the … stage branch" never deploys deletions.** It deploys every component in the branch
   as it is, with no `destructiveChanges.xml`. A component deleted from the branch is just absent from the deploy and
   **stays in Production**.
2. **The default "Only changes missing from Production" does deploy deletions**, built from the work items. That's why
   it failed in Exp 17 on a component Production never had.
3. Consequence: use the default option whenever a real deletion needs to ship. If "All changes" is used with a real
   deletion pending, the stage merge still happens, so `main` loses the files while Production keeps the component:
   silent org/branch drift. (*Inferred* from the validation content; not run for real, to avoid stranding a component
   in Production.)
4. Combined with Exp 17: a **revert by deletion** (component never shipped) needs "All changes"; a **real deletion**
   needs the default. They can't go out in the same Promote Stage. Ship one, then the other.
