# Stub for IAG5 service: switch-refresh-save-site-devices
# Replace with Bloomberg's actual script when available.
# Set STUB_FORCE_FAIL=1 to simulate failure.

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Persist the device list for a site to storage")
    parser.add_argument("--site", required=True, help="Site name")
    parser.add_argument("--devices", required=True, help="JSON array of device hostnames")
    args = parser.parse_args()

    if os.environ.get("STUB_FORCE_FAIL"):
        print(json.dumps({"success": False, "error": "forced failure (STUB_FORCE_FAIL set)"}))
        sys.exit(1)

    try:
        devices = json.loads(args.devices)
    except json.JSONDecodeError:
        print(json.dumps({"success": False, "error": "devices must be a valid JSON array"}))
        sys.exit(1)

    print(json.dumps({
        "success": True,
        "result": {
            "site": args.site,
            "device_count": len(devices),
            "devices": devices,
        }
    }))


if __name__ == "__main__":
    main()
