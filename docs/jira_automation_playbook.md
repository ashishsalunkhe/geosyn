# Jira Automation Playbook

## Goal

Make Jira status movement happen automatically from GitHub activity without forcing developers to manually update tickets every time they code.

This playbook assumes:

- Jira project key is `GEOSYN`
- GitHub repo is `ashishsalunkhe/geosyn`
- Jira is connected to GitHub through the GitHub for Atlassian app
- sprint naming follows `GEOSYN MM.DD`

In all examples below, `GEOSYN-0028` is a placeholder for the real Jira issue key in zero-padded form such as `GEOSYN-0027` or `GEOSYN-0028`.

## Recommended Approach

Use both of these, but for different jobs:

- `GitHub for Atlassian` for visibility
- `Jira Automation` for status transitions

Use `Smart Commits` only for optional extras like comments or time logging, not as the main workflow engine.

Why:

- Automation rules are easier to reason about
- PR-driven transitions are safer than raw commit-driven transitions
- Smart Commits are brittle when emails or transition names do not match exactly

## Recommended Workflow

Use these issue states:

- `To Do`
- `In Progress`
- `In Review`
- `Done`

Recommended transition logic:

1. branch created with `GEOSYN-0028` in the branch name:
   move issue from `To Do` to `In Progress`
2. commit created with `GEOSYN-0028` in the commit message:
   if still `To Do`, move issue to `In Progress`
3. pull request created with `GEOSYN-0028` in the PR title:
   move issue from `In Progress` to `In Review`
4. pull request merged with `GEOSYN-0028` in the PR title:
   move issue to `Done`

This gives you a clean operational model:

- first code activity starts work
- opening a PR means review has started
- merging the PR means delivery is complete

## Commit, Branch, and PR Conventions

Always include the Jira key in:

- branch name
- commit message
- PR title

Use:

```text
Branch: GEOSYN-0028-short-description
Commit: GEOSYN-0028: Short task description
PR: GEOSYN-0028: Short task description
```

Replace `0028` with the real Jira issue number in zero-padded form on the ticket you are working on.

## Jira Automation Rules

### Rule 1: Branch Created -> In Progress

Trigger:

- `Branch created`

Conditions:

- branch name contains `GEOSYN-`
- issue status equals `To Do`

Action:

- transition issue to `In Progress`

Why:

- this marks planned work as actively started once a real implementation branch exists

### Rule 2: Commit Created -> In Progress

Trigger:

- `Commit created`

Conditions:

- commit message contains `GEOSYN-`
- issue status equals `To Do`

Action:

- transition issue to `In Progress`

Why:

- catches direct commits or cases where branch creation was missed

Note:

- keep this rule narrow so it does not move tickets backward from `In Review` or `Done`

### Rule 3: Pull Request Created -> In Review

Trigger:

- `Pull request created`

Conditions:

- PR title contains `GEOSYN-`
- issue status equals `In Progress`

Action:

- transition issue to `In Review`

Why:

- this is the cleanest signal that the work is ready for review

### Rule 4: Pull Request Merged -> Done

Trigger:

- `Pull request merged`

Conditions:

- PR title contains `GEOSYN-`
- issue status does not equal `Done`

Action:

- transition issue to `Done`

Optional follow-up actions:

- add comment with merged PR URL
- set resolution if your workflow requires it

Why:

- merging is a much safer completion signal than any individual commit

## Optional Smart Commit Usage

If your team wants commit-message-driven comments or time tracking, use Smart Commits sparingly.

Examples:

```text
GEOSYN-0028: Add event service #comment service implemented
GEOSYN-0028: Wire alerts #time 1h 30m
GEOSYN-0028: Finish alert workflow #transition "In Review"
```

Recommended policy:

- use Smart Commits for comments and time logging
- do not rely on Smart Commits as the primary path to `Done`

## Admin Checklist

Someone with Jira admin and GitHub org access should confirm:

1. `GitHub for Atlassian` is installed in Jira
2. the GitHub org or repo is connected to Jira
3. Jira Automation dev triggers are available:
   `Branch created`, `Commit created`, `Pull request created`, `Pull request merged`
4. workflow statuses exist:
   `To Do`, `In Progress`, `In Review`, `Done`
5. developers use the same email in GitHub and Jira if Smart Commits are enabled
6. GitHub private noreply email mode is disabled if Smart Commits are required

## Recommended Jira Automation Build Order

Set up rules in this order:

1. `Pull request merged -> Done`
2. `Pull request created -> In Review`
3. `Branch created -> In Progress`
4. `Commit created -> In Progress`

Why this order:

- merge and PR signals are the highest-confidence workflow events
- branch and commit rules are useful but noisier

## Practical Advice

- prefer PR-based automation over commit-based automation
- never use a commit rule that moves issues out of `In Review` or `Done`
- do not make every commit add comments, or Jira will get noisy fast
- if one PR legitimately closes several issues, include all issue keys in the PR title or description
- use one ticket per branch when possible

## Suggested Team Policy

Use this simple rule:

`No branch, commit, or PR without a GEOSYN key.`

Then let Jira Automation do the status changes.

That gives you the lowest-friction workflow with the highest signal quality.
