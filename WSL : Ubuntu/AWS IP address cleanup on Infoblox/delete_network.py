import requests
from urllib.parse import quote
import urllib3
import re

USERNAME = "awsapiuser"
PASSWORD = "c7e116f813502ebd834cbbdc78c67a31836a82e4948f25f4ec0c3eaa8b7e4945"
# ---------------- Configuration ----------------
WAPI_BASE = "https://ns3.mediait.ch/wapi/v2.12.2"
NETWORK_VIEW = "default"

auth = (USERNAME, PASSWORD)
verify_ssl = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ---------------- Utility Functions ----------------
def get_objects(object_type, params):
    """Generic GET request for object type."""
    url = f"{WAPI_BASE}/{object_type}"
    resp = requests.get(url, params=params, auth=auth, verify=verify_ssl)
    resp.raise_for_status()
    return resp.json()


def get_networks_in_container(container_network):
    """Get networks directly under a container."""
    return get_objects("network", {
        "network_container": container_network,
        "network_view": NETWORK_VIEW
    })


def get_containers_in_network(container_network):
    """Get sub-containers of a network container."""
    return get_objects("networkcontainer", {
        "network_container": container_network,
        "network_view": NETWORK_VIEW
    })


def get_container_by_network(network):
    """Get container by network address."""
    res = get_objects("networkcontainer", {
        "network": network,
        "network_view": NETWORK_VIEW
    })
    return res[0] if res else None


def delete_object(_ref):
    """Delete object by _ref."""
    url = f"{WAPI_BASE}/{_ref}"
    resp = requests.delete(url, auth=auth, verify=verify_ssl)
    
    if resp.status_code == 404 or "could not be found" in resp.text:
        print(f"Object already deleted: {_ref}")
        return
    
    if resp.status_code in [200, 204]:
        print(f"Deleted {_ref}")
    else:
        print(f"Failed to delete {_ref}: {resp.text}")


# ---------------- Recursive Deletion ----------------
def delete_network_container_recursively(network, seen=None, depth=0):
    """Delete container and all sub-containers/networks recursively."""
    if seen is None:
        seen = set()
    if network in seen:
        return
    seen.add(network)

    indent = "  " * depth
    print(f"{indent}Processing container {network}")

    # Delete sub-containers first
    sub_containers = get_containers_in_network(network)
    for c in sub_containers:
        sub_net = c["network"]
        if sub_net != network:
            delete_network_container_recursively(sub_net, seen, depth + 1)

    # Delete networks in this container
    networks = get_networks_in_container(network)
    for n in networks:
        print(f"{indent}  Deleting network {n['network']}")
        delete_object(n["_ref"])

    # Delete the container itself
    container = get_container_by_network(network)
    if container:
        ref = container["_ref"]
        print(f"{indent}  Deleting container {network}")
        delete_object(ref)
    else:
        print(f"{indent}  Container {network} not found")


# ---------------- Deletion Planning ----------------
def plan_deletion(network, depth=0, seen=None):
    """Print deletion plan recursively."""
    if seen is None:
        seen = set()
    if network in seen:
        return
    seen.add(network)

    indent = "  " * depth
    print(f"{indent}- Container: {network}")

    sub_containers = get_containers_in_network(network)
    for c in sub_containers:
        sub_net = c["network"]
        if sub_net != network:
            plan_deletion(sub_net, depth + 1, seen)

    networks = get_networks_in_container(network)
    for n in networks:
        print(f"{indent}  - Network: {n['network']}")


# ---------------- Main Execution ----------------
if __name__ == "__main__":

    network_input = input("Enter the network container to delete (format X.X.X.X/X): ")
    if not re.match(r"^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$", network_input):
        print("Invalid format. Exiting.")
        exit(1)

    NETWORK_CONTAINER = network_input

    print(f"\nDeletion plan for container {NETWORK_CONTAINER}:\n")
    plan_deletion(NETWORK_CONTAINER)

    confirm = input("\nConfirm deletion of all listed items? (yes/no): ")
    if confirm.lower() in ["YES", "yes"]:
        delete_network_container_recursively(NETWORK_CONTAINER)
    else:
        print("Deletion canceled.")
