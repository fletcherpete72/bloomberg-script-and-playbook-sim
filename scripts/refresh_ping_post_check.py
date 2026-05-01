# Stub for IAG5 service: refresh-ping-post-check
# Replace with Bloomberg's actual script when available.
# Set STUB_FORCE_FAIL=1 to simulate failure.

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Ping a list of IPs and verify reachability after refresh")
    parser.add_argument("--hosts", required=True, help="Comma-separated list of IP addresses to ping")
    parser.add_argument("--expected_count", type=int, default=0,
                        help="Expected number of reachable hosts (0 = all must respond)")
    args = parser.parse_args()

    if os.environ.get("STUB_FORCE_FAIL"):
        print(json.dumps({"success": False, "error": "forced failure (STUB_FORCE_FAIL set)"}))
        sys.exit(1)

    hosts = [h.strip() for h in args.hosts.split(",") if h.strip()]
    print(json.dumps({
        "success": True,
        "result": {
            "total": len(hosts),
            "reachable": len(hosts),
            "unreachable": [],
            "details": {h: {"reachable": True, "rtt_ms": 1.2} for h in hosts},
        }
    }))


if __name__ == "__main__":
    main()
