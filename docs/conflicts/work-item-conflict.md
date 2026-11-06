# Work item vs. stage conflict

**Situation:** two work items changed the same lines. The first one was promoted to Staging. The second one's
PR (`WI-xxxxxx → staging`) now conflicts.

!!! warning "Needs Git? Recommended"
    There is a Lifecycle Center-only way out (abandon-and-redo route, [Exp 07](../lab/07-b8-never-and-redo.md)), but the developer has to throw their work item away
    and redo the change by hand. A Git merge on the work item branch (branch-resolution route) keeps their work. See
    [When you need Git](when-you-need-git.md).

**What you see ([Exp 07](../lab/07-b8-never-and-redo.md)):** nothing, until you promote. The work item page shows no warning and lets you mark it Ready to
Promote. **Promote Selected** then shows *"Can't validate promotion: Cannot initiate the promotion due to merge
conflicts"*, offering only Close or Resolve using Agentforce. No request record is created.

## Confirm the problem

**Who:** a contributor who can inspect the PR; the branch-resolution route needs Git merge and push access.
Open the work item's PR and confirm that it conflicts with the **first stage** branch. In your pipeline this is
Integration; the lab calls its first stage Staging. Adapt both branch and org names in the examples below.

## Choose a recovery

| What needs to survive? | Route | Consequence |
|---|---|---|
| Existing work item and its changes | Resolve on its branch | Preserves work, but a later Combine can discard the manual resolution |
| Only the intended outcome; redoing the change is acceptable | Abandon, Back Sync, redo | Never deletes the branch; sync can overwrite the developer's change |

## Resolve on the work item branch (Git)

This is what we did in [Exp 01](../lab/01-same-lines-conflict.md). It worked for getting into Staging.

```bash
git fetch
git switch -c resolve-work-item origin/WI-xxxxxx
git merge origin/staging            # conflicts appear
# edit the conflicted files, keeping class and test consistent
sf project deploy validate -o <staging-alias> -d force-app \
   --test-level RunSpecifiedTests --tests <YourTest>
git add <resolved-files>
git commit
git push origin HEAD:WI-xxxxxx       # updates the existing work item PR
```

Then promote the work item in Lifecycle Center as usual.

!!! danger "Two traps"
    1. **Your dev org is now out of date.** The dev org still has the work item's original version. The branch
       has the resolution. The next commit from that org can silently put the old version back
       (**Observed**, [Exp 05](../lab/05-b3c-combine-dialog-trigger.md)). Back Sync the org once the work item has been promoted.
    2. **A combine throws your resolution away.** If this work item is later combined, its branch is rebuilt from
       its original commits only. See [Combining](../how-it-works/combining.md).

!!! tip "Keep class and test consistent"
    A resolution can be textually clean but logically wrong. For example, if you take one side's class constant
    and the other side's test assertion, the tests fail at promotion. Resolve each pair of related lines the same way.

## Abandon, Back Sync, and redo (Lifecycle Center only)

**Verified in [Exp 07](../lab/07-b8-never-and-redo.md).** Throw away the conflicting work item, bring its dev org up to date with Staging, and make
the change again on top.

1. On the conflicting work item: status menu → **Change Status to Never**. Lifecycle Center closes its PR and
   deletes its branch. *"You can't undo this action."*
2. Pipeline → Approved Work Items → **"N Development Environments · View"** → pick the dev environment →
   **Sync Options…** → **Sync**. This deploys Staging's version of the other work items' components into the dev org.
3. Make the change again in the dev org, on top of Staging's version.
4. New work item for that dev environment (if the org's top bar shows no work item selector, create it in
   Lifecycle Center: Work Items → New) → commit only the redone files → review → promote. The PR is clean.

!!! danger "What it costs"
    - **The developer's change is overwritten in the dev org** by the sync, without warning. They have to redo it.
      Their original commit only survives in the closed PR (and in anyone's local clone).
    - **Back Sync is refused while the dev org has any open work item** (*"Can't back sync … Promote them, then try
      again."*). The conflicting work item can't be promoted, so you must Never it first.
    - After a sync, Change Management lists the synced components (in [Exp 07](../lab/07-b8-never-and-redo.md), classes from *other* developers'
      work items) as changes. Commit **only** your own files.
    - The default **"Show Uncommitted Changes"** filter may hide the file you redid. Switch to **Show All Changes**.

## Verify success

1. The work item's PR is mergeable and contains the agreed resolution, including consistent tests.
2. Promotion to the first stage passes the relevant tests and deploys the expected components.
3. The development org is brought up to date after promotion before another commit can restore stale content.
4. If the work item is later prepared or combined, inspect that rebuilt PR again; the earlier resolution may not survive.

??? info "Supporting evidence: unverified prevention and alternative resolution"

    !!! tip "Prevention (Hypothesis)"
        Back Sync each dev environment before starting a new work item there. The work item branch is cut from the
        stage branch at the **first commit** ([Exp 07](../lab/07-b8-never-and-redo.md)), so a synced org plus an early commit should keep the change on
        top of what's already in Staging. Not tested yet.

    ## Option 3: Resolve in the dev org without Never (not tested)

    **Hypothesis (B2):** put the latest Staging version plus the agreed values into the dev org, and commit to the
    **same** work item. Back Sync can't do this while the work item is open, so getting Staging's version into the org
    needs the CLI or a manual edit. Also, the work item's branch still has its old base, so the PR may still conflict.
    Untested.
