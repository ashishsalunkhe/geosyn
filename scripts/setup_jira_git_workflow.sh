#!/usr/bin/env bash
set -euo pipefail

git config core.hooksPath .githooks
git config commit.template .gitmessage-jira.txt

echo "Configured Jira-aware git workflow for this repo."
echo "Hooks path: .githooks"
echo "Commit template: .gitmessage-jira.txt"
echo
echo "Recommended branch format: GEOSYN-123-short-description"
echo "Recommended commit format: GEOSYN-123: short task description"
