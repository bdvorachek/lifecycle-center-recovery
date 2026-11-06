# Collect a focused state snapshot

Replace placeholders with confirmed values. Use explicit repository and org targets; do not assume CLI defaults are the correct environment. These examples come from `recipes/inspecting-state.md` and `recipes/request-logs.md` in the companion manual.

## Git and GitHub

```bash
git status --short
git remote -v
git fetch origin
gh pr view <PR> --repo <owner/repo> --json state,baseRefName,headRefName,headRefOid,mergeable,mergeStateStatus,statusCheckRollup
git diff --stat origin/<target> origin/<source>
git diff origin/<source> origin/<prepared-WI> -- <affected-files>
git log --graph --oneline origin/<target> origin/<source> -20
git merge-base origin/<target> origin/<source>
```

A content diff or old merge-base is not proof of a conflict. Inspect GitHub's mergeability and conflicting files or simulate the merge in an isolated checkout. `UNKNOWN` can be transient; recheck after computation. Inspect failing checks even when they are not required: a prepared PR that is not `CLEAN` blocked Next in Exp 14.

Compare the actual affected files against the intended source version after Prepare/Combine. A provenance check can accept *historical* source-stage content, including an obsolete version (Exp 10).

## Lifecycle Center hub records

```bash
sf data query -o <hub-alias> -q \
  "SELECT Name, Subject, Status, LastModifiedDate FROM WorkItem ORDER BY Name"
sf data query -o <hub-alias> -q \
  "SELECT Name, OperationType, Status, Message, CreatedDate, RequestCompletionDate FROM DevopsRequestInfo ORDER BY CreatedDate DESC LIMIT 10"
```

Use the hub org (the release org served that role in the lab). Do not use Tooling API for these objects. Correlate timestamps and operations with the user's attempt; increase or filter the window as needed. Prepare is `REBASE`; Combine is `REBASE_AND_COMBINE`.

A preflight rejection may create no request; absence of an ERROR does not mean success. The notebook observed differing work-item failure paths (Exp 01 and 07), while stage conflicts/protection could fail before a request (Exp 02 and 03). Inspect PRs and orgs independently.

## Deployed content

For Apex, inspect the actual class body in each relevant org:

```bash
sf data query -o <target-alias> --use-tooling-api --json \
  -q "SELECT Name, Body, LastModifiedDate FROM ApexClass WHERE Name='MyClass'"
```

For other metadata, retrieve only affected components into a separate local Salesforce project and compare with the final PR. Retrieval writes local files: avoid overwriting the working source. Modification timestamps are supporting evidence, not deployment audit logs. Inspect the deployment report for the components and tests actually processed. Redact credentials and identifying org details from shared reports.
