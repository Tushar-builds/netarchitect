from __future__ import annotations

from typing import Any, Dict, List


def generate_cisco_configs(profile_name: str, profile: Dict[str, Any], vlsm_allocations: List[Dict[str, Any]], routing_summary: Dict[str, Any]) -> List[str]:
    name = profile_name.lower()
    if name in {"campus", "campus_lan"}:
        return _generate_campus_configs(vlsm_allocations, routing_summary)
    if name in {"metro", "metro_man"}:
        return _generate_metro_configs(vlsm_allocations, routing_summary)
    if name in {"global", "global_wan"}:
        return _generate_global_configs(vlsm_allocations, routing_summary)
    return _generate_generic_configs(vlsm_allocations, routing_summary)


def _generate_campus_configs(vlsm_allocations: List[Dict[str, Any]], routing_summary: Dict[str, Any]) -> List[str]:
    blocks = [
        {
            "hostname": "CORE-01",
            "type": "router",
            "subnet": vlsm_allocations[0] if vlsm_allocations else {"network_address": "192.168.10.0", "subnet_mask": "255.255.255.0"},
            "description": "Campus core router",
        },
        {
            "hostname": "DIST-01",
            "type": "switch",
            "description": "Distribution switch",
        },
        {
            "hostname": "ACCESS-01",
            "type": "switch",
            "description": "Access switch",
        },
    ]
    lines: List[str] = []
    for block in blocks:
        lines.append(f"hostname {block['hostname']}")
        lines.append(f"! {block['description']}")
        if block["type"] == "router":
            subnet = block["subnet"]
            lines.append("interface GigabitEthernet0/0")
            lines.append(f" description {block['description']}")
            lines.append(f" ip address {subnet['network_address']} {subnet['subnet_mask']}")
            lines.append(" no shutdown")
            lines.append("!")
            lines.append("router ospf 1")
            lines.append(f" network {subnet['network_address']} 0.0.0.255 area 0")
            lines.append(" default-information originate")
            lines.append("!")
        else:
            lines.append("vlan 10")
            lines.append(" name DATA")
            lines.append("vlan 20")
            lines.append(" name VOICE")
            lines.append("interface Vlan10")
            lines.append(" description DATA_SVI")
            lines.append(" ip address 192.168.10.10 255.255.255.0")
            lines.append(" no shutdown")
            lines.append("!")
            lines.append("interface Vlan20")
            lines.append(" description VOICE_SVI")
            lines.append(" ip address 192.168.20.10 255.255.255.0")
            lines.append(" no shutdown")
            lines.append("!")
            lines.append("interface GigabitEthernet0/1")
            lines.append(" description Access port")
            lines.append(" switchport mode access")
            lines.append(" switchport access vlan 10")
            lines.append(" spanning-tree portfast")
            lines.append("!")
            lines.append("interface GigabitEthernet0/2")
            lines.append(" description Trunk to core")
            lines.append(" switchport mode trunk")
            lines.append(" switchport trunk allowed vlan 10,20")
            lines.append(" spanning-tree link-type point-to-point")
            lines.append("!")
            lines.append("access-list 101 permit tcp any any eq 443")
            lines.append("!")
    return ["\n".join(lines)]


def _generate_metro_configs(vlsm_allocations: List[Dict[str, Any]], routing_summary: Dict[str, Any]) -> List[str]:
    blocks = [
        {"hostname": "HQ-RTR-01", "subnet": vlsm_allocations[0] if vlsm_allocations else {"network_address": "10.0.0.0", "subnet_mask": "255.255.255.0"}},
        {"hostname": "BRANCH-01", "subnet": vlsm_allocations[1] if len(vlsm_allocations) > 1 else {"network_address": "10.0.1.0", "subnet_mask": "255.255.255.0"}},
        {"hostname": "BRANCH-02", "subnet": vlsm_allocations[2] if len(vlsm_allocations) > 2 else {"network_address": "10.0.2.0", "subnet_mask": "255.255.255.0"}},
    ]
    lines: List[str] = []
    for block in blocks:
        subnet = block["subnet"]
        lines.append(f"hostname {block['hostname']}")
        lines.append("!")
        lines.append("interface GigabitEthernet0/0")
        lines.append(f" description {block['hostname']} LAN")
        lines.append(f" ip address {subnet['network_address']} {subnet['subnet_mask']}")
        lines.append(" no shutdown")
        lines.append("!")
        lines.append("router ospf 1")
        lines.append(f" network {subnet['network_address']} 0.0.0.255 area 0")
        lines.append(" auto-cost reference-bandwidth 100000")
        lines.append("!")
        if block["hostname"] == "HQ-RTR-01":
            lines.append("class-map match-all VOICE")
            lines.append(" match dscp ef")
            lines.append("policy-map WAN-QOS")
            lines.append(" class VOICE")
            lines.append("  priority 1000")
            lines.append("!")
    return ["\n".join(lines)]


def _generate_global_configs(vlsm_allocations: List[Dict[str, Any]], routing_summary: Dict[str, Any]) -> List[str]:
    cities = [
        {"hostname": "SEA-RTR", "subnet": vlsm_allocations[0] if vlsm_allocations else {"network_address": "10.10.0.0", "subnet_mask": "255.255.255.0"}},
        {"hostname": "NYC-RTR", "subnet": vlsm_allocations[1] if len(vlsm_allocations) > 1 else {"network_address": "10.10.1.0", "subnet_mask": "255.255.255.0"}},
        {"hostname": "LON-RTR", "subnet": vlsm_allocations[2] if len(vlsm_allocations) > 2 else {"network_address": "10.10.2.0", "subnet_mask": "255.255.255.0"}},
        {"hostname": "SIN-RTR", "subnet": vlsm_allocations[3] if len(vlsm_allocations) > 3 else {"network_address": "10.10.3.0", "subnet_mask": "255.255.255.0"}},
    ]
    lines: List[str] = []
    for city in cities:
        subnet = city["subnet"]
        lines.append(f"hostname {city['hostname']}")
        lines.append("!")
        lines.append("interface Tunnel0")
        lines.append(f" ip address {subnet['network_address']} {subnet['subnet_mask']}")
        lines.append(" tunnel mode ipsec ipv4")
        lines.append("!")
        lines.append("router ospf 1")
        lines.append(f" network {subnet['network_address']} 0.0.0.255 area 0")
        lines.append(" area 0 range 10.10.0.0 255.255.0.0")
        lines.append("!")
    lines.append("router bgp 65000")
    lines.append(" bgp log-neighbor-changes")
    lines.append(" neighbor 10.10.0.2 remote-as 65001")
    lines.append(" neighbor 10.10.0.2 update-source Loopback0")
    lines.append(" address-family ipv4")
    lines.append("  network 10.10.0.0 mask 255.255.255.0")
    lines.append(" exit-address-family")
    lines.append("!")
    return ["\n".join(lines)]


def _generate_generic_configs(vlsm_allocations: List[Dict[str, Any]], routing_summary: Dict[str, Any]) -> List[str]:
    return ["hostname NET-EDGE\n!\nrouter ospf 1\n network 10.0.0.0 0.0.0.255 area 0\n!"]
