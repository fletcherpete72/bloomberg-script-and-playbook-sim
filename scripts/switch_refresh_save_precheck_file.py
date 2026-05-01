# Stub for IAG5 service: switch-refresh-save-precheck-file
# Replace with Bloomberg's actual script when available.
# Set STUB_FORCE_FAIL=1 to simulate failure.

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Save a pre-check output file for a device")
    parser.add_argument("--device", required=True, help="Device hostname")
    parser.add_argument("--filename", required=True, help="Destination filename")
    parser.add_argument("--content", required=True, help="File content to save")
    args = parser.parse_args()

    if os.environ.get("STUB_FORCE_FAIL"):
        print(json.dumps({"success": False, "error": "forced failure (STUB_FORCE_FAIL set)"}))
        sys.exit(1)

    print(json.dumps({
        "success": True,
        "result": {
            "device": args.device,
            "filename": args.filename,
            "bytes_written": len(args.content.encode()),
        }
    }))


if __name__ == "__main__":
    main()
