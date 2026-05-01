# Stub for IAG5 service: refresh-post-check
# Replace with Bloomberg's actual script when available.
# Set STUB_FORCE_FAIL=1 to simulate failure.

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Run post-check commands and diff against pre-check snapshot")
    parser.add_argument("--host", required=True, help="Device hostname or IP")
    parser.add_argument("--username", required=True, help="Device username")
    parser.add_argument("--password", required=True, help="Device password")
    parser.add_argument("--pre_check_snapshot", required=True, help="Pre-check snapshot as a JSON string")
    args = parser.parse_args()

    if os.environ.get("STUB_FORCE_FAIL"):
        print(json.dumps({"success": False, "error": "forced failure (STUB_FORCE_FAIL set)"}))
        sys.exit(1)

    print(json.dumps({
        "success": True,
        "result": {
            "host": args.host,
            "checks_passed": True,
            "diff": {
                "added": [],
                "removed": [],
                "changed": [],
            },
            "post_check_output": {
                "version": "stub-4.29.1F",
                "uptime": "0 days 0:01:23",
                "interface_count": 48,
                "bgp_neighbors_up": 4,
            }
        }
    }))


if __name__ == "__main__":
    main()
