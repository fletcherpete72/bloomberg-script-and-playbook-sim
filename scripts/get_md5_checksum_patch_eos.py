# Stub for IAG5 service: get-md5-checksum-patch-eos
# Replace with Bloomberg's actual script when available.
# Set STUB_FORCE_FAIL=1 to simulate failure.

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Fetch the MD5 checksum of an EOS patch image from a device")
    parser.add_argument("--host", required=True, help="Device hostname or IP")
    parser.add_argument("--username", required=True, help="Device username")
    parser.add_argument("--password", required=True, help="Device password")
    parser.add_argument("--filename", required=True, help="EOS patch filename to checksum")
    args = parser.parse_args()

    if os.environ.get("STUB_FORCE_FAIL"):
        print(json.dumps({"success": False, "error": "forced failure (STUB_FORCE_FAIL set)"}))
        sys.exit(1)

    print(json.dumps({
        "success": True,
        "result": {
            "host": args.host,
            "filename": args.filename,
            "md5": "b026324c6904b2a9cb4b88d6d61c81d1",
            "verified": True,
        }
    }))


if __name__ == "__main__":
    main()
