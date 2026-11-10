from __future__ import annotations

from typing import Any, Dict, List


def create_explanations(profile_name: str, media_summary: Dict[str, Any], routing_summary: Dict[str, Any], vlsm_allocations: List[Dict[str, Any]]) -> List[str]:
    explanations: List[str] = []
    explanations.append(
        f"Media explanation: {media_summary['explanation']} The selected transceiver is {media_summary['transceiver']} and the attenuation warning is: {media_summary['attenuation_warning']}"
    )
    explanations.append(f"Routing explanation: {routing_summary['explanation']}")
    explanations.append(
        "VLSM explanation: Each subnet was sorted by descending host count and allocated on valid network boundaries to avoid overlap. "
        "This preserves address availability while keeping every allocation within the root network."
    )
    for subnet in vlsm_allocations:
        explanations.append(
            f"Allocated subnet {subnet['name']} as {subnet['network_address']}/{subnet['prefix']} with a default gateway of {subnet['default_gateway']} because {subnet['host_requirement']} hosts require a subnet sized for {subnet['total_usable_addresses']} usable addresses."
        )
    return explanations
