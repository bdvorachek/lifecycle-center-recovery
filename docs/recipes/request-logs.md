# Work item records and request logs

Read-only diagnostics for correlating a promotion with its recorded operations. Use the Lifecycle Center hub org
for these queries; the lab used its release org as the hub.

## Request log: `DevopsRequestInfo`

Every Lifecycle Center operation that actually runs creates a `DevopsRequestInfo` record:

| Field | Example |
|---|---|
| `Name` | `DORI-000000018` |
| `OperationType` | `COMMIT`, `PROMOTE`, `REBASE` (custom-promotion "Prepare"), `REBASE_AND_COMBINE` (combine) |
| `Status` | `SUCCESS`, `ERROR` |
| `Message` | `Promotion completed successfully`, `Promotion failed`, `Prepare branch with rebase completed successfully.` |
| `CreatedDate` / `RequestCompletionDate` | start / end |

!!! tip "Which failures leave a record"
    - **Work item promotions** that fail on conflicts (a bundle of overlapping work items, or one work item that
      conflicts with the stage branch) create a request with `Status = ERROR`, "Promotion failed". Git and the orgs
      don't change. *([Exp 01](../lab/01-same-lines-conflict.md): DORI-6, DORI-8.)*
    - **Promote Stage** refused for merge conflicts or branch protection creates **no** request at all. The check
      runs before a request is made. *([Exp 02](../lab/02-stage-promotion-after-combine.md), [Exp 03](../lab/03-e5-branch-protection-gate.md).)*

    Either way, nothing was merged or deployed, so there's nothing to clean up.

```bash
sf data query -o <release-org> -q \
  "SELECT Name, Subject, Status, LastModifiedDate FROM WorkItem ORDER BY Name"

sf data query -o <release-org> -q \
  "SELECT Name, OperationType, Status, Message, CreatedDate, RequestCompletionDate
   FROM DevopsRequestInfo ORDER BY CreatedDate DESC LIMIT 10"
```

Don't add `-t` to these queries: in `sf data query` it means **Tooling API**, which answers "sObject type not supported".

See [Inspecting pipeline state](../recipes/inspecting-state.md) for a full snapshot.
