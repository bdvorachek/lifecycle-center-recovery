# Work items and statuses

Use work item status to follow promotion progress, then verify the PR and target org separately.
A status records what happened to the work item; it does not prove which version is currently deployed.

In particular, **Combined** means the changes travel with another item, and **Closed** means the item reached the
last stage. A later promotion can replace that content without reopening the earlier item.

## What to check before moving it again

- Identify its current stage and intended next stage.
- If prepared or combined, inspect the current PR rather than assuming it matches the source stage.
- If it is already Promoted, the lab did not offer the Never action; use the relevant recovery route.

The table below uses API status values observed in the lab, not a complete list of UI labels.

## Statuses we've seen

| Status | Meaning (observed) |
|---|---|
| `PROMOTED` | In a stage, not yet at the final stage. |
| `CLOSED` | Reached the last stage (Production). |
| `IN_PROGRESS` / `IN_REVIEW` | Committed, before / after **Create Review** (which opens the `WI → <first stage>` PR). |
| `NEVERED` | Set to **Never**. Lifecycle Center closes its PR and **deletes its branch** ([Exp 05](../lab/05-b3c-combine-dialog-trigger.md)). |
| `COMBINED` | Folded into a newer work item by a combine. Its branch is deleted, and it never shows in Production's "Latest Promotions", its changes travel with the surviving work item when that item is promoted. |

## A clean PR can still restore stale content

**Observed ([Exp 05](../lab/05-b3c-combine-dialog-trigger.md)):** a work item committed from an outdated dev org
reverted a change already in Production, even though its PR was mergeable. Review the actual changes before
promotion; a clean merge does not establish that the values are current or intended.

For operation types, request failures, and SOQL queries, see [Request logs](../recipes/request-logs.md).
