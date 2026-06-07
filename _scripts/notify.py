#!/usr/bin/env python3
"""Send notifications when the stats sync pipeline has an issue.

Email: Gmail SMTP with App Password stored in macOS keychain.
Banner: macOS osascript notification.

Keychain setup (one-time):
    security add-generic-password -a default -s mobetter-stats-gmail-app-pw -w "<GMAIL_APP_PW>"

Generate a Gmail App Password at https://myaccount.google.com/apppasswords
(requires 2-Step Verification to be enabled).

If the keychain item is missing, email is skipped but the banner still fires.

Library use:
    from notify import notify
    notify("Garmin sync failed", "detail...")

CLI (for testing):
    python3 _scripts/notify.py "subject" "body"
"""

from __future__ import annotations

import os
import smtplib
import subprocess
import sys
from email.message import EmailMessage

EMAIL_TO = os.environ.get("NOTIFY_EMAIL", "")  # set NOTIFY_EMAIL to receive notifications; empty = email skipped, banner still fires
EMAIL_FROM = EMAIL_TO
GMAIL_PW_SERVICE = "mobetter-stats-gmail-app-pw"
GMAIL_PW_ACCOUNT = "default"


def keychain_get(service: str, account: str = "default") -> str | None:
    proc = subprocess.run(
        ["security", "find-generic-password", "-a", account, "-s", service, "-w"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def send_email(subject: str, body: str) -> tuple[bool, str]:
    if not EMAIL_TO:
        return False, "no recipient (set NOTIFY_EMAIL)"
    pw = keychain_get(GMAIL_PW_SERVICE, GMAIL_PW_ACCOUNT)
    if not pw:
        return False, "no keychain password (skipped)"
    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as s:
            s.login(EMAIL_FROM, pw)
            s.send_message(msg)
        return True, "sent"
    except Exception as e:  # noqa: BLE001
        return False, f"smtp error: {e}"


def mac_banner(subject: str, body: str) -> None:
    safe_subject = subject.replace('"', '\\"')[:100]
    safe_body = body.replace('"', '\\"')[:200]
    subprocess.run(
        ["osascript", "-e", f'display notification "{safe_body}" with title "{safe_subject}"'],
        capture_output=True,
    )


def notify(subject: str, body: str) -> dict[str, str]:
    ok, status = send_email(subject, body)
    mac_banner(subject, body)
    return {"email_ok": "1" if ok else "0", "email_status": status}


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: notify.py SUBJECT BODY", file=sys.stderr)
        return 2
    result = notify(sys.argv[1], "\n".join(sys.argv[2:]))
    print(result)
    return 0 if result["email_ok"] == "1" else 1


if __name__ == "__main__":
    sys.exit(main())
