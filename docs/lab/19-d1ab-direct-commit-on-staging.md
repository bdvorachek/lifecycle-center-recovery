# Experiment 19: A direct Git commit on `staging` (D1a, D1b)

## Question
Exp 06, 17 and 18 suggest the default Promote Stage decides **what** to deploy from the work items. What happens to a
content change committed straight to the `staging` branch (outside Lifecycle Center)?
- **D1a:** on a file **no work item** touches (DiscountCalculator). Is the Staging org redeployed? Does Promote Stage
  carry it to Production, or only to `main`?
- **D1b:** on a file a **pending work item also touches** (LabPing). Does Production get the work item's version or
  the branch's version, with the direct edit?
- Recovery: can Lifecycle Center alone get the orgs back in line with the branches?

## Design
- **WI-Q** (dev): a comment line at the **top** of LabPing → Staging.
- **Direct commit** pushed to `staging`: a header comment in DiscountCalculator (D1a), and LabPing's **bottom**
  comment line changed (D1b). Comment-only, so tests are unaffected.
- Watch the Staging org for ~3 minutes. Then Promote Stage (default "Only changes missing from Production", tests
  LabPingTest, DiscountCalculatorTest). Read the release deploy and compare org bodies with the branches.
- Recovery without Git: a carrier work item (new test class `LabCarrierTest`, on a file no dev org can revert) →
  Staging with **"All changes in the Staging stage branch"** → Promote Stage with **"All changes in the Production
  stage branch"**.

## Before snapshot
- Exp 18's after state: `main` = `545c0ee`, `staging` = `e7cac4f`, identical content, shared history, no open PRs.
- staging and release: DiscountCalculator and LabPing identical (same body hash).

## Steps / Actual
1. Deployed WI-Q's LabPing to dev (`--ignore-conflicts`: dev's source tracking still had an old LabPing).
   **WI-Q** = WI-000044, commit `b024eaf` (DORI-156) → Staging with LabPingTest (DORI-157), `staging` = `e4cf5ad`.
2. **Direct commit** `24437ec` pushed to `staging` (DiscountCalculator header + LabPing bottom line). `staging` isn't
   protected, so the push went straight in.
3. Waited 3 minutes: **no request, no redeploy.** staging DiscountCalculator and LabPing unchanged (LabPing has Q,
   not the direct line). Pipeline view: no warning; Staging card just shows WI-000044. A new stage PR (#89) was
   MERGEABLE.
4. **Promote Stage**, default, tests LabPingTest + DiscountCalculatorTest. DORI-158 **SUCCESS**, `main` = `6845e8a`
   (contains the direct commit). release deploy `0Afg700000IPZOPCA5`: **LabPing only**.
   - **D1a:** DiscountCalculator **not deployed**. `main` has the header line; release and staging don't.
   - **D1b:** release LabPing = **branch version**: Q's top line **and** the direct bottom line. staging LabPing
     has only Q's line, so Production now runs a version the Staging org never had.
5. Promote Stage then greyed out: *"No Work Items in Staging"*. No Lifecycle Center control redeploys a stage without a
   work item.

### Recovery (Lifecycle Center only)
6. **Carrier** WI-C = WI-000045 (dev): new `LabCarrierTest` (an `@IsTest` class, so it needs no coverage itself),
   commit `fa31d10` (DORI-159).
7. → Staging with **"All changes in the Staging stage branch"**, Run specified tests LabCarrierTest: DORI-160
   **ERROR** *"Code Coverage: Test coverage of selected Apex Class is 0%"* (×3). Coverage is enforced on the scratch
   Staging org too when you name tests. Retried with LabCarrierTest, LabPingTest, AccountSummaryTest,
   DiscountCalculatorTest: DORI-161 **SUCCESS**. staging now has the DiscountCalculator header and LabPing's direct
   line: **the Staging org matches its branch again.**
8. **Promote Stage, "All changes in the Production stage branch"**, same four tests: DORI-162 **SUCCESS**. release
   DiscountCalculator has the header; LabPing unchanged (already right); LabCarrierTest added.

## After snapshot
- `main` = `667386d`, `staging` = `282e5e3`, merge-base = `282e5e3`: identical content, shared history. No open PRs.
- staging = release = branches for DiscountCalculator (with `d1a` header), LabPing (Q top line + direct bottom line)
  and LabCarrierTest (new, lab-only test class).
- dev LabPing has Q's line but **not** the direct line (dev orgs never see a direct commit; see finding 5).

## Findings
1. **A direct commit on `staging` is accepted silently and redeploys nothing.** No request, no warning, no change to the
   Staging org. The branch and the Staging org now differ.
2. **D1a: the default Promote Stage merges it into `main` but never deploys it.** "Only changes missing from
   Production" deploys only the **components of the promoted work items**. A file no work item touches goes to
   `main` and stays out of every org. After the stage merge, nothing in the UI shows it.
3. **D1b: on a file a work item touches, the deploy takes the file from the branch**, so the direct edit ships with the
   work item. Production gets a version that never ran in the Staging org (and that no test in Staging covered).
4. **Lifecycle Center-only recovery exists** but needs a carrier work item: promote it to Staging with "All changes in
   the Staging stage branch" (redeploys the whole branch to the Staging org), then Promote Stage with "All changes in
   the Production stage branch". Both need tests covering all Apex in the branch. Remember "All changes" never deploys
   deletions (Exp 18).
5. *Hypothesis:* the next work item from a dev org on a file changed by a direct commit will silently revert that
   change (the dev org never had it, same as D6). Back Sync first.
6. Rule for the guide: **don't commit content straight to a stage branch.** If someone did, the safe recovery is the
   "All changes" pair above, and check `git diff` between the branch and what's actually in the orgs.
