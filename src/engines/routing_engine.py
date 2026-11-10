from __future__ import annotations

from typing import Any, Dict


def determine_routing(profile: Dict[str, Any]) -> Dict[str, Any]:
    profile_name = str(profile.get("profile", "custom")).lower()
    sites = int(profile.get("sites", profile.get("buildings", 1)))
    host_requirements = profile.get("host_requirements", [])
    subnets = len(host_requirements)
    routing_domain = profile.get("routing_domain", {})
    as_count = int(routing_domain.get("as_count", 1))
    external_boundary = bool(routing_domain.get("external_cloud", False))

    if as_count > 1 or external_boundary:
        protocol = "eBGP"
        topology = "Dual-homed or multi-AS topology with cloud/provider boundaries"
        details = "External cloud provider routes should be exchanged via eBGP; internal domains retain summarization."
        explanation = (
            "Selected eBGP because the design includes multiple autonomous systems or external cloud/provider routing boundaries. "
            "This preserves routing-domain separation while allowing controlled advertisement of summarized prefixes."
        )
    elif sites > 1 and subnets >= 50:
        protocol = "Multi-Area OSPF"
        topology = "Core-area plus area border summarization and remote-site reachability"
        details = "Use Area 0 for the backbone and additional non-zero areas for site-specific routing domains."
        explanation = (
            "Selected Multi-Area OSPF because the topology has multiple sites and more than 50 subnets. "
            "The design separates the backbone from local site routing while maintaining deterministic SPF computation."
        )
    else:
        protocol = "OSPF"
        topology = "Single-area backbone with end-site reachability"
        details = "Use OSPF Area 0 as the single-area backbone for a single AS with fewer than 50 subnets."
        explanation = (
            "Selected OSPF Area 0 because the network operates within a single autonomous system and contains fewer than 50 subnets. "
            "This keeps the routing domain simple, loop-free, and consistent with documented enterprise design guidance."
        )

    if profile_name == "global_wan":
        protocol = "Multi-Area OSPF + eBGP"
        topology = "Regional OSPF domains connected through BGP for cloud and internet edge reachability"
        details = "Summarize route advertisements between regional OSPF areas and the cloud edge with BGP route filtering."
        explanation = (
            "Selected Multi-Area OSPF with eBGP because the global WAN includes multiple cities and cloud connectivity. "
            "The OSPF domains handle internal route propagation while eBGP preserves provider and VPC routing boundaries."
        )

    return {
        "protocol": protocol,
        "topology": topology,
        "areas": [0] if protocol.lower() == "ospf" or "ospf" in protocol.lower() else [0, 10],
        "as_number": routing_domain.get("as_number", 65000),
        "details": details,
        "explanation": explanation,
    }
