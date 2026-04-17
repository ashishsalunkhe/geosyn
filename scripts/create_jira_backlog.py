#!/usr/bin/env python3
"""
Create Jira issues from docs/jira_backlog.md.

Required environment variables:
    JIRA_BASE_URL
    JIRA_EMAIL
    JIRA_API_TOKEN

Optional environment variables:
    JIRA_PROJECT_KEY=SCRUM
    JIRA_BACKLOG_DOC=docs/jira_backlog.md

Examples:
    python scripts/create_jira_backlog.py --dry-run
    python scripts/create_jira_backlog.py
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from urllib import error, request


@dataclass
class BacklogTicket:
    ordinal: int
    title: str
    issue_type: str
    priority: str
    description: str
    acceptance_criteria: List[str] = field(default_factory=list)
    epic: Optional[str] = None


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def jira_request(
    method: str,
    path: str,
    email: str,
    api_token: str,
    base_url: str,
    payload: Optional[dict] = None,
) -> dict | list:
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


def parse_backlog(path: Path) -> List[BacklogTicket]:
    text = path.read_text(encoding="utf-8")
    tickets: List[BacklogTicket] = []

    epic_sections = re.split(r"^## Epic: ", text, flags=re.MULTILINE)
    for section in epic_sections[1:]:
        lines = section.splitlines()
        if not lines:
            continue
        epic_name = lines[0].strip()
        body = "\n".join(lines[1:])

        ticket_sections = re.split(r"^### Ticket (\d+)\s*$", body, flags=re.MULTILINE)
        # Structure: [preface, ordinal1, body1, ordinal2, body2, ...]
        for idx in range(1, len(ticket_sections), 2):
            ordinal = int(ticket_sections[idx])
            ticket_body = ticket_sections[idx + 1]

            title_match = re.search(r"^- Title:\s*`?(.*?)`?\s*$", ticket_body, flags=re.MULTILINE)
            type_match = re.search(r"^- Type:\s*(.*?)\s*$", ticket_body, flags=re.MULTILINE)
            priority_match = re.search(r"^- Priority:\s*(.*?)\s*$", ticket_body, flags=re.MULTILINE)

            desc_match = re.search(
                r"^- Description:\s*\n(.*?)(?=^- Acceptance Criteria:|\Z)",
                ticket_body,
                flags=re.MULTILINE | re.DOTALL,
            )
            ac_match = re.search(
                r"^- Acceptance Criteria:\s*\n(.*?)(?=^### Ticket |\Z)",
                ticket_body,
                flags=re.MULTILINE | re.DOTALL,
            )

            description_lines: List[str] = []
            if desc_match:
                for line in desc_match.group(1).splitlines():
                    cleaned = line.strip()
                    if cleaned:
                        description_lines.append(cleaned)

            acceptance_criteria: List[str] = []
            if ac_match:
                for line in ac_match.group(1).splitlines():
                    cleaned = line.strip()
                    if cleaned.startswith("- "):
                        acceptance_criteria.append(cleaned[2:].strip())

            tickets.append(
                BacklogTicket(
                    ordinal=ordinal,
                    title=title_match.group(1).strip() if title_match else f"Ticket {ordinal}",
                    issue_type=type_match.group(1).strip() if type_match else "Task",
                    priority=priority_match.group(1).strip() if priority_match else "Medium",
                    description=" ".join(description_lines).strip(),
                    acceptance_criteria=acceptance_criteria,
                    epic=epic_name,
                )
            )

    return sorted(tickets, key=lambda t: t.ordinal)


def get_issue_type_map(email: str, api_token: str, base_url: str) -> Dict[str, str]:
    issue_types = jira_request("GET", "/rest/api/3/issuetype", email, api_token, base_url)
    return {item["name"].lower(): item["id"] for item in issue_types}


def get_project_issue_type_map(project_key: str, email: str, api_token: str, base_url: str) -> Dict[str, str]:
    project = jira_request("GET", f"/rest/api/3/project/{project_key}", email, api_token, base_url)
    issue_types = project.get("issueTypes", [])
    return {item["name"].lower(): item["id"] for item in issue_types}


def get_priority_map(email: str, api_token: str, base_url: str) -> Dict[str, str]:
    priorities = jira_request("GET", "/rest/api/3/priority", email, api_token, base_url)
    return {item["name"].lower(): item["id"] for item in priorities}


def get_epic_link_field(email: str, api_token: str, base_url: str) -> Optional[str]:
    fields = jira_request("GET", "/rest/api/3/field", email, api_token, base_url)
    for item in fields:
        name = (item.get("name") or "").lower()
        if name == "epic link":
            return item["id"]
    return None


def render_description(ticket: BacklogTicket) -> str:
    parts = [ticket.description.strip()]
    if ticket.acceptance_criteria:
        parts.append("Acceptance Criteria:")
        for criterion in ticket.acceptance_criteria:
            parts.append(f"- {criterion}")
    return "\n".join(part for part in parts if part)


def create_epic(
    epic_name: str,
    project_key: str,
    email: str,
    api_token: str,
    base_url: str,
    issue_type_map: Dict[str, str],
) -> dict:
    epic_issue_type = issue_type_map.get("epic")
    if not epic_issue_type:
        raise ValueError("Jira project does not expose an Epic issue type via the API.")

    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": epic_name,
            "issuetype": {"id": epic_issue_type},
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": f"Created from GeoSyn Jira backlog automation for epic: {epic_name}"}],
                    }
                ],
            },
            "labels": ["geosyn", "automation", "backlog-import", "epic-import"],
        }
    }
    return jira_request("POST", "/rest/api/3/issue", email, api_token, base_url, payload)


def to_adf(text: str) -> dict:
    paragraphs = []
    for block in text.split("\n"):
        if not block.strip():
            continue
        paragraphs.append(
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": block}],
            }
        )
    if not paragraphs:
        paragraphs = [{"type": "paragraph", "content": []}]
    return {"type": "doc", "version": 1, "content": paragraphs}


def create_ticket(
    ticket: BacklogTicket,
    project_key: str,
    email: str,
    api_token: str,
    base_url: str,
    issue_type_map: Dict[str, str],
    priority_map: Dict[str, str],
    epic_link_field: Optional[str],
    epic_key: Optional[str],
) -> dict:
    issue_type_id = issue_type_map.get(ticket.issue_type.lower())
    if not issue_type_id:
        fallback = issue_type_map.get("task") or issue_type_map.get("story")
        if not fallback:
            raise SystemExit(f"Could not resolve Jira issue type for {ticket.issue_type}")
        issue_type_id = fallback

    fields = {
        "project": {"key": project_key},
        "summary": ticket.title,
        "issuetype": {"id": issue_type_id},
        "description": to_adf(render_description(ticket)),
        "labels": ["geosyn", "automation", "backlog-import"],
    }

    priority_id = priority_map.get(ticket.priority.lower())
    if priority_id:
        fields["priority"] = {"id": priority_id}

    if epic_key and epic_link_field:
        fields[epic_link_field] = epic_key
    elif ticket.epic:
        fields["labels"].append(ticket.epic.lower().replace(" ", "-"))

    payload = {"fields": fields}
    return jira_request("POST", "/rest/api/3/issue", email, api_token, base_url, payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Parse and print backlog without creating issues")
    parser.add_argument("--output", default="docs/jira_created_map.json", help="Where to write created ticket mapping")
    args = parser.parse_args()

    project_key = os.environ.get("JIRA_PROJECT_KEY", "SCRUM")
    backlog_doc = Path(os.environ.get("JIRA_BACKLOG_DOC", "docs/jira_backlog.md"))
    tickets = parse_backlog(backlog_doc)

    if args.dry_run:
        dry = [
            {
                "ordinal": t.ordinal,
                "epic": t.epic,
                "title": t.title,
                "issue_type": t.issue_type,
                "priority": t.priority,
            }
            for t in tickets
        ]
        print(json.dumps(dry, indent=2))
        return

    base_url = require_env("JIRA_BASE_URL")
    email = require_env("JIRA_EMAIL")
    api_token = require_env("JIRA_API_TOKEN")

    issue_type_map = get_issue_type_map(email, api_token, base_url)
    project_issue_type_map = get_project_issue_type_map(project_key, email, api_token, base_url)
    priority_map = get_priority_map(email, api_token, base_url)
    epic_link_field = get_epic_link_field(email, api_token, base_url)

    created_epics: Dict[str, str] = {}
    created_tickets: List[dict] = []

    for ticket in tickets:
        epic_key = None
        if ticket.epic:
            if ticket.epic not in created_epics:
                try:
                    epic_issue = create_epic(ticket.epic, project_key, email, api_token, base_url, project_issue_type_map)
                    created_epics[ticket.epic] = epic_issue["key"]
                except ValueError:
                    created_epics[ticket.epic] = ""
            epic_key = created_epics[ticket.epic]

        issue = create_ticket(
            ticket=ticket,
            project_key=project_key,
            email=email,
            api_token=api_token,
            base_url=base_url,
            issue_type_map=project_issue_type_map or issue_type_map,
            priority_map=priority_map,
            epic_link_field=epic_link_field,
            epic_key=epic_key or None,
        )
        created_tickets.append(
            {
                "ordinal": ticket.ordinal,
                "key": issue["key"],
                "title": ticket.title,
                "issue_type": ticket.issue_type,
                "epic": ticket.epic,
            }
        )
        print(f"Created {issue['key']}: {ticket.title}")

    output = {
        "project_key": project_key,
        "epics": created_epics,
        "tickets": created_tickets,
    }
    output_path = Path(args.output)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\nWrote Jira issue mapping to {output_path}")


if __name__ == "__main__":
    main()
