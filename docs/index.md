# Lifecycle Center: Promotion Mechanics

Understand what moves between stages, what Prepare and Combine change, and how to recover a blocked promotion.
This guide assumes you already know how to create, commit, and review a work item.

[Download the pipeline recovery agent skill](agent-skill.md) to use this guide’s recovery knowledge with your agent.

## Understand a promotion

- **[Promotion paths and scope](how-it-works/promotions.md)** — Promote Stage versus custom promotion, and why stage merges matter.
- **[Prepare and Combine](how-it-works/combining.md)** — how selected work items become a release, and what to inspect.
- **[Branches and deployed content](how-it-works/git-model.md)** — why a merged PR and a successful deployment answer different questions.
- **[Work item status](how-it-works/work-items.md)** — what the records tell you, and what they don't.

## Troubleshoot a promotion

| What you see | Start here |
|---|---|
| A work item cannot enter the first stage | [Work item vs. stage conflict](conflicts/work-item-conflict.md) |
| Promote Stage fails after custom promotion or Combine | [Stage conflict recovery](conflicts/stuck-after-combine.md) |
| Git is clean, but deployment tests fail | [Test failure recovery](conflicts/test-failures.md) |
| The pipeline looks clean, but the target has an older value | [Silent rollback](conflicts/stuck-after-combine.md#silent-rollback-after-out-of-order-custom-promotions) |
| A custom promotion fails without a useful message | [Find the failing PR or check](conflicts/where-conflicts-show-up.md) |
| You need to decide whether recovery changes Git | [Recovery options](conflicts/when-you-need-git.md) |

## Reading the examples in a four-environment pipeline

Your pipeline is **Dev Sandboxes → Integration → Staging → Production**. Integration is the first pipeline stage;
Dev Sandboxes are the development environments. A later promotion has a **source stage** and a **target stage**:
Integration → Staging, or Staging → Production.

The experiments used a smaller pipeline: **dev / dev2 → Staging (`staging`) → Production (`main`)**.
The lab's Staging served the first-stage role that Integration serves in your pipeline. Its final org was
Developer Edition, not a business production org. The examples keep those original names so their commands and
evidence remain traceable. Identify your actual source and target branches before adapting a recovery.
The four-environment topology has not been tested by this lab.

## What the evidence means

This is an unofficial guide to **Lifecycle Center**, formerly next-generation DevOps Center, with GitHub.
It does not establish behavior for **DevOps Center (Managed Package)**.

| Label | Meaning |
|---|---|
| **Documented** | Salesforce describes this behavior; linked to the relevant official page. |
| **Observed** | Seen in the lab configuration; linked to the experiment. |
| **Simulated** | Reproduced locally in Git, not through a live promotion. |
| **Hypothesis** | An explanation or possible route that has not been verified. |
| **Practical implication** | Guidance derived from the evidence, not a product requirement or team policy. |

The guide draws on 21 experiments from October 31 through November 5, 2026 (UTC).
For setup and individual development workflows, use Salesforce's
[Lifecycle Center journey](https://help.salesforce.com/s/articleView?id=platform.next_gen_devops_center_alm_journey.htm&language=en_US&type=5)
and your internal development documentation. For the tested configuration and limitations, see
[How we tested](lab/index.md). Detailed logs are supporting evidence, not required reading.
