from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from src.generators.cisco_config import generate_cisco_configs


def export_scenario(profile_name: str, profile: Dict[str, Any], routing_summary: Dict[str, Any], media_summary: Dict[str, Any], vlsm_allocations: List[Dict[str, Any]]) -> Path:
    output_dir = Path(__file__).resolve().parent.parent.parent / "verification"
    output_dir.mkdir(exist_ok=True)
    cfg_path = output_dir / f"{profile_name}.cfg"

    config_text = "\n\n".join(generate_cisco_configs(profile_name, profile, vlsm_allocations, routing_summary))
    cfg_path.write_text(config_text, encoding="utf-8")

    report = {
        "profile": profile_name,
        "media": media_summary,
        "routing": routing_summary,
        "vlsm_allocations": vlsm_allocations,
    }
    summary_path = output_dir / f"{profile_name}_summary.json"
    summary_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return cfg_path
