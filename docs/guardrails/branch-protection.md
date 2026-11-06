# Gating promotions with GitHub branch protection

**Observed ([Exp 03](../lab/03-e5-branch-protection-gate.md)): Lifecycle Center respects GitHub branch protection.** A required status check that isn't
passing blocks *Promote Stage*. The block happens **before anything is deployed**, so it fails cleanly.

This makes GitHub the natural place to add guardrails Lifecycle Center doesn't have: CI tests, policy checks,
or a check that Production only receives versions that were in Staging first.

## Requirements

- Branch protection (or rulesets) on a **private** repo needs a paid GitHub plan (**Pro** for a personal-account
  repo, Team/Enterprise for an org). On the free plan the API answers *"Upgrade to GitHub Pro or make this
  repository public"*.
- Turn on **"Do not allow bypassing" / `enforce_admins`**. Lifecycle Center merges PRs as the connected GitHub user,
  who is often a repo admin. Without it, an admin’s merge can bypass the gate. For rulesets, review the
  bypass list instead; that mechanism was not tested here.

GitHub documents both [plan availability and administrator bypass behavior](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

The API example below **replaces** the classic protection configuration for `main`, including review settings.
For an existing team repository, add the required check in settings while preserving its other protections.

```bash
# Require a status check named "lab-gate" on main, enforced for admins too
gh api -X PUT repos/<owner>/<repo>/branches/main/protection --input - <<'EOF'
{"required_status_checks":{"strict":false,"contexts":["lab-gate"]},
 "enforce_admins":true,"required_pull_request_reviews":null,"restrictions":null}
EOF
```

## What happens when the check fails

| | Observed |
|---|---|
| Message | *"We couldn't merge the changes because of branch protection rules in your source control repository. Review the pull request, resolve the issue, then try again."* |
| Production org | **Not deployed.** Component timestamps unchanged. |
| Branch / PR | `main` unchanged. Stage PR stays open, `BLOCKED` in GitHub. |
| Work item | Status unchanged (`PROMOTED`). |
| Request log | No `DevopsRequestInfo` record. |
| Recovery | Fix the check, click **Promote Stage** again. The earlier failure isn't cached. |

Compare this with the [merge-conflict popup](../conflicts/where-conflicts-show-up.md), which names nothing. This
message tells you to look at the PR.

## Checks can run before promotion

**Observed ([Exp 03](../lab/03-e5-branch-protection-gate.md)):** the stage PR exists before Promote Stage is
clicked, so a `pull_request` workflow can run in advance. Check its current result before promoting; the lab's
execution time is not a guarantee about how long your checks will take.

## Ideas for checks

Built and tested: [Check file versions against Staging history](staging-provenance.md) *([Exp 04](../lab/04-g1-staging-provenance-check.md))*.

!!! question "Not yet built"
    - **Run Apex tests** against a validation deploy (`sf project deploy validate`) to the target org.
    - **Block custom/combined promotions** (`WI-xxxxxx → main` PRs) entirely, allowing only `staging → main`.
