# NetArchitect

NetArchitect is a command-line recommendation engine for enterprise network planning. It accepts network requirements, recommends physical media, allocates IPv4 subnets using VLSM, selects routing protocols, and produces Cisco IOS configuration templates.

## Overview

The application is designed for academic mini-project use and is optimized for explainability, deterministic design decisions, and clean modular implementation. It supports three predefined scenarios and custom JSON input.

## Features

- Campus LAN media and VLAN planning
- Metro MAN fiber and QoS-aware design recommendations
- Global WAN multi-domain routing design
- VLSM subnet allocation using the Python `ipaddress` standard library
- Explainability engine for media, routing and subnet decisions
- Cisco IOS configuration generation and export to `verification/`
- Automated `pytest` validation suite

## Installation

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the tool

```bash
python -m src.main --profile campus
python -m src.main --profile metro
python -m src.main --profile global
python -m src.main --config custom_network.json
python -m src.main --profile campus --export
```

## Example outputs

The CLI prints:

- Input summary
- Physical media recommendation
- Routing protocol recommendation
- VLSM allocation table
- Technical justifications
- Generated file paths when `--export` is used

## Testing

```bash
python -m pytest -q
```

## Assumptions and limitations

- This project models design recommendations, not live carrier measurements.
- Packet Tracer or GNS3 validation is not claimed here, and the exported Cisco configurations are design templates rather than a full lab simulation.
- Optical reach decisions are based on standard enterprise assumptions and published reach guidance; they do not replace a formal optical link-budget analysis.

## Cisco Packet Tracer / GNS3 import

1. Open Packet Tracer or GNS3.
2. Create a new topology.
3. Import the generated `.cfg` file into the relevant IOS device or copy the configuration into a router or switch CLI session.
4. Validate VLANs and trunking with ping tests and show commands.
5. Test connectivity by confirming end-to-end reachability between subnets and the default gateway.

## Project structure

- `scenarios/` contains predefined JSON profiles.
- `src/` contains the engine and CLI code.
- `tests/` contains pytest coverage.
- `verification/` contains exported device configurations.
- `docs/architecture.md` describes the engineering approach.
