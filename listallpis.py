import socket
from typing import Dict

import nmap

mapp_oakville = {
    "pi5": "Snack Shack Left",
    "pi2": "Snack Shack Right",
    "pi3": "Check in Left",  # ssh snackshack_left@192.168.50.51
}


def scan_network_for_pis() -> Dict[str, str]:
    """
    Scans local network for devices with 'pi' in their hostname.
    Returns dict mapping hostnames to IP addresses.
    """
    scanner = nmap.PortScanner()
    pi_devices = {}

    try:
        # Get local IP to determine network range
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        # Construct network range (e.g. 192.168.1.0/24)
        network = ".".join(local_ip.split(".")[:-1]) + ".0/24"

        # Scan network
        scanner.scan(hosts=network, arguments="-sn")

        # Check each responding host
        for host in scanner.all_hosts():
            try:
                hostname = socket.gethostbyaddr(host)[0].lower()
                if "pi" in hostname:
                    print(f"Found : {hostname}")
                    pi_devices[mapp_oakville[hostname]] = host

            except socket.herror:
                continue

    except Exception as e:
        print(f"Error scanning network: {e}")
        return {}

    return pi_devices


if __name__ == "__main__":
    results = scan_network_for_pis()
    if results:
        print("Found Pi devices:")
        for name, ip in results.items():
            print(f"{name}: {ip}")
    else:
        print("No Pi devices found")
