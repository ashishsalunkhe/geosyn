#!/usr/bin/env python3
"""
Transition Jira issues to target statuses using Jira Cloud REST API.

Required environment variables:
    JIRA_BASE_URL
    JIRA_EMAIL
    JIRA_API_TOKEN

Usage:
    python scripts/update_jira_statuses.py docs/jira_status_updates.json
"""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
from urllib import error, request


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def jira_request(method: str, path: str, email: str, api_token: str, base_url: str, payload: dict | None = None) -> dict | list:
    auth_raw = f"{email}:{api_token}".encode("utf-8")
    auth_header = base64.b64encode(auth_raw).decode("ascii")
    url = f"{base_url.rstrip('/')}{path}"
    data = None
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Accept": "application/json",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = request.Request(url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Jira API error {exc.code} for {method} {path}: {body}") from exc


def find_transition(issue_key: str, target_status: str, email: str, api_token: str, base_url: str) -> str | None:
    data = jira_request("GET", f"/rest/api/3/issue/{issue_key}/transitions", email, api_token, base_url)
    transitions = data.get("transitions", [])
    lowered_target = target_status.lower()
    for transition in transitions:
        to_name = (transition.get("to", {}).get("name") or "").lower()
        transition_name = (transition.get("name") or "").lower()
        if lowered_target == to_name or lowered_target == transition_name:
            return transition["id"]
    for transition in transitions:
        to_name = (transition.get("to", {}).get("name") or "").lower()
        transition_name = (transition.get("name") or "").lower()
        if lowered_target in to_name or lowered_target in transition_name:
            return transition["id"]
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mapping_file", help="JSON file mapping issue keys to target statuses")
    args = parser.parse_args()

    base_url = require_env("JIRA_BASE_URL")
    email = require_env("JIRA_EMAIL")
    api_token = require_env("JIRA_API_TOKEN")

    mapping = json.loads(Path(args.mapping_file).read_text(encoding="utf-8"))
    for issue_key, target_status in mapping.items():
        transition_id = find_transition(issue_key, target_status, email, api_token, base_url)
        if not transition_id:
            print(f"Skipping {issue_key}: no transition found for target status '{target_status}'")
            continue
        jira_request(
            "POST",
            f"/rest/api/3/issue/{issue_key}/transitions",
            email,
            api_token,
            base_url,
            payload={"transition": {"id": transition_id}},
        )
        print(f"Updated {issue_key} -> {target_status}")


if __name__ == "__main__":
    main()
