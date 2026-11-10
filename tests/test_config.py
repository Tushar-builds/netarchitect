from src.generators.cisco_config import generate_cisco_configs


def test_campus_config_contains_vlan_and_ospf():
    config = generate_cisco_configs("campus", {}, [{"network_address": "192.168.10.0", "subnet_mask": "255.255.255.0"}], {"protocol": "OSPF"})[0]
    assert "hostname CORE-01" in config
    assert "vlan 10" in config
    assert "switchport trunk allowed vlan 10,20" in config
    assert "router ospf 1" in config
    assert "area 0" in config


def test_global_config_contains_bgp_and_ipsec():
    config = generate_cisco_configs("global", {}, [{"network_address": "10.10.0.0", "subnet_mask": "255.255.255.0"}], {"protocol": "eBGP"})[0]
    assert "router bgp 65000" in config
    assert "tunnel mode ipsec ipv4" in config
    assert "neighbor 10.10.0.2 remote-as 65001" in config


def test_config_uses_valid_vlan_references():
    config = generate_cisco_configs("campus", {}, [{"network_address": "192.168.10.0", "subnet_mask": "255.255.255.0"}], {"protocol": "OSPF"})[0]
    assert "switchport access vlan 10" in config
    assert "switchport trunk allowed vlan 10,20" in config
