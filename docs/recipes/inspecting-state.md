# Inspecting pipeline state

Take a snapshot like this before and after anything risky. It shows what each layer says: Git, GitHub,
Lifecycle Center's records, and the orgs.

Commands use placeholders such as `<release-org>` and `<WI-branch>`; replace them with your pipeline’s
aliases and branch names. Recovery commands assume a clean working tree and a fresh fetch.

## Git: branch heads and divergence

```bash
git fetch --prune
git ls-remote --heads origin                     # every branch head
git diff --stat origin/main origin/staging        # content differences in either direction
git log --graph --oneline origin/main origin/staging -15
git merge-base origin/main origin/staging         # best common ancestor (not a content comparison)
```

## GitHub: pull requests

```bash
gh pr list --state all --limit 20                 # date column = created, not merged
gh pr view <N> --json state,mergeable,mergeStateStatus,createdAt,mergedAt,headRefOid
```

`mergeable` is computed on demand. Right after a push it reads `UNKNOWN`, so query it again a few seconds later.

## Lifecycle Center records

```bash
sf data query -o <release-org> -q "SELECT Name, Subject, Status FROM WorkItem ORDER BY Name"
sf data query -o <release-org> -q "SELECT Name, OperationType, Status, Message, CreatedDate
  FROM DevopsRequestInfo ORDER BY CreatedDate DESC LIMIT 10"
```

## Orgs: what's actually deployed

`LastModifiedDate` records the component’s last modification; it is supporting evidence, not a deployment audit
log. Compare the body to establish content, and inspect the deployment report to establish which components shipped.

```bash
sf data query -o <alias> --use-tooling-api -q \
  "SELECT Name, LastModifiedDate FROM ApexClass WHERE Name LIKE 'MyClass%'"

# grep specific lines out of the deployed body
sf data query -o <alias> --use-tooling-api --json \
  -q "SELECT Body FROM ApexClass WHERE Name='MyClass'" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['result']['records'][0]['Body'])" \
  | grep -n 'MY_CONSTANT'
```

## Simulate a promotion without touching anything

Use a throwaway worktree so your checkout stays untouched:

```bash
git fetch
sim_dir=$(mktemp -d "${TMPDIR:-/tmp}/lc-merge.XXXXXX")
git worktree add --detach "$sim_dir" origin/main
# A nonzero exit here can mean a conflict; inspect the output and status.
git -C "$sim_dir" merge --no-commit --no-ff origin/staging
git -C "$sim_dir" status --short
# If already up to date, no merge was started and there is nothing to abort.
if git -C "$sim_dir" rev-parse -q --verify MERGE_HEAD >/dev/null; then
  git -C "$sim_dir" merge --abort
fi
git worktree remove "$sim_dir"
```
