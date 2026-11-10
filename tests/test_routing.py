from src.engines.routing_engine import determine_routing


def test_single_as_under_50_subnets_uses_ospf_area_0():
    profile = {"profile": "campus_lan", "sites": 3, "host_requirements": [{"name": "A", "hosts": 20}, {"name": "B", "hosts": 30}], "routing_domain": {"as_count": 1, "external_cloud": False}}
    summary = determine_routing(profile)
    assert "OSPF" in summary["protocol"]
    assert summary["areas"] == [0]


def test_multiple_sites_with_many_subnets_uses_multi_area_ospf():
    profile = {"profile": "campus_lan", "sites": 5, "host_requirements": [{"name": f"S{i}", "hosts": 10} for i in range(60)], "routing_domain": {"as_count": 1, "external_cloud": False}}
    summary = determine_routing(profile)
    assert "Multi-Area OSPF" in summary["protocol"]


def test_multiple_as_or_cloud_uses_bgp():
    profile = {"profile": "global_wan", "sites": 4, "host_requirements": [{"name": "A", "hosts": 10}], "routing_domain": {"as_count": 2, "external_cloud": True}}
    summary = determine_routing(profile)
    assert "eBGP" in summary["protocol"]


def test_external_cloud_boundary_is_detected():
    profile = {"profile": "global_wan", "sites": 2, "host_requirements": [{"name": "A", "hosts": 12}], "routing_domain": {"as_count": 1, "external_cloud": True}}
    summary = determine_routing(profile)
    assert "eBGP" in summary["protocol"]
