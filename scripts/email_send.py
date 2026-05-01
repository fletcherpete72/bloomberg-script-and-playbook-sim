# Stub for IAG5 service: email-send
# Replace with Bloomberg's actual script when available.
# Set STUB_FORCE_FAIL=1 to simulate failure.

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Send an email via SMTP")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--body", required=True, help="Email body text")
    parser.add_argument("--smtp_host", required=True, help="SMTP server hostname")
    parser.add_argument("--smtp_port", type=int, default=25, help="SMTP port (default: 25)")
    parser.add_argument("--from_addr", default="no-reply@bloomberg.com", help="Sender address")
    args = parser.parse_args()

    if os.environ.get("STUB_FORCE_FAIL"):
        print(json.dumps({"success": False, "error": "forced failure (STUB_FORCE_FAIL set)"}))
        sys.exit(1)

    print(json.dumps({
        "success": True,
        "result": {
            "to": args.to,
            "subject": args.subject,
            "smtp_host": args.smtp_host,
            "smtp_port": args.smtp_port,
            "delivered": True,
        }
    }))


if __name__ == "__main__":
    main()
