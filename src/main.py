from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from src.engines.explainability_engine import create_explanations
from src.engines.media_engine import media_summary
from src.engines.routing_engine import determine_routing
from src.engines.vlsm_engine import allocate_vlsm
from src.generators.export_engine import export_scenario
from src.input_handler import load_any_profile


def _run_profile(profile_name: str, custom_path: str | None = None, export: bool = False) -> Dict[str, object]:
    profile = load_any_profile(profile_name, custom_path)
    host_requirements = profile["host_requirements"]
    vlsm_allocations = allocate_vlsm(profile["root_network"], host_requirements)
    routing_summary = determine_routing(profile)

    first_distance = int(profile.get("link_distances", {}).get("backbone", profile.get("distance_m", 100)))
    media = media_summary(
        profile_name=profile["profile"],
        distance_m=first_distance,
        medium_hint=profile.get("media_hint"),
        explicit_copper_request=bool(profile.get("explicit_copper_request", False)),
    )

    explanations = create_explanations(profile["profile"], media, routing_summary, vlsm_allocations)

    if export:
        export_scenario(profile["profile"], profile, routing_summary, media, vlsm_allocations)

    result = {
        "input_summary": {
            "profile": profile["profile"],
            "root_network": profile["root_network"],
            "sites": profile.get("sites", profile.get("buildings", 1)),
            "endpoints": profile.get("endpoints", 0),
            "host_requirements": host_requirements,
        },
        "media": media,
        "routing": routing_summary,
        "vlsm_allocations": vlsm_allocations,
        "explanations": explanations,
    }
    return result


def _print_result(result: Dict[str, object]) -> None:
    summary = result["input_summary"]
    print("Input summary:")
    print(json.dumps(summary, indent=2))
    print("\nPhysical media recommendations:")
    print(json.dumps(result["media"], indent=2))
    print("\nRouting recommendations:")
    print(json.dumps(result["routing"], indent=2))
    print("\nVLSM allocation table:")
    for item in result["vlsm_allocations"]:
        print(json.dumps(item, indent=2))
    print("\nTechnical justifications:")
    for explanation in result["explanations"]:
        print(f"- {explanation}")


def main() -> int:
    parser = argparse.ArgumentParser(description="NetArchitect recommendation engine")
    parser.add_argument("--profile", choices=["campus", "metro", "global"], help="Use one of the predefined network profiles")
    parser.add_argument("--config", help="Path to a custom JSON network specification")
    parser.add_argument("--export", action="store_true", help="Write generated configuration files under verification/")
    args = parser.parse_args()

    try:
        profile_name = args.profile if args.profile else ""
        result = _run_profile(profile_name, args.config, args.export)
        _print_result(result)
        if args.export:
            print("\nGenerated configuration file locations:")
            for exported_name in ["campus_lan", "metro_man", "global_wan"]:
                path = Path(__file__).resolve().parent.parent / "verification" / f"{exported_name}.cfg"
                if path.exists():
                    print(f"- {path}")
        return 0
    except Exception as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
