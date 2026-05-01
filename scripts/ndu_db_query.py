"""
IAG5 service: ndu-db-query

Queries the Itential network device upgrade tracking database.
Replaces the MicrosoftSQL adapter task (task 6063, summary: db_query)
in the following workflows of the network_device_upgrade project:

    Workflow                                Transformation (task 3d0a)            SQL
    eos_code_upgrade_view_pre_post_diff     ts_construct_db_query_view_diff       SELECT DIFF_RESULT FROM dbo.code_upgrade WHERE SWITCH = '<target_device>'
    eos_file_staging_view_error_query_db    ts_construct_file_staging_db_query_view_error  SELECT RESULT FROM dbo.code_file_staging WHERE SWITCH = '<target_device>'
    eos_patch_file_staging_view_error_query_db  ts_construct_patch_file_staging_db_query_view_error  SELECT RESULT FROM dbo.patch_file_staging WHERE SWITCH = '<target_device>'
    eos_code_upgrade_view_error_query_db    ts_construct_code_upgrade_db_query_view_error  SELECT RESULT FROM dbo.code_upgrade WHERE SWITCH = '<target_device>'
    eos_patch_application_view_error_query_db  ts_construct_patch_application_db_query_view_error  SELECT RESULT FROM dbo.patch_application WHERE SWITCH = '<target_device>'
    eos_patch_application_view_pre_post_diff  ts_construct_patch_db_query_view_diff  SELECT DIFF_RESULT FROM dbo.patch_application WHERE SWITCH = '<target_device>'
    pre_post_check_view_error_db            ts_construct_pre_check_db_query_view_error  SELECT PRE_CHECK_RESULT FROM dbo.code_upgrade_pre_check WHERE SWITCH = '<target_device>'

All seven queries follow the same pattern:
    SELECT <column> FROM dbo.<table> WHERE SWITCH = '<target_device>'

The --table and --column parameters are validated against an allowlist to
prevent SQL injection (table/column names cannot be parameterized in SQL).

Adapter instance in original workflows: amsqlent01agl01
MicrosoftSQL adapter task summary: db_query

Simulator: set MSSQL_SIM_URL=http://localhost:3003 to route calls to the
local Express simulator instead of a real SQL Server instance.

Dependencies (requirements.txt):
    pymssql

IAG5 service definition (iag5-services.yaml):
    - name: ndu-db-query
      type: python-script
      filename: ndu_db_query.py
      working-directory: scripts
      repository: iag5-git-repo
      decorator: ndu-db-query
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

ALLOWED_TABLES = {
    "code_upgrade",
    "code_file_staging",
    "patch_file_staging",
    "patch_application",
    "code_upgrade_pre_check",
}

ALLOWED_COLUMNS = {
    "RESULT",
    "DIFF_RESULT",
    "PRE_CHECK_RESULT",
}


def main():
    parser = argparse.ArgumentParser(
        description="Query Itential network device upgrade tracking database"
    )
    parser.add_argument("--host", required=True, help="SQL Server hostname or IP address")
    parser.add_argument("--port", type=lambda x: int(x) if x and x.strip() else 1433, help="SQL Server port (default: 1433)")
    parser.add_argument("--database", required=True, help="Database name")
    parser.add_argument("--target_device", required=True, help="Switch/device name (SWITCH column value)")
    parser.add_argument(
        "--table",
        required=True,
        choices=sorted(ALLOWED_TABLES),
        help="Table name to query (without dbo. prefix)",
    )
    parser.add_argument(
        "--column",
        required=True,
        choices=sorted(ALLOWED_COLUMNS),
        help="Column to select",
    )
    args = parser.parse_args()

    sim_url = os.environ.get("MSSQL_SIM_URL")
    if sim_url:
        payload = json.dumps({
            "table": args.table,
            "column": args.column,
            "target_device": args.target_device,
        }).encode()
        req = urllib.request.Request(
            f"{sim_url.rstrip('/')}/mssql/query",
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

    # Table and column names are validated by argparse choices — safe to interpolate
    query = f"SELECT [{args.column}] FROM [dbo].[{args.table}] WHERE SWITCH = %s"

    try:
        import pymssql

        conn = pymssql.connect(
            server=args.host,
            port=args.port,
            user=username,
            password=password,
            database=args.database
        )
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query, (args.target_device,))
        rows = cursor.fetchall()

        # Serialize any non-JSON-native types (e.g. datetime)
        for row in rows:
            for key, val in row.items():
                if hasattr(val, "isoformat"):
                    row[key] = val.isoformat()

        print(json.dumps({"success": True, "result": rows}))
        cursor.close()
        conn.close()

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
