import pytest

from src.engines.vlsm_engine import allocate_vlsm, smallest_valid_prefix, wildcard_mask_from_prefix


def test_smallest_valid_prefix_for_50_hosts():
    assert smallest_valid_prefix(50) == 26


def test_allocation_sizes_are_correct():
    subnets = allocate_vlsm("192.168.0.0/16", [{"name": "A", "hosts": 50}, {"name": "B", "hosts": 20}, {"name": "C", "hosts": 10}])
    assert len(subnets) == 3
    assert subnets[0]["network_address"] == "192.168.0.0"
    assert subnets[0]["prefix"] == 26
    assert subnets[0]["total_usable_addresses"] == 62


def test_no_overlapping_subnets():
    allocations = allocate_vlsm("10.0.0.0/24", [{"name": "A", "hosts": 10}, {"name": "B", "hosts": 8}, {"name": "C", "hosts": 4}])
    networks = [item["network_address"] for item in allocations]
    assert len(networks) == len(set(networks))


def test_subnet_exhaustion_raises():
    with pytest.raises(ValueError):
        allocate_vlsm("10.0.0.0/30", [{"name": "A", "hosts": 10}, {"name": "B", "hosts": 5}])


def test_invalid_root_prefix_raises():
    with pytest.raises(ValueError):
        allocate_vlsm("invalid", [{"name": "A", "hosts": 10}])


def test_boundary_alignment_is_valid():
    allocations = allocate_vlsm("192.168.10.0/24", [{"name": "A", "hosts": 50}, {"name": "B", "hosts": 25}])
    assert allocations[0]["broadcast_address"] == "192.168.10.63"
    assert allocations[1]["network_address"] == "192.168.10.64"


def test_wildcard_mask_for_common_prefixes():
    assert wildcard_mask_from_prefix(8) == "0.255.255.255"
    assert wildcard_mask_from_prefix(16) == "0.0.255.255"
    assert wildcard_mask_from_prefix(24) == "0.0.0.255"
    assert wildcard_mask_from_prefix(26) == "0.0.0.63"
    assert wildcard_mask_from_prefix(30) == "0.0.0.3"
