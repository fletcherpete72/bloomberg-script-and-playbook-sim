# Stub for IAG5 service: ping-ip
# Replace with Bloomberg's actual script when available.
# Set STUB_FORCE_FAIL=1 to simulate failure.

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Ping a list of IP addresses and return reachability results")
    parser.add_argument("--hosts", required=True, help="Comma-separated list of IP addresses to ping")
    parser.add_argument("--count", type=int, default=4, help="Number of ping packets per host (default: 4)")
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
            "details": {h: {"reachable": True, "packet_loss_pct": 0, "avg_rtt_ms": 0.8} for h in hosts},
        }
    }))


if __name__ == "__main__":
    main()
