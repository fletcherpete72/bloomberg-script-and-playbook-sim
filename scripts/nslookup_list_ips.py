# Stub for IAG5 service: nslookup-list-ips
# Replace with Bloomberg's actual script when available.
# Verify this service has a confirmed workflow caller before developing.
# Set STUB_FORCE_FAIL=1 to simulate failure.

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Resolve a list of hostnames to IP addresses via DNS")
    parser.add_argument("--hostnames", required=True, help="Comma-separated list of hostnames to resolve")
    args = parser.parse_args()

    if os.environ.get("STUB_FORCE_FAIL"):
        print(json.dumps({"success": False, "error": "forced failure (STUB_FORCE_FAIL set)"}))
        sys.exit(1)

    hostnames = [h.strip() for h in args.hostnames.split(",") if h.strip()]
    results = {}
    stub_ips = ["10.0.1.1", "10.0.1.2", "10.0.2.1", "10.0.3.1", "10.0.4.1"]
    for i, hostname in enumerate(hostnames):
        results[hostname] = stub_ips[i % len(stub_ips)]

    print(json.dumps({
        "success": True,
        "result": {
            "resolved": results,
            "failed": [],
        }
    }))


if __name__ == "__main__":
    main()
