# Open questions

Unresolved questions and a record of answers from the lab. IDs refer to the experiment test plan.
Historical notebook entries retain the hypotheses held at the time; use the guide for current recovery advice.

## Still open

| ID | Question | Why it matters |
|---|---|---|
| H3 | Does merging `main` back into `staging` right after a custom promotion or combine prevent the trap? | Cheap preventive habit. |
| E5a | Does a required check that is *missing* block promotion before deployment, like a failing check? | Expected the same; not run. |
| B7 | Does combine follow creation order when commit and promotion order differ? Salesforce documents creation order; the lab has not varied those orders independently. | Confirm the documented rule against deliberately reordered work items. |
| B3d | Does the dialog appear for a non-conflicting overlap (same file, different lines) when no check is failing? | Exp 04's failing check may have come first. |
| F1 | What exactly does Change Management's "Show Uncommitted Changes" filter hide? | It hid changed classes in Exp 04. |
| B2 | If the newest work item's own commit carries the resolution, does combine keep it? | Would make "resolve in the dev org" the safe practice, and might remove a **Git required** case. |
| D6b | Does a later commit from a stale dev org revert a direct Git edit? Exp 20 confirmed the org lacked the edit; the subsequent revert scenario remains untested. | Detecting and recovering from drift. |
| E1b | Does assigning a **test plan** to a stage run tests automatically on every promotion? | Would close the "No tests by default" gap. |
| E3 | Is there a supported rollback? | – |
| E4 | How do you replace an expired stage org? | Scratch orgs expire. |
| B9 | Does Back Sync before starting work reduce conflicts, and how does “Sync all changes” differ? “In Sync” was observed in Exp 08; its exact scope remains unverified. | Establish a reliable team sync routine. |
| E1c | Can a Git merge fail after a successful deployment and leave the org ahead of its branch? | Failed deployments were tested (Exp 13); a post-deploy merge failure was not. |

## Answered in this lab

| ID | Question | Why it matters |
|---|---|---|
| ~~A3b~~ | ~~Does fixing a stuck stage with a plain Git merge work?~~ **Yes, silently**: no warning, no Staging redeploy (Exp 06). See [Fix B](../conflicts/stuck-after-combine.md#fix-b-merge-the-branches-in-git-outside-lifecycle-center). | – |
| ~~H2~~ | ~~Does an ordinary custom promotion split the history?~~ **Yes** (Exp 08): promoting the older of two same-line work items stuck the stage. See [Stuck stage](../conflicts/stuck-after-combine.md). | – |
| ~~C3b~~ | ~~Does a Promote Stage of a work item on other files repair the split history?~~ **Yes** (Exp 12): merge-base moved to staging's tip. | – |
| ~~C3d~~ | ~~Fix C with two same-line stuck work items?~~ **Combine works; Continue fails cleanly** (Exp 09). | – |
| ~~C3e~~ | ~~Does an out-of-order custom promotion silently roll Production back?~~ **Yes** (Exp 10), with no warning, and the provenance check passes. | – |
| ~~C3f~~ | ~~Can the silent rollback be undone without Git?~~ **Yes**, with two throwaway work items + Combine (Exp 11). "All changes in the … stage branch" deploys the whole branch. | – |
| ~~E5~~ | ~~Does Lifecycle Center respect branch protection?~~ **Yes, and before deploying.** See [Branch protection](../guardrails/branch-protection.md). | – |
| ~~G1~~ | ~~Can a CI check reject versions that never existed on `staging`?~~ **Yes.** See [Staging provenance check](../guardrails/staging-provenance.md). | – |
| ~~B3b~~ | A single prepared item: no dialog in Exp 04 (different-line overlap, failing check); dialog in Exp 08 (same-line overlap). | See B3d for the remaining uncertainty. |
| ~~B3c~~ | ~~What triggers the combine dialog?~~ **Clicking Promote** with prepared work items sharing a component (Exp 05). | – |
| ~~C2~~ | ~~Out-of-order custom promotion: can Production get a version that never existed in Staging?~~ **Yes, silently**, with no dialog. See Exp 04. | – |
| ~~C1 / Exp 21~~ | ~~Does a plain custom promotion (no shared components) make stage branches diverge?~~ **Yes, in history** (merge-base doesn't move), not in content. Harmless until someone edits the same or adjacent lines; one Promote Stage repairs it (Exp 21). | – |
| ~~D1a/D1b / Exp 19~~ | ~~What happens to content committed straight to `staging`?~~ **Silently accepted, nothing redeployed.** The default Promote Stage merges it into `main` but deploys it only with a work item on the same file. Recovery: carrier work item + "All changes" at both stages (Exp 19). | – |
| ~~D1c / Exp 20~~ | ~~A commit on a **prepared** branch, promoted without Combine: is it promoted as-is?~~ **Yes** (Exp 20). The [Git fix](../conflicts/test-failures.md#the-git-fix) needs one commit when nothing is combined. | – |
| ~~E1~~ | ~~Is the org left out of step with its branch after a failed deploy?~~ **No** (Exp 13): deploy fails → no merge. But with the default No tests, a failing combination ships silently. | – |
| ~~E6~~ | A broken combined work item can be fixed without shipping it broken: fix the branch after the last rebuild (Exp 15), or revert held-back work and Promote Stage (Exp 16–17). Exp 14’s ship-then-fix route is historical evidence only. | See [Test failures](../conflicts/test-failures.md). |
| ~~D4 / Exp 15~~ | ~~Does Lifecycle Center promote a branch fixed in Git as you left it?~~ **Yes, the combined branch** (Exp 15). Combine drops commits pushed to *prepared* branches. See [the Git fix](../conflicts/test-failures.md#the-git-fix). | – |
| ~~E6b / Exp 16~~ | ~~Can pending work be taken out of Staging with a revert work item, so Promote Stage ships only what's wanted?~~ **Yes** (Exp 16). The reverted work item shows Closed. See [the revert route](../conflicts/test-failures.md#the-revert-route). | – |
| ~~E6c / Exp 17~~ | ~~Revert route when the pending work item **added** a component?~~ **Works**: the deletion commits and reaches Staging, but the default Promote Stage fails on it; "All changes in the Production stage branch" gets through (Exp 17). | – |
| ~~E6d / Exp 18~~ | ~~Does "All changes in the … stage branch" ever deploy deletions?~~ **No.** It deploys the branch contents only; the default option deploys deletions (Exp 18). | – |
| ~~B8~~ | ~~Can a work item vs stage conflict be fixed without Git?~~ **Yes**: Never → Back Sync → redo (Exp 07). The developer has to redo the change. See [Work item vs. stage](../conflicts/work-item-conflict.md). | – |
