# Experiment 17: Revert route when the pending work item added a component (E6c)

## Question
Exp 16's revert route takes unwanted work out of Staging with a new work item that commits Production's version of
each file. If the unwanted work item **added** a component, there is no Production version to commit: the revert
has to be a **deletion**.
1. Does Change Management in Lifecycle Center show a component deleted in the dev org, and can it be committed?
2. Does promoting that work item to Staging delete the component from the Staging org (destructive deploy), or only
   from the branch?
3. Does Promote Stage then ship the wanted work and leave Production without the component?
4. Can the added component be redone afterwards as a new work item?

## Design
- **Wanted work:** WI-P2 (WI-000039, LabPing comment) is already pending in Staging from Exp 16. This time it should ship.
- **WI-N** (dev): adds a new class `LabGadget` + `LabGadgetTest`. → Staging with tests. N must not reach Production.
- **WI-RN** (dev): delete both classes from dev, then look for the deletion in Change Management. Commit →
  Staging. Check `staging` (files gone?) and staging (classes gone?).
- **Promote Stage** with Run specified tests (LabPingTest). Expect: release LabPing = P2's, no LabGadget.
- **WI-N2** (dev): re-add `LabGadget` → Staging. Staging ends with N pending again.
- Fallback if Lifecycle Center can't commit a deletion: record it, and that this case needs Git (`git rm` on a work item
  branch) or an out-of-band destructive deploy to the Staging org.

## Before snapshot
- `main` = `d9e3251`, `staging` = `7c18946` (Exp 16's after state): differ only in LabPing (WI-P2 = WI-000039 pending).
  Merge-base `36cccb2`, stage PR #81 open and mergeable. No `LabGadget*` in dev, staging or release.
  Provenance check required on `main` throughout.

## Steps / Actual
Lifecycle Center UI steps were automated in Chrome. Dev org changes made with `sf project deploy start` /
`sf project delete source` against dev (stand-ins for a developer editing in the org).

### Setup
1. Deployed `LabGadget` + `LabGadgetTest` (new) to dev. **WI-N** = WI-000040 (dev). Change Management listed both
   classes as **Modify** (not "Add"). Commit `4f7fa08` (DORI-142) → Staging with LabGadgetTest (DORI-143),
   `staging` = `cfbcc27`. staging has both classes. Staging = P2 (wanted) + N (unwanted, new component).

### The revert (a deletion)
2. Deleted both classes from dev (`sf project delete source`). **WI-RN** = WI-000041 (dev): Change Management listed
   both with Operation **Delete**; the commit preview showed `delete`. Commit `311c49f` (DORI-144): a plain Git
   deletion of the 4 files (no `destructiveChanges.xml` in the repo).
3. RN → Staging with LabPingTest (DORI-145) **SUCCESS**: `staging` = `37b8436`, files gone from the branch, and the
   classes **deleted from staging** (Lifecycle Center ran a destructive deploy). `git diff main staging` = LabPing only.

### Promote Stage
4. **Promote Stage**, default "Only changes missing from Production", Run specified tests (LabPingTest).
   DORI-146 **ERROR** `DEPLOYMENT_FAILURE`: *"destructiveChanges.xml: No ApexClass named: LabGadget found"* (and
   LabGadgetTest). Lifecycle Center built the deploy from the **work items** (N adds, RN deletes) and sent RN's
   deletion to Production, where the classes never existed. Nothing deployed, `main` unchanged, stage PR #81 still
   open, all three WIs still PROMOTED in Staging. Pipeline card: *"We couldn't deploy your work items"* +
   **Resolve Using Agentforce**.
5. Retry with **"All changes in the Production stage branch"**, LabPingTest only. DORI-147 **ERROR**: *"Code Coverage:
   Test coverage of selected Apex Class is 0%"* (twice). The destructive error is gone: this option deploys the
   branch's **contents** (every class in it), so AccountSummary and DiscountCalculator needed their tests too.
6. Retry, "All changes", Run specified tests **LabPingTest, AccountSummaryTest, DiscountCalculatorTest**. DORI-148
   **SUCCESS**. `main` = `f92ca45` (merge of `staging`). release: LabPing = P2's comment, **no LabGadget**.
   WI-000039 (P2), WI-000040 (N) and WI-000041 (RN) all **CLOSED**. Stage PR merged.

### Redo N
7. Re-deployed `LabGadget*` to dev. **WI-N2** = WI-000042 (dev): listed as Modify again; commit `1939598`
   (DORI-149), a plain re-add → Staging with LabGadgetTest (DORI-150). `staging` = `90cf167`, staging has both
   classes again.

## After snapshot
- `main` = `f92ca45`, `staging` = `90cf167`, merge-base `37b8436` (shared history). `git diff main staging` =
  the 4 `LabGadget*` files only (N2 pending). Stage PR #85 open, MERGEABLE.
- staging: LabPing (P2), LabPingTest, LabGadget, LabGadgetTest. release: LabPing (P2), LabPingTest; no LabGadget.
- dev: has LabGadget*. WI-000039/40/41 CLOSED, WI-000042 PROMOTED.

```
*   90cf167 Merge branch 'WI-000042' into staging     (N2: re-add)
*   37b8436 Merge branch 'WI-000041' into staging     (RN: delete)   <- main f92ca45 merged this
*   cfbcc27 Merge branch 'WI-000040' into staging     (N: add)
*   7c18946 Merge branch 'WI-000039' into staging     (P2)
```

## Findings
1. **Lifecycle Center can commit and promote a deletion.** Delete the component in the dev org; Change Management
   lists it as **Delete**; the commit is a plain Git delete; promoting to Staging runs a destructive deploy and the
   component disappears from the Staging org. (New components, by contrast, show as **Modify**, not Add.)
2. **But the default Promote Stage then fails.** "Only changes missing from Production" builds the deployment from the
   work items, including a `destructiveChanges.xml` for the revert's deletion. The component never reached
   Production, so the deploy fails: *"No ApexClass named: … found"*. Nothing is deployed and nothing merges; the error
   is retryable.
3. **Way out, Lifecycle Center only: Promote Stage with "All changes in the Production stage branch".** That option
   deploys the branch contents (no destructive changes), so the never-shipped component is simply absent. Cost: it
   redeploys **every** component in the branch, so "Run specified tests" must cover all Apex in the branch (or use
   Run local tests). In a real project that's a full-size deployment.
4. **The rest of the revert route behaves as in Exp 16:** Production never gets N or a broken version; N, RN and P2 all
   show **Closed**; the redo (N2) is an ordinary new work item and history stays shared.
5. **Not Git required.** No Git was needed at any point. (*Hypothesis:* removing the files with a direct commit on
   `staging` instead of a work item would avoid the failed attempt, since no work item would carry a deletion.)
6. *Hypothesis:* "All changes in the … stage branch" never deploys deletions, so a **genuine** deletion that should
   reach Production must go through the default option. Don't mix a revert-by-deletion and a real deletion in one
   Promote Stage.
