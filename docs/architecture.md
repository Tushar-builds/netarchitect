# NetArchitect architecture

NetArchitect follows a modular design to keep the network engineering logic transparent and verifiable.

## Modules

- `input_handler.py`: validates scenario and custom JSON input.
- `media_engine.py`: applies physical media rules and transceiver selection.
- `routing_engine.py`: selects the routing domain and explains protocol choice.
- `vlsm_engine.py`: allocates IPv4 subnets and checks for overlaps and exhaustion.
- `explainability_engine.py`: converts design decisions into human-readable engineering explanations.
- `cisco_config.py`: generates Cisco IOS templates.
- `export_engine.py`: writes configuration outputs to `verification/`.

## Design approach

The engine uses deterministic rules, documented engineering assumptions, and Python `ipaddress` calculations to ensure valid IPv4 addressing. Each module is independent so unit tests can validate behavior without needing a full network lab.
