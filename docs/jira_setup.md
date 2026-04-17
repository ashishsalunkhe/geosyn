# Jira + GitHub Workflow Setup

## Goal

Make GeoSyn follow a Jira-linked workflow where:

- every branch references a Jira ticket
- every commit references a Jira ticket
- every PR references a Jira ticket
- Jira automatically shows linked development activity
- optional Smart Commits can transition Jira work items from commit messages

This repo is configured for GitHub, so the recommended setup is:

- GitHub for Atlassian app
- Jira issue keys in branch names, commit messages, and PR titles
- optional Smart Commits in Jira if your company wants commit-driven transitions

For the recommended status automation model, see:

- `docs/jira_automation_playbook.md`

## Official Atlassian References

- Connect GitHub Cloud to Jira:
  https://support.atlassian.com/jira-cloud-administration/docs/integrate-with-github/
- Enable Smart Commits:
  https://support.atlassian.com/jira-cloud-administration/docs/enable-smart-commits/
- Process work items with Smart Commits:
  https://support.atlassian.com/jira-software-cloud/docs/process-issues-with-smart-commits/

## Recommended Company Convention

Your Jira project is `GEOSYN`, so use keys like:

- `GEOSYN-0028`
- `GEOSYN-0245`

The numeric part is not fixed. It should be the actual Jira issue number already assigned to the ticket, written in zero-padded form.
For this project, the next new key after the tickets created so far would be `GEOSYN-0028`.

### Branch naming

Use:

```text
GEOSYN-0028-short-task-description
```

Replace `0028` with the real Jira issue number in zero-padded form.

Examples:

```text
GEOSYN-0028-add-v2-event-service
GEOSYN-0029-backfill-canonical-events
GEOSYN-0030-add-jira-git-hooks
```

### Commit message format

Use:

```text
GEOSYN-0028: Short task description
```

Replace `0028` with the real Jira issue number in zero-padded form.

Examples:

```text
GEOSYN-0028: Add v2 event service
GEOSYN-0029: Backfill canonical events from legacy clusters
GEOSYN-0030: Add Jira-aware git hooks and PR template
```

### PR title format

Use:

```text
GEOSYN-0028: Short task description
```

Replace `0028` with the real Jira issue number in zero-padded form.

## Smart Commit Examples

If Smart Commits are enabled in Jira, you can also do things like:

```text
GEOSYN-0028: Add v2 event service #comment implemented service layer #time 1h 30m
GEOSYN-0028: Wire clustering into canonical events #transition "In Review"
```

Important notes:

- Smart Commits depend on Jira configuration.
- The commit author email must match exactly one Jira user email.
- Transition names must match your Jira workflow status names.

## One-Time Repo Setup

This repo now includes:

- `.gitmessage-jira.txt`
- `.githooks/prepare-commit-msg`
- `.githooks/commit-msg`
- `scripts/setup_jira_git_workflow.sh`
- `scripts/create_jira_backlog.py`
- `.github/pull_request_template.md`

Run this once locally from the repo root:

```bash
bash scripts/setup_jira_git_workflow.sh
```

That will:

- set `core.hooksPath` to `.githooks`
- set the commit template to `.gitmessage-jira.txt`

## What The Hooks Do

### `prepare-commit-msg`

- reads the current branch name
- extracts a Jira issue key like `GEOSYN-0028`
- prefixes the commit message with `GEOSYN-0028: ` if it is missing

The hook accepts any valid Jira key matching the `GEOSYN-<number>` pattern. Team convention is to use zero-padded issue numbers, for example `GEOSYN-0028`.

### `commit-msg`

- validates that the first line of the commit message contains a Jira issue key
- blocks commits that do not reference a ticket

## Jira-Side Setup Checklist

Someone with Jira admin and GitHub org access should verify:

1. Install the GitHub for Atlassian app in Jira.
2. Connect the GitHub organization that contains `ashishsalunkhe/geosyn`.
3. Ensure this repository is included in the Jira app’s repository access.
4. Enable Smart Commits in Jira if you want commit-driven transitions.
5. Confirm your Jira workflow statuses and transition names.
6. Confirm developer emails in Git match Jira user emails.
7. Configure Jira Automation rules using `docs/jira_automation_playbook.md`.

## Creating The Backlog Automatically

The repo now includes a helper script that can create the backlog from `docs/jira_backlog.md`.

Export your credentials first:

```bash
export JIRA_BASE_URL="https://casehumana.atlassian.net"
export JIRA_EMAIL="your-email@example.com"
export JIRA_API_TOKEN="your-token"
export JIRA_PROJECT_KEY="GEOSYN"
```

Dry run first:

```bash
python scripts/create_jira_backlog.py --dry-run
```

Then create the issues:

```bash
python scripts/create_jira_backlog.py
```

The script will write a mapping file to:

```text
docs/jira_created_map.json
```

That file can be used to map:

- Jira ticket -> branch name
- Jira ticket -> commit prefix
- Jira ticket -> implementation area

## What This Gives You

Once Jira and GitHub are connected and the team follows the naming conventions:

- branches show up on Jira work items
- commits show up on Jira work items
- PRs show up on Jira work items
- Smart Commit commands can comment, log time, and transition issues

## Recommended Team Rule

No branch, commit, or PR without a Jira key.

That one rule usually gets you 90% of the automation value with very little overhead.
