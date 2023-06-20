import sys
import json
from typing import Tuple, List, Optional


def get_ips(json_data: dict) -> Tuple[Optional[List[str]], Optional[Exception]]:
    try:
        ip_values = json_data["vm_private_ips"]["value"]

        if "network" in json_data:
            network_values = {}
            if "vms" in json_data["network"]:
                for vm in json_data["network"]["vms"]:
                    name = vm["attributes"]["name"]
                    ip = vm["attributes"]["access_ip_v4"]
                    network_values[name] = ip

            ip_addresses = []
            for name, ip in ip_values.items():
                network_ip = network_values.get(name, "")
                ip_addresses.append(f"{ip} {network_ip}".strip())
            return ip_addresses, None
        else:
            return list(ip_values.values()), None
    except KeyError as e:
        return None, KeyError(f"KeyError: {e} is not found.")


def execute():
    # Check if the correct number of command line arguments are provided
    if len(sys.argv) != 2:
        print("Error: Couldn't find the filename argument")
        sys.exit(1)

    filename = sys.argv[1]

    # Load json data
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(2)
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' does not contain valid JSON.")
        sys.exit(3)

    ip_addresses, e = get_ips(data)

    if e:
        print(f"Error: Error {e} happened while parsing the file data.")
        sys.exit(4)

    if len(ip_addresses) == 0:
        print(f"Error: Couldn't find ip address in {data}")
        sys.exit(5)
    else:
        for ip in ip_addresses:
            print(ip)

    sys.exit(0)