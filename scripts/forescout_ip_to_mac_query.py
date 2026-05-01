"""
IAG5 service: forescout-ip-to-mac-query

Queries the ForescoutDB Devices table to resolve an IP address to a MAC
address. Replaces the MicrosoftSQL adapter task (task f470, summary:
ip_query_mac) in the forescout_host_log_query workflow of the
Forescout_host_query project.

Original SQL (from transformation ts_db_ip_to_mac_query, ID 67c781a5b25cb767ac5bef14):

    SELECT [mac]
          ,[ip]
      FROM [ForescoutDB].[dbo].[Devices]
      WHERE ip = '<ip>'

Note: the workflow input variable is named normalized_ip ($var.job.normalized_ip)
but the transformation parameter is named normalized_mac — this is a naming
inconsistency in the original workflow. The value passed is an IP address.

Dependencies (requirements.txt):
    pymssql

IAG5 service definition (iag5-services.yaml):
    - name: forescout-ip-to-mac-query
      type: python-script
      filename: forescout_ip_to_mac_query.py
      working-directory: scripts
      repository: iag5-git-repo
      decorator: forescout-ip-to-mac-query
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
        description="Query ForescoutDB.dbo.Devices to resolve IP address to MAC address"
    )
    parser.add_argument("--host", required=True, help="SQL Server hostname or IP address")
    parser.add_argument("--port", type=int, default=1433, help="SQL Server port (default: 1433)")
    parser.add_argument("--database", default="ForescoutDB", help="Database name (default: ForescoutDB)")
    parser.add_argument("--ip", required=True, help="IP address to resolve to MAC")
    args = parser.parse_args()

    sim_url = os.environ.get("MSSQL_SIM_URL")
    if sim_url:
        payload = json.dumps({"ip": args.ip}).encode()
        req = urllib.request.Request(
            f"{sim_url.rstrip('/')}/mssql/forescout/devices",
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
                  ,[ip]
              FROM [dbo].[Devices]
              WHERE ip = %s
        """
        cursor.execute(query, (args.ip,))
        rows = cursor.fetchall()

        print(json.dumps({"success": True, "result": rows}))
        cursor.close()
        conn.close()

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
