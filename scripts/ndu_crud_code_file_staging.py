"""
IAG5 service: ndu-crud-code-file-staging

Calls the dbo.crud_code_file_staging stored procedure to record a code file
staging operation in the Itential network device upgrade tracking database.
Replaces the MicrosoftSQL adapter task (task d72b, summary: itential_db_insert)
in the eos_file_staging_run_job_batch workflow of the network_device_upgrade
project.

Original SQL (from transformation ts_construct_db_query_file_staging,
ID 697800f5f40aa73eab464fb3):

    EXEC dbo.crud_code_file_staging
      @SWITCH    = '<target_device>',
      @OS        = '<network_os>',
      @FILENAME  = '<eos_code_filename>',
      @SUCCESS   = '<success>',
      @RESULT    = '<result>'

Note: In the original transformation the @SUCCESS value is extracted from
result.success and @RESULT is JSON-stringified. This script accepts
--result_json (the full result object) and derives success from
result_json["success"].

Adapter instance in original workflow: amsqlent01agl01

Simulator: set MSSQL_SIM_URL=http://localhost:3003 to route calls to the
local Express simulator instead of a real SQL Server instance.

Dependencies (requirements.txt):
    pymssql

IAG5 service definition (iag5-services.yaml):
    - name: ndu-crud-code-file-staging
      type: python-script
      filename: ndu_crud_code_file_staging.py
      working-directory: scripts
      repository: iag5-git-repo
      decorator: ndu-crud-code-file-staging
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
        description="Call dbo.crud_code_file_staging stored procedure"
    )
    parser.add_argument("--host", required=True, help="SQL Server hostname or IP address")
    parser.add_argument("--port", type=lambda x: int(x) if x and x.strip() else 1433, help="SQL Server port (default: 1433)")
    parser.add_argument("--database", required=True, help="Database name")
    parser.add_argument("--target_device", required=True, help="Switch/device name (@SWITCH)")
    parser.add_argument("--network_os", required=True, help="Network OS (@OS)")
    parser.add_argument("--eos_code_filename", required=True, help="EOS code filename (@FILENAME)")
    parser.add_argument("--result_json", required=True, help="Full result object as a JSON string; success is extracted from result.success (@SUCCESS, @RESULT)")
    args = parser.parse_args()

    try:
        result_obj = json.loads(args.result_json)
    except json.JSONDecodeError as e:
        print(json.dumps({"success": False, "error": f"Invalid JSON for --result_json: {e}"}))
        sys.exit(1)

    sim_url = os.environ.get("MSSQL_SIM_URL")
    if sim_url:
        payload = json.dumps({
            "target_device": args.target_device,
            "network_os": args.network_os,
            "eos_code_filename": args.eos_code_filename,
            "result_json": args.result_json,
        }).encode()
        req = urllib.request.Request(
            f"{sim_url.rstrip('/')}/mssql/exec/crud_code_file_staging",
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

    success = str(result_obj.get("success", "")).lower()

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
            EXEC dbo.crud_code_file_staging
              @SWITCH    = %s,
              @OS        = %s,
              @FILENAME  = %s,
              @SUCCESS   = %s,
              @RESULT    = %s
            """,
            (
                args.target_device,
                args.network_os,
                args.eos_code_filename,
                success,
                args.result_json,
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
