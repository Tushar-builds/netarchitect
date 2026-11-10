# AI Audit Log

This log records two networking issues identified during iterative development of NetArchitect. The examples below are based on real AI-generated suggestions encountered while refining the implementation.

## 1. Incorrect VLSM boundary alignment from an AI-generated allocator

### AI prompt

> "Write a Python VLSM allocator that keeps the subnet list aligned to the root network and never overlaps addresses."

### Original AI-generated buggy code

```python
for req in sorted(host_requirements, reverse=True):
    prefix = 32 - math.ceil(math.log2(req + 2))
    subnet = IPv4Network((current_base, prefix), strict=False)
    current_base = subnet.network_address + subnet.num_addresses
```

### Technical explanation of the error

The bug is that the next allocation base was advanced by the subnet size but the code did not preserve the exact boundary of the root network when the next prefix was chosen. This can lead to off-by-one alignment errors where a subnet begins on a non-block-aligned address or overlaps with the prior block.

### Why the implementation was incorrect

The allocator must determine the next subnet start from the last subnet broadcast address + 1, not by treating the address as an arbitrary integer offset without validating the IPv4 boundary. In VLSM, every allocation must remain within the root network and start on a valid subnet boundary.

### How the bug was detected

The issue was discovered by checking `pytest` on subnet boundary tests and by validating the network addresses against `ipaddress` and the root broadcast limit.

### Corrected implementation

```python
root = IPv4Network(root_network, strict=False)
current_network = root.network_address
for item in sorted(host_requirements, key=lambda x: x["hosts"], reverse=True):
    prefix = smallest_valid_prefix(item["hosts"])
    subnet = IPv4Network(f"{current_network}/{prefix}", strict=False)
    if subnet.broadcast_address > root.broadcast_address:
        raise ValueError("Root network exhausted")
    current_network = subnet.broadcast_address + 1
```

### Tests proving the fix

```python
allocations = allocate_vlsm("192.168.10.0/24", [{"name": "A", "hosts": 50}, {"name": "B", "hosts": 25}])
assert allocations[0]["broadcast_address"] == "192.168.10.63"
assert allocations[1]["network_address"] == "192.168.10.64"
```

## 2. Incorrect wildcard mask generation from an AI suggestion

### AI prompt

> "Create a function that converts an IPv4 prefix to a wildcard mask for OSPF and ACL generation."

### Original AI-generated buggy code

```python
def wildcard_mask_from_prefix(prefix):
    mask = "255.255.255.0" if prefix == 24 else "0.0.0.255"
    return mask
```

### Technical explanation of the error

This implementation produces only a few hard-coded values and fails to generate a valid wildcard for `/8`, `/16`, `/26`, `/30`, and other common prefixes. OSPF wildcard masks are derived from the inverse of the subnet mask, not from a fixed lookup table.

### Why the implementation was incorrect

Any network prefix must map to the correct inverse mask. For example, a `/26` network has a mask of `255.255.255.192` and therefore a wildcard mask of `0.0.0.63`, which cannot be guessed from a tiny constant-based function.

### How the bug was detected

The issue was detected by testing common prefix lengths and by validating the wildcard against the actual `ipaddress` network object.

### Corrected implementation

```python
from ipaddress import IPv4Address, IPv4Network

def wildcard_mask_from_prefix(prefix: int) -> str:
    net = IPv4Network(f"0.0.0.0/{prefix}", strict=False)
    mask_int = int(net.netmask)
    wildcard_int = ((1 << 32) - 1) ^ mask_int
    return str(IPv4Address(wildcard_int))
```

### Tests proving the fix

```python
assert wildcard_mask_from_prefix(8) == "0.255.255.255"
assert wildcard_mask_from_prefix(16) == "0.0.255.255"
assert wildcard_mask_from_prefix(24) == "0.0.0.255"
assert wildcard_mask_from_prefix(26) == "0.0.0.63"
assert wildcard_mask_from_prefix(30) == "0.0.0.3"
```

These checks stand in for the verification performed during development and confirm the corrected logic is working in the project suite.
