#!/usr/bin/env python3
"""
Dynamic Ansible Inventory Script
Reads JSON from stdin and converts it to Ansible inventory format.

Input format:
{
    "inventory_nodes": [
        {
            "name": "host-name",
            "attributes": {
                "ansible_host": "hostname",
                "ansible_user": "user",
                ...
            }
        }
    ]
}

Usage:
  cat input.json | ./dynamic_inventory.py
  echo '{"inventory_nodes":[...]}' | ansible-playbook -i ./dynamic_inventory.py playbook.yml
"""

import json
import sys

def read_stdin():
    """Read JSON data from stdin."""
    try:
        data = json.load(sys.stdin)
        return data
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading stdin: {e}", file=sys.stderr)
        sys.exit(1)


def build_inventory(data):
    """
    Convert input data to Ansible dynamic inventory format.
    
    Returns a dictionary with the structure:
    {
        "_meta": {
            "hostvars": {
                "hostname": { "var": "value", ... }
            }
        },
        "all": {
            "hosts": ["host1", "host2", ...],
            "vars": {}
        }
    }
    """
    inventory = {
        "_meta": {
            "hostvars": {}
        },
        "all": {
            "hosts": [],
            "vars": {}
        }
    }
    
    # Process inventory nodes
    nodes = data.get("inventory_nodes", [])
    
    for node in nodes:
        name = node.get("name")
        attributes = node.get("attributes", {})
        
        if not name:
            print("Warning: Node missing 'name' field, skipping", file=sys.stderr)
            continue
        
        # Add host to 'all' group
        inventory["all"]["hosts"].append(name)
        
        # Add host variables
        if attributes:
            inventory["_meta"]["hostvars"][name] = attributes
    
    return inventory


def main():    
    # Read from stdin and build inventory
    data = read_stdin()
    inventory = build_inventory(data)
    print(json.dumps(inventory, indent=2))

if __name__ == "__main__":
    main()
