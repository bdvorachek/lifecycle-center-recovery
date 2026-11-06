# Where conflicts show up

Lifecycle Center checks for conflicts at a few points. Here's what each looks like and what it tells you.

## Start with the operation that failed

| Failure | Inspect | Recovery |
|---|---|---|
| Work item cannot enter first stage | Work item → first-stage PR | [Work item conflict](work-item-conflict.md) |
| Promote Stage reports conflicts | Source-stage → target-stage PR | [Stage conflict](stuck-after-combine.md) |
| Prepare/Next fails with a generic message | Prepared PRs and their checks | Correct the failing check or conflicting PR before retrying |
| Deployment reports a test failure | Activity History → View Details → Error Details | [Test failures](test-failures.md) |

## The UI doesn't name the files

!!! info "Needs Git? To diagnose"
    You'll need GitHub, or read-only Git, to see what's conflicting. Whether you need Git to *fix* it depends on
    the situation. See [When you need Git](when-you-need-git.md).

To find out what's actually conflicting, go to GitHub:

```bash
gh pr list --state open                         # find the stuck PR (e.g. "Promotion: staging → main")
gh pr view <N> --json mergeable,mergeStateStatus  # CONFLICTING / DIRTY
```

The PR page lists the files ("This branch has conflicts that must be resolved"). To reproduce locally without changing your checkout, use the throwaway worktree in
[Inspecting pipeline state](../recipes/inspecting-state.md#simulate-a-promotion-without-touching-anything).

## The banner is cached

**Observed ([Exp 02](../lab/02-stage-promotion-after-combine.md)):** after a failed Promote Stage, the *"couldn't validate"* banner stays on the Staging
column even after the conflict has been fixed in Git and GitHub reports the PR as `MERGEABLE`. Clicking
**Promote Stage** again re-checks it and goes through.

## About "Resolve Using Agentforce"

**Documented:** Salesforce's
[Resolve Using Agentforce](https://help.salesforce.com/s/articleView?id=platform.devops_center_next_gen_resolve_conflict.htm&language=en_US&type=5)
flow opens Agentforce Vibes IDE with conflict context. It assists the investigation and code/Git repair, much as an
AI coding agent can in desktop VS Code; it is not a separate kind of branch reconciliation.

The lab did not test this integration. Whether you use the browser IDE or desktop tooling, inspect which branch is
changed, what content survives, and whether the next promotion deploys the intended result. The recovery pages
explain those mechanics independently of the editor.

??? info "Supporting evidence: UI messages and side effects by operation"

    | When | What you see | Files named? | Options | Side effects |
    |---|---|---|---|---|
    | Committing a work item | Nothing | – | – | – |
    | Work item cards in Approved | **No warning**, even when two items change the same lines | – | – | – |
    | Promoting a **bundle** of overlapping work items into the first stage | Blocked before merging | No | Resolve using Agentforce | Branches, PRs and orgs untouched. Request log gets an `ERROR` "Promotion failed" ([Exp 01](../lab/01-same-lines-conflict.md)) |
    | Promoting a single work item that conflicts with its stage branch | Popup **"Can't validate promotion"**: *"Cannot initiate the promotion due to merge conflicts"*, shown before the Promotion Options dialog. The work item page shows no warning, and approval is allowed. | In GitHub | Close / Resolve using Agentforce. Fix: see [Work item vs. stage](work-item-conflict.md) | None ([Exp 07](../lab/07-b8-never-and-redo.md)). [Exp 01](../lab/01-same-lines-conflict.md) left an `ERROR` "Promotion failed" request record instead; this may have changed between releases |
    | Custom promotion, **Prepare** step, work item's commit conflicts with `main` | **Nothing**: Prepare succeeds, keeping the work item's lines ([Exp 05](../lab/05-b3c-combine-dialog-trigger.md)) | – | – | The prepared PR can differ from Staging |
    | Custom promotion, clicking **Promote** with prepared work items that share a component | **Resolve Shared Components** dialog | Components listed | Combine / Continue | See [Combining](../how-it-works/combining.md) |
    | Custom promotion of **one** of two work items that share a file | **No dialog** for different-line overlap ([Exp 04](../lab/04-g1-staging-provenance-check.md)); **Resolve Shared Components** for same-line overlap ([Exp 08](../lab/08-c3-stuck-stage-promoted-wi.md)) | – | – | Production can get a version Staging never had. See [Staging provenance check](../guardrails/staging-provenance.md) |
    | Promoting with tests when the **combined** code fails a test | Red banner *"We couldn't deploy your work items…"* | **View Details** shows the test and assertion | Fix forward (see [Test failures](test-failures.md)) | `ERROR` request, `DEPLOYMENT_FAILURE`. Org unchanged, branch not merged ([Exp 13](../lab/13-e1-combined-test-failure.md)). With the default **No tests**, nothing is caught. |
    | **Promote Stage** when stage branches conflict | Popup: *"Cannot initiate promotion due to merge conflicts."* Then a banner: *"We couldn't validate the promotion due to merge conflicts."* | **No** | Resolve Using Agentforce | None. **No** request record, no merge, no deploy ([Exp 02](../lab/02-stage-promotion-after-combine.md)) |
