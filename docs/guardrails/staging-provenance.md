# Check file versions against Staging history

This optional diagnostic gate checks historical Git file versions. **It does not prove that a release was tested
as a whole, matches the current Staging org, or avoids rollback.**

Lifecycle Center has two ways to send Production a version of a file that **never existed in Staging**:

- **Combine** replays the work items' commits onto `main`, and "newest wins" can produce a result Staging never
  had. *([Exp 01](../lab/01-same-lines-conflict.md))*
- **Custom promotion with "Prepare"** rebases each selected work item onto `main` with only its own commits. If an
  earlier work item touched the same file and isn't being promoted, Production gets a mix that was never tested.
  **No dialog or warning appears.** *([Exp 04](../lab/04-g1-staging-provenance-check.md))*

Lifecycle Center respects required GitHub checks and is blocked **before deploying** (see
[branch protection](branch-protection.md)). The check below rejected the unrecognized file versions in [Exp 04](../lab/04-g1-staging-provenance-check.md). It checks file history, not release correctness.

## The rule

For every file under `force-app` that the PR would change on `main`:

- **changed or added:** its exact content (Git blob) must match a version `staging` itself held at some point,
  meaning a commit on staging's **first-parent** history. Commits that only lived on work item branches don't count.
- **deleted:** the file must no longer exist on `staging`.

Matching *any* earlier staging version, not just the latest one, is deliberate. A custom promotion of the older
of two work items produces a state Staging really did have, between the two merges, so it's allowed.

??? info "Implementation: GitHub workflow and script"

    ## The workflow

    `.github/workflows/staging-provenance.yml` (commit it to `staging` so it reaches `main` with the next promotion):

    ```yaml
    name: staging-provenance
    on:
      pull_request:
        branches: [main]
        types: [opened, synchronize, reopened]
    permissions:
      contents: read
    jobs:
      staging-provenance:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
            with:
              fetch-depth: 0
          - run: bash .github/scripts/staging-provenance.sh "${{ github.event.pull_request.base.sha }}" HEAD origin/staging force-app
    ```

    `.github/scripts/staging-provenance.sh`:

    ```bash
    #!/usr/bin/env bash
    # Fail if a promotion to main would produce a file version that was never on staging.
    # Usage: staging-provenance.sh <base> <result> <staging> [pathspec]
    set -euo pipefail
    BASE=$1 RESULT=$2 STAGING=$3 SPEC=${4:-force-app}

    annotate() { if [[ -n "${GITHUB_ACTIONS:-}" ]]; then echo "::$1 file=$2::$3"; else echo "$1: $2: $3"; fi; }

    checked=0 bad=0
    while IFS=$'\t' read -r status path; do
      [[ -z "$path" ]] && continue
      checked=$((checked + 1))
      if [[ $status == D ]]; then
        if git cat-file -e "$STAGING:$path" 2>/dev/null; then
          annotate error "$path" "deleted by this promotion but still present on staging"; bad=$((bad + 1))
        fi
        continue
      fi
      want=$(git rev-parse "$RESULT:$path")
      found=""
      for c in $(git log --first-parent --full-history --format=%H "$STAGING" -- "$path"); do
        if [[ "$(git rev-parse -q --verify "$c:$path" 2>/dev/null || true)" == "$want" ]]; then found=$c; break; fi
      done
      if [[ -n "$found" ]]; then
        echo "ok: $path (matches staging @ ${found:0:7})"
      else
        annotate error "$path" "this version never existed on staging (blob ${want:0:7}). Promote it through staging first."
        bad=$((bad + 1))
      fi
    done < <(git diff --no-renames --name-status "$BASE" "$RESULT" -- "$SPEC")

    echo "staging-provenance: $checked file(s) checked, $bad problem(s)."
    [[ $bad -eq 0 ]]
    ```

    Then make `staging-provenance` a required check on `main` with `enforce_admins` on (see
    [branch protection](branch-protection.md)).

    `HEAD` in the workflow is GitHub's test merge (`refs/pull/N/merge`), which is exactly what `main` would become.


## Results

**Observed ([Exp 04](../lab/04-g1-staging-provenance-check.md)):**

| Scenario | Check | Lifecycle Center |
|---|---|---|
| Normal Promote Stage | pass | Promoted and deployed |
| Replay of [Exp 01](../lab/01-same-lines-conflict.md)'s combine PR | **fail**: class and test "never existed on staging" | (offline test) |
| Custom promotion of the **newer** of two work items sharing a file (Prepare → Continue) | **fail** | Blocked with the branch protection message. Nothing deployed. |
| Custom promotion of the **older** one | pass | – |
| Custom promotion of **both** together | one PR passes, one fails | **Whole promotion blocked**, including the passing PR |
| Promote Stage afterwards | pass | Promoted and deployed. Production = Staging. |

Lifecycle Center runs it with its own GitHub token: the `pull_request` workflow fired on the PRs it opened.

## Limitations

- **Files are checked independently.** Two files can each match a historical Staging version without their
  combination ever having existed there. This is not proof that the release was tested as a whole.

- **Per-PR, not per-bundle.** Each `WI-xxxxxx → main` PR is checked against the current `main`. Merged one after
  the other, two work items can add up to exactly Staging's version, but the second PR's check doesn't know the
  first will merge, so the bundle is blocked. Use **Promote Stage** instead. That's the intended effect: custom
  promotions of overlapping work items are pushed back to the whole-stage path.
- **Only Git content is checked**, not what's deployed in the Staging org. Org drift outside Lifecycle Center isn't
  caught.
- Out-of-band commits on `staging` count as "in Staging" even though Lifecycle Center doesn't show them.
- **It accepts any version that *ever* existed on `staging`, including outdated ones.** **Observed ([Exp 10](../lab/10-c3e-silent-regression.md)):** after the
  newer of two same-line work items shipped, custom-promoting the older one rolled Production back to the older
  value, and the check passed. Possible fix (not built): also reject a PR whose result is *older* than what `main`
  already has, for example by requiring the result to match `staging`'s tip for every file that both `main` and
  `staging` have changed.
- A failing check leaves the prepared `WI-xxxxxx → main` PRs and branches **open** after the work items ship by
  Promote Stage. Close them by hand. *([Exp 04](../lab/04-g1-staging-provenance-check.md))*

## When it fails

Inspect the rejected files. If the entire stage is ready to move, **Promote Stage** merges the source stage
branch; still verify the [deployment scope](../how-it-works/promotions.md#deployment-scope-is-a-separate-choice). If you really need only
part of the stage in Production, first make Staging match that part (for example, remove the other work item's
change with a new work item) and let it go through Staging.
