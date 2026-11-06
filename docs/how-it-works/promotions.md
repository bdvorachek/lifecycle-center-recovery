# Promotion paths and scope

A promotion changes a target stage's branch and deploys selected components to its org. To understand the result,
separate three questions: **which work items move, which Git content is merged, and which components are deployed?**

## Which path are you using?

| Path | How it builds the result | What to inspect |
|---|---|---|
| Work item into the first stage | Merges the work item branch into the first stage branch | The work item PR, conflicts with work already there, and the deployment result |
| **Promote Stage** | Merges the source stage branch into the target stage branch | The entire stage PR and deployment scope; this is not a selection of individual work items |
| **Custom promotion** | Prepare replays selected work items' own commits onto the target branch | Each prepared PR; the result can differ from the source stage |
| **Combine during custom promotion** | Rebuilds selected work into a surviving work item branch | The final combined PR, especially any earlier manual conflict resolutions |

**Documented:** Salesforce describes selective promotion in
[Custom Promotion](https://help.salesforce.com/s/articleView?id=platform.devops_center_custom_promotion.htm&language=en_US&type=5)
and creation-order combining in
[Combine Work Items](https://help.salesforce.com/s/articleView?id=platform.devops_center_combine_work_items.htm&language=en_US&type=5).
**Observed:** the branch and deployment distinctions above come from
[Exp 01](../lab/01-same-lines-conflict.md), [Exp 19](../lab/19-d1ab-direct-commit-on-staging.md), and
[Exp 21](../lab/21-c1-custom-promotion-independent.md).

## Apply this to Integration → Staging → Production

```mermaid
flowchart LR
    D[Dev Sandboxes] -->|Work items| I[Integration]
    I -->|Stage or custom promotion| S[Staging]
    S -->|Stage or custom promotion| P[Production]
```

Examine each boundary separately. An Integration → Staging promotion doesn't itself release anything to Production.
A later Staging → Production promotion has its own PR, deployment scope, and checks.

The lab used only one intermediate stage, named Staging. In the lab's **first-stage** recipes, that name maps to
your **Integration** role. In **stage-to-stage** recipes, `staging` and `main` mean the lab's source and target branches.
Use the actual branches for the boundary you are investigating; don't substitute names blindly. In particular,
the lab's Back Sync recipes source the first stage, not an arbitrary later stage. A four-environment recovery may
need an additional promotion through Integration before the repaired content reaches Staging.

## Why Promote Stage matters after custom promotions

**Observed:** Prepare and Combine put replayed commits on the target branch while the source retains its original
commits. Even when file content matches, those branches can retain separate histories. A later change to the same
or adjacent lines can then conflict ([Exp 06](../lab/06-a3b-git-merge-recovery.md),
[Exp 21](../lab/21-c1-custom-promotion-independent.md)). An old merge-base alone does not prove a conflict.

A successful **Promote Stage** incorporates the source branch's history into the target. The lab demonstrated that
this can clear the history divergence left by custom promotions
([Exp 12](../lab/12-c3b-heal-split-history.md), [Exp 21](../lab/21-c1-custom-promotion-independent.md)).

**Practical implication:** periodically completing a stage promotion matters when using custom promotion;
otherwise the shared history can remain behind. It is appropriate when the source stage's release scope can move
forward and the merge and tests pass. If held-back work must stay, inspect the
[recovery alternatives](../conflicts/stuck-after-combine.md) instead.

This reconciles **that pair of branches**. It does not automatically sync development sandboxes, repair every org's
drift, or synchronize all stages. In your pipeline, inspect Integration → Staging and Staging → Production separately.

## Deployment scope is a separate choice

**Observed in the tested Apex promotions:**

| Promotion option | Scope | Limitation |
|---|---|---|
| Only changes missing from the target (default) | Components associated with promoted work items, using branch content | Other changes in those same files can ride along; unrelated branch-only changes may not deploy |
| All changes in the target stage branch | All components in that branch | Does not deploy deletions in the lab; it is not a complete org reset |

See [deployment evidence and exceptions](git-model.md#what-gets-deployed). Validate other metadata types and your
org's test requirements; the lab's final org was Developer Edition.

## What confirms a successful promotion?

1. The intended work items and final PR represent the intended release scope.
2. Required checks and the selected deployment tests pass.
3. The promotion completes and the expected PR is merged.
4. The affected components in the target org have the intended behavior and content.
5. After custom promotion, inspect whether a later stage merge is clean; matching file content alone doesn't
   establish shared history.

These are different observations. A Closed work item, passing provenance check, or merged PR alone is not proof
that the target org matches the intended release. Use [Inspecting pipeline state](../recipes/inspecting-state.md)
when those signals disagree.
