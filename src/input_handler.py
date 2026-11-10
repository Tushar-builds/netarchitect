from __future__ import annotations

import json
from ipaddress import IPv4Network
from pathlib import Path
from typing import Any, Dict, List

SCENARIO_DIR = Path(__file__).resolve().parent.parent / "scenarios"


def _coerce_host_requirements(raw_requirements: Any) -> List[Dict[str, Any]]:
    if raw_requirements is None:
        return []
    if not isinstance(raw_requirements, list):
        raise ValueError("host_requirements must be a list of subnet requirements")

    normalized: List[Dict[str, Any]] = []
    for item in raw_requirements:
        if isinstance(item, dict):
            name = str(item.get("name") or item.get("label") or f"subnet_{len(normalized) + 1}")
            hosts = item.get("hosts")
            if hosts is None:
                raise ValueError(f"Subnet '{name}' is missing a hosts value")
            hosts = int(hosts)
            if hosts <= 0:
                raise ValueError(f"Subnet '{name}' must require at least one host")
            normalized.append({"name": name, "hosts": hosts})
        else:
            hosts = int(item)
            if hosts <= 0:
                raise ValueError(f"Subnet host requirement '{hosts}' must be positive")
            normalized.append({"name": f"subnet_{len(normalized) + 1}", "hosts": hosts})
    return normalized


def _validate_topology(profile: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(profile, dict):
        raise ValueError("Profile must be a JSON object")

    required = ["profile", "root_network", "host_requirements"]
    for key in required:
        if key not in profile:
            raise ValueError(f"Profile is missing required key: {key}")

    try:
        IPv4Network(profile["root_network"], strict=False)
    except ValueError as exc:
        raise ValueError(f"Invalid root network '{profile['root_network']}'") from exc

    profile["host_requirements"] = _coerce_host_requirements(profile.get("host_requirements"))
    int(profile.get("sites", profile.get("buildings", 1)))
    return profile


def load_profile(profile_name: str) -> Dict[str, Any]:
    name = str(profile_name).strip().lower()
    mapping = {
        "campus": "campus_lan.json",
        "metro": "metro_man.json",
        "global": "global_wan.json",
    }
    if name not in mapping:
        raise ValueError(f"Unsupported predefined profile: {profile_name}")

    path = SCENARIO_DIR / mapping[name]
    if not path.exists():
        raise FileNotFoundError(f"Scenario file '{path}' does not exist")

    with path.open("r", encoding="utf-8") as handle:
        profile = json.load(handle)
    return _validate_topology(profile)


def load_custom_profile(custom_path: str) -> Dict[str, Any]:
    file_path = Path(custom_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Custom profile file '{custom_path}' was not found")

    with file_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    return _validate_topology(config)


def load_any_profile(profile_name: str | None = None, custom_path: str | None = None) -> Dict[str, Any]:
    if custom_path:
        return load_custom_profile(custom_path)
    if profile_name is not None:
        return load_profile(profile_name)
    raise ValueError("Provide either --profile or --config")
