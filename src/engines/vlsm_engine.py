from __future__ import annotations

import math
from ipaddress import IPv4Address, IPv4Network
from typing import Dict, List, Sequence


def smallest_valid_prefix(hosts: int) -> int:
    if hosts <= 0:
        raise ValueError("Host requirement must be positive")
    required_addresses = hosts + 2
    bits = max(1, math.ceil(math.log2(required_addresses)))
    return 32 - bits


def wildcard_mask_from_prefix(prefix: int) -> str:
    if prefix < 0 or prefix > 32:
        raise ValueError("Prefix must be between 0 and 32")
    net = IPv4Network(f"0.0.0.0/{prefix}", strict=False)
    mask_int = int(net.netmask)
    wildcard_int = ((1 << 32) - 1) ^ mask_int
    return str(IPv4Address(wildcard_int))


def allocate_vlsm(root_network: str, host_requirements: Sequence[int | Dict[str, int] | Dict[str, object]]) -> List[Dict[str, object]]:
    root = IPv4Network(root_network, strict=False)
    if root.num_addresses < 2:
        raise ValueError("Root network is too small for VLSM allocation")

    normalized = []
    for idx, item in enumerate(host_requirements, start=1):
        if isinstance(item, dict):
            name = str(item.get("name", f"subnet_{idx}"))
            hosts = int(item.get("hosts", item.get("host_count", 0)))
        else:
            name = f"subnet_{idx}"
            hosts = int(item)
        if hosts <= 0:
            raise ValueError(f"Subnet '{name}' requires a positive host count")
        normalized.append({"name": name, "hosts": hosts})

    allocations: List[Dict[str, object]] = []
    current_network = root.network_address

    for item in sorted(normalized, key=lambda x: x["hosts"], reverse=True):
        hosts = int(item["hosts"])
        prefix = smallest_valid_prefix(hosts)
        subnet = IPv4Network(f"{current_network}/{prefix}", strict=False)

        if subnet.network_address < root.network_address or subnet.broadcast_address > root.broadcast_address:
            raise ValueError("Subnet allocation exceeds the root network boundaries")

        if current_network + subnet.num_addresses > (root.broadcast_address + 1):
            raise ValueError("Root network exhausted before all subnets were allocated")

        usable_hosts = list(subnet.hosts())
        if len(usable_hosts) == 0:
            raise ValueError(f"No usable addresses available for subnet '{item['name']}'")
        if hosts > len(usable_hosts):
            raise ValueError(f"Subnet '{item['name']}' requires more usable addresses than allocated")

        default_gateway = usable_hosts[0]
        first_usable = usable_hosts[0]
        last_usable = usable_hosts[-1]
        total_usable = len(usable_hosts)
        efficiency = round((hosts / total_usable) * 100, 2)

        allocations.append(
            {
                "name": item["name"],
                "host_requirement": hosts,
                "prefix": prefix,
                "network_address": str(subnet.network_address),
                "subnet_mask": str(subnet.netmask),
                "wildcard_mask": wildcard_mask_from_prefix(prefix),
                "first_usable": str(first_usable),
                "last_usable": str(last_usable),
                "default_gateway": str(default_gateway),
                "broadcast_address": str(subnet.broadcast_address),
                "total_usable_addresses": total_usable,
                "address_utilization_efficiency": efficiency,
                "explanation": (
                    f"Allocated a /{prefix} subnet because {hosts} hosts require {total_usable} usable addresses, "
                    f"which provides {efficiency}% utilization without overlapping adjacent allocations."
                ),
            }
        )
        current_network = subnet.broadcast_address + 1

    return allocations
