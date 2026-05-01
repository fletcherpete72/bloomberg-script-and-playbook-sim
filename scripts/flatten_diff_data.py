# Stub for IAG5 service: flatten-diff-data
# Replace with Bloomberg's actual script when available.
# Set STUB_FORCE_FAIL=1 to simulate failure.

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Flatten structured diff data into a human-readable string")
    parser.add_argument("--device", required=True, help="Device hostname the diff relates to")
    parser.add_argument("--diff_result", required=True, help="Diff result object as a JSON string")
    args = parser.parse_args()

    if os.environ.get("STUB_FORCE_FAIL"):
        print(json.dumps({"success": False, "error": "forced failure (STUB_FORCE_FAIL set)"}))
        sys.exit(1)

    try:
        diff = json.loads(args.diff_result)
    except json.JSONDecodeError:
        print(json.dumps({"success": False, "error": "diff_result must be valid JSON"}))
        sys.exit(1)

    added = diff.get("added", [])
    removed = diff.get("removed", [])
    changed = diff.get("changed", [])

    lines = []
    for item in added:
        lines.append(f"+ {item}")
    for item in removed:
        lines.append(f"- {item}")
    for item in changed:
        lines.append(f"~ {item}")

    print(json.dumps({
        "success": True,
        "result": {
            "device": args.device,
            "flat_diff": "\n".join(lines) if lines else "No differences",
            "added_count": len(added),
            "removed_count": len(removed),
            "changed_count": len(changed),
        }
    }))


if __name__ == "__main__":
    main()
