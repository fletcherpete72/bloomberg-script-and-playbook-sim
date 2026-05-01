# Stub for IAG5 service: project-backup
# Replace with Bloomberg's actual script when available.
# Set STUB_FORCE_FAIL=1 to simulate failure.

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Back up an Itential project to a file")
    parser.add_argument("--itential_host", required=True, help="Itential platform hostname")
    parser.add_argument("--token", required=True, help="Itential API auth token")
    parser.add_argument("--project_name", required=True, help="Project name to back up")
    parser.add_argument("--output_path", required=True, help="Destination file path for the backup")
    args = parser.parse_args()

    if os.environ.get("STUB_FORCE_FAIL"):
        print(json.dumps({"success": False, "error": "forced failure (STUB_FORCE_FAIL set)"}))
        sys.exit(1)

    print(json.dumps({
        "success": True,
        "result": {
            "project_name": args.project_name,
            "output_path": args.output_path,
            "size_bytes": 204800,
            "backed_up_at": "2026-05-01T00:00:00Z",
        }
    }))


if __name__ == "__main__":
    main()
