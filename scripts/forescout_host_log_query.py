"""
IAG5 service: forescout-host-log-query

Queries the ForescoutDB Devices_JSON table for host log records matching a
given MAC address. Replaces the MicrosoftSQL adapter task (task e9e6,
summary: host_query_log) in the forescout_host_log_query workflow of the
Forescout_host_query project.

Original SQL (from transformation ts_db_host_query, ID 67c87c00b25cb767ac5bef15):

    SELECT [mac]
          ,[json]
          ,[updateDateTime]
      FROM [ForescoutDB].[dbo].[Devices_JSON]
      where mac = '<host_mac>'

Dependencies (requirements.txt):
    pymssql

IAG5 service definition (iag5-services.yaml):
    - name: forescout-host-log-query
      type: python-script
      filename: forescout_host_log_query.py
      working-directory: scripts
      repository: iag5-git-repo
      decorator: forescout-host-log-query
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
        description="Query ForescoutDB.dbo.Devices_JSON by MAC address"
    )
    parser.add_argument("--host", required=True, help="SQL Server hostname or IP address")
    parser.add_argument("--port", type=int, default=1433, help="SQL Server port (default: 1433)")
    parser.add_argument("--database", default="ForescoutDB", help="Database name (default: ForescoutDB)")
    parser.add_argument("--mac", required=True, help="MAC address to query")
    args = parser.parse_args()

    sim_url = os.environ.get("MSSQL_SIM_URL")
    if sim_url:
        payload = json.dumps({"mac": args.mac}).encode()
        req = urllib.request.Request(
            f"{sim_url.rstrip('/')}/mssql/forescout/devices-json",
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
        cursor = conn.cursor(as_dict=True)

        query = """
            SELECT [mac]
                  ,[json]
                  ,[updateDateTime]
              FROM [dbo].[Devices_JSON]
              WHERE mac = %s
        """
        cursor.execute(query, (args.mac,))
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
