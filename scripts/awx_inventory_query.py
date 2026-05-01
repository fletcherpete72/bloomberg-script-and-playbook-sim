# Stub for IAG5 service: awx-inventory-query
# Replace with Bloomberg's actual script when available.
# Set STUB_FORCE_FAIL=1 to simulate failure.

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Query an AWX/Ansible Tower inventory and return host list")
    parser.add_argument("--awx_host", required=True, help="AWX hostname or URL")
    parser.add_argument("--token", required=True, help="AWX API token")
    parser.add_argument("--inventory_name", required=True, help="Inventory name to query")
    args = parser.parse_args()

    if os.environ.get("STUB_FORCE_FAIL"):
        print(json.dumps({"success": False, "error": "forced failure (STUB_FORCE_FAIL set)"}))
        sys.exit(1)

    print(json.dumps({
        "success": True,
        "result": {
            "inventory_name": args.inventory_name,
            "host_count": 3,
            "hosts": [
                {"name": "arista-leaf-01", "enabled": True, "groups": ["leaf", "eos"]},
                {"name": "arista-leaf-02", "enabled": True, "groups": ["leaf", "eos"]},
                {"name": "switch-core-01", "enabled": True, "groups": ["core", "ios-xe"]},
            ]
        }
    }))


if __name__ == "__main__":
    main()
