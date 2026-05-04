"""
IAG5 service: forescout-host-query

Queries the Forescout Web API Plugin to retrieve host properties by MAC address
or IP address. Replaces the genericAdapterRequest (app=Forescout, adapter_id=region)
task in collect_forescout_host_query.

Multi-region support: connection info is taken from region-suffixed environment
variables. The region identifier is normalized to uppercase with hyphens and
spaces converted to underscores before the lookup:

    FORESCOUT_HOST_{REGION}  — Forescout base URL (e.g., https://forescout.example.com)
    FORESCOUT_USER_{REGION}  — API username
    FORESCOUT_PASS_{REGION}  — API password

Example: --region us-east  →  FORESCOUT_HOST_US_EAST, FORESCOUT_USER_US_EAST, ...
         --region emea      →  FORESCOUT_HOST_EMEA, FORESCOUT_USER_EMEA, ...

For testing against the local simulator set region=simulator and:
    FORESCOUT_HOST_SIMULATOR=http://localhost:3001
    FORESCOUT_USER_SIMULATOR=admin   (any non-empty value)
    FORESCOUT_PASS_SIMULATOR=admin   (any non-empty value)

Dependencies (requirements.txt): none (stdlib only)

IAG5 service definition (iag5-services.yaml):
    - name: forescout-host-query
      type: python-script
      filename: forescout_host_query.py
      working-directory: scripts
      repository: iag5-git-repo
      decorator: forescout-host-query
      secrets:
        - name: forescout-host-<region>
          type: env
          target: FORESCOUT_HOST_<REGION>
        - name: forescout-user-<region>
          type: env
          target: FORESCOUT_USER_<REGION>
        - name: forescout-pass-<region>
          type: env
          target: FORESCOUT_PASS_<REGION>
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


def normalize_region(region):
    return region.upper().replace("-", "_").replace(" ", "_")


def strip_mac(mac):
    return re.sub(r"[:\-.]", "", mac).lower()


def forescout_login(base_url, username, password):
    payload = urllib.parse.urlencode({"username": username, "password": password}).encode()
    req = urllib.request.Request(
        f"{base_url}/api/login",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode().strip()


def main():
    parser = argparse.ArgumentParser(
        description="Query Forescout Web API for host data by MAC address or IP address"
    )
    parser.add_argument("--host_info", required=True, help="MAC address or IP address to query")
    parser.add_argument(
        "--is_mac", required=True,
        help="'true' if host_info is a MAC address, 'false' if an IP address",
    )
    parser.add_argument(
        "--region", required=True,
        help="Forescout region identifier (e.g., us-east, emea). Selects the "
             "FORESCOUT_HOST/USER/PASS_<REGION> env vars for this call.",
    )
    args = parser.parse_args()

    is_mac = args.is_mac.lower() in ("true", "1", "yes")
    region_key = normalize_region(args.region)

    base_url = os.environ.get(f"FORESCOUT_HOST_{region_key}", "").rstrip("/")
    username  = os.environ.get(f"FORESCOUT_USER_{region_key}", "")
    password  = os.environ.get(f"FORESCOUT_PASS_{region_key}", "")

    if not base_url or not username or not password:
        print(json.dumps({
            "success": False,
            "error": (
                f"Missing Forescout credentials for region '{args.region}'. "
                f"Required env vars: FORESCOUT_HOST_{region_key}, "
                f"FORESCOUT_USER_{region_key}, FORESCOUT_PASS_{region_key}"
            ),
        }))
        sys.exit(1)

    try:
        token = forescout_login(base_url, username, password)

        if is_mac:
            path = f"/api/hosts/mac/{strip_mac(args.host_info)}"
        else:
            path = f"/api/hosts/ip/{args.host_info}"

        req = urllib.request.Request(
            f"{base_url}{path}",
            headers={"Authorization": token},
            method="GET",
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())

        print(json.dumps({"success": True, "result": result, "response": result}))

    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode()
        except Exception:
            pass
        print(json.dumps({"success": False, "error": f"HTTP {e.code}: {body}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
