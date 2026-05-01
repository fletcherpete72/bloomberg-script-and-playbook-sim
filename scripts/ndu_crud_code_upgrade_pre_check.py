"""
IAG5 service: ndu-crud-code-upgrade-pre-check

Calls the dbo.crud_code_upgrade_pre_check stored procedure to record pre-check
results for a code upgrade operation in the Itential network device upgrade
tracking database. Replaces the MicrosoftSQL adapter task (task df2c, summary:
itential_db_insert) in the get_pre_checks workflow of the
network_device_upgrade project.

Original SQL (from transformation ts_construct_db_query_pre_check,
ID 69b45f93bfa1c49d7c17759a):

    EXEC dbo.crud_code_upgrade_pre_check
      @SWITCH             = '<target_device>',
      @OS                 = '<network_os>',
      @PRE_CHECK_SUCCESS  = '<pre_check_success>',
      @PRE_CHECK_RESULT   = '<pre_check_result>'

Note: @PRE_CHECK_RESULT is JSON-stringified in the original transformation.
This script accepts --pre_check_result_json as a JSON string.

Adapter instance in original workflow: amsqlent01agl01

Simulator: set MSSQL_SIM_URL=http://localhost:3003 to route calls to the
local Express simulator instead of a real SQL Server instance.

Dependencies (requirements.txt):
    pymssql

IAG5 service definition (iag5-services.yaml):
    - name: ndu-crud-code-upgrade-pre-check
      type: python-script
      filename: ndu_crud_code_upgrade_pre_check.py
      working-directory: scripts
      repository: iag5-git-repo
      decorator: ndu-crud-code-upgrade-pre-check
      secrets:
        - name: mssql-username
          type: env
          target: MSSQL_USERNAME
        - name: mssql-password
          type: env
          target: MSSQL_PASSWORD
"""

import argparse
import json
import os
import sys
import urllib.request


def main():
    parser = argparse.ArgumentParser(
        description="Call dbo.crud_code_upgrade_pre_check stored procedure"
    )
    parser.add_argument("--host", required=True, help="SQL Server hostname or IP address")
    parser.add_argument("--port", type=lambda x: int(x) if x and x.strip() else 1433, help="SQL Server port (default: 1433)")
    parser.add_argument("--database", required=True, help="Database name")
    parser.add_argument("--target_device", required=True, help="Switch/device name (@SWITCH)")
    parser.add_argument("--network_os", required=True, help="Network OS (@OS)")
    parser.add_argument("--pre_check_success", required=True, help="Pre-check success flag — 'true' or 'false' (@PRE_CHECK_SUCCESS)")
    parser.add_argument("--pre_check_result_json", required=True, help="Pre-check result object as a JSON string (@PRE_CHECK_RESULT)")
    args = parser.parse_args()

    sim_url = os.environ.get("MSSQL_SIM_URL")
    if sim_url:
        payload = json.dumps({
            "target_device": args.target_device,
            "network_os": args.network_os,
            "pre_check_success": args.pre_check_success,
            "pre_check_result_json": args.pre_check_result_json,
        }).encode()
        req = urllib.request.Request(
            f"{sim_url.rstrip('/')}/mssql/exec/crud_code_upgrade_pre_check",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            print(resp.read().decode())
        return

    username = os.environ.get("MSSQL_USERNAME")
    password = os.environ.get("MSSQL_PASSWORD")

    if not username or not password:
        print(json.dumps({
            "success": False,
            "error": "MSSQL_USERNAME and MSSQL_PASSWORD environment variables are required"
        }))
        sys.exit(1)

    try:
        import pymssql

        conn = pymssql.connect(
            server=args.host,
            port=args.port,
            user=username,
            password=password,
            database=args.database
        )
        cursor = conn.cursor()

        cursor.execute(
            """
            EXEC dbo.crud_code_upgrade_pre_check
              @SWITCH            = %s,
              @OS                = %s,
              @PRE_CHECK_SUCCESS = %s,
              @PRE_CHECK_RESULT  = %s
            """,
            (
                args.target_device,
                args.network_os,
                args.pre_check_success,
                args.pre_check_result_json,
            )
        )
        conn.commit()

        print(json.dumps({"success": True}))
        cursor.close()
        conn.close()

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
