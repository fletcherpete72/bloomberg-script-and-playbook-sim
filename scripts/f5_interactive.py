# Stub for IAG5 service: f5-interactive
# Replace with Bloomberg's actual script when available.
# Set STUB_FORCE_FAIL=1 to simulate failure.

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Run an interactive command against an F5 BIG-IP device")
    parser.add_argument("--host", required=True, help="F5 hostname or IP")
    parser.add_argument("--username", required=True, help="F5 username")
    parser.add_argument("--password", required=True, help="F5 password")
    parser.add_argument("--command", required=True, help="iControl REST command or tmsh command to execute")
    parser.add_argument("--partition", default="Common", help="BIG-IP partition (default: Common)")
    args = parser.parse_args()

    if os.environ.get("STUB_FORCE_FAIL"):
        print(json.dumps({"success": False, "error": "forced failure (STUB_FORCE_FAIL set)"}))
        sys.exit(1)

    print(json.dumps({
        "success": True,
        "result": {
            "host": args.host,
            "partition": args.partition,
            "command": args.command,
            "output": "stub output for command",
            "status": "complete",
        }
    }))


if __name__ == "__main__":
    main()
