# Stub for IAG5 service: fs-host-query-epoch (Python component)
# Called from fs_host_query_epoch.yml Ansible playbook.
# Replace with Bloomberg's actual script when available.
# Set STUB_FORCE_FAIL=1 to simulate failure.

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Query Forescout for host info at a given epoch timestamp")
    parser.add_argument("--host", required=True, help="Forescout server hostname or IP")
    parser.add_argument("--mac", required=True, help="Host MAC address to look up")
    parser.add_argument("--epoch", type=int, required=True, help="Epoch timestamp for the query window")
    args = parser.parse_args()

    if os.environ.get("STUB_FORCE_FAIL"):
        print(json.dumps({"success": False, "error": "forced failure (STUB_FORCE_FAIL set)"}))
        sys.exit(1)

    print(json.dumps({
        "success": True,
        "result": {
            "mac": args.mac,
            "epoch": args.epoch,
            "host_info": {
                "ip": "10.0.3.1",
                "hostname": "arista-leaf-01",
                "online": True,
                "last_seen": args.epoch,
            }
        }
    }))


if __name__ == "__main__":
    main()
