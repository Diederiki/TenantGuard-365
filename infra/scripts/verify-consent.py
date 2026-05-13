#!/usr/bin/env python3
"""Compare granted Graph application scopes against the platform's required set.

Usage:
    export ENTRA_TENANT_ID=...
    export COLLECTOR_CLIENT_ID=...
    export COLLECTOR_CLIENT_SECRET=...
    python verify-consent.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request

REQUIRED_APP_SCOPES = [
    "User.Read.All",
    "Group.Read.All",
    "GroupMember.Read.All",
    "RoleManagement.Read.Directory",
    "Organization.Read.All",
    "Sites.Read.All",
    "Files.Read.All",
    "MailboxSettings.Read",
    "Reports.Read.All",
    "ServiceHealth.Read.All",
    "ServiceMessage.Read.All",
    "Team.ReadBasic.All",
    "Channel.ReadBasic.All",
    "TeamMember.Read.All",
    "Application.Read.All",
    "AuditLog.Read.All",
]


def acquire_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    body = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }
    ).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:  # noqa: S310 known-https
        return json.loads(r.read())["access_token"]


def fetch_granted(token: str, client_id: str) -> set[str]:
    url = (
        "https://graph.microsoft.com/v1.0/servicePrincipals"
        f"(appId='{client_id}')/appRoleAssignments"
    )
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as r:  # noqa: S310
        data = json.loads(r.read())
    return {row.get("resourceDisplayName", "") for row in data.get("value", [])}


def main() -> int:
    tenant = os.environ.get("ENTRA_TENANT_ID")
    cid = os.environ.get("COLLECTOR_CLIENT_ID")
    sec = os.environ.get("COLLECTOR_CLIENT_SECRET")
    if not (tenant and cid and sec):
        print("ENTRA_TENANT_ID / COLLECTOR_CLIENT_ID / COLLECTOR_CLIENT_SECRET required")
        return 2
    token = acquire_token(tenant, cid, sec)
    granted = fetch_granted(token, cid)
    missing = [s for s in REQUIRED_APP_SCOPES if not any(s in g for g in granted)]
    print("Granted:")
    for g in sorted(granted):
        print(f"  {g}")
    if missing:
        print("\nMISSING scopes:")
        for m in missing:
            print(f"  - {m}")
        return 1
    print("\nAll required scopes appear granted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
