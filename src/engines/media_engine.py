from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


class PhysicalDistanceViolationError(ValueError):
    """Raised when a copper path is requested beyond 100 metres."""


@dataclass(frozen=True)
class MediaRecommendation:
    selected_medium: str
    transceiver: str
    transmission_distance_m: int
    attenuation_warning: str
    explanation: str


def choose_media(distance_m: int, medium_hint: Optional[str] = None, explicit_copper_request: bool = False) -> MediaRecommendation:
    if distance_m < 0:
        raise ValueError("Distance must be non-negative")

    if explicit_copper_request and distance_m > 100:
        raise PhysicalDistanceViolationError(
            "Copper link exceeds the 100-metre Ethernet channel limit; Cat6a is not recommended beyond 100 m."
        )

    if distance_m <= 100:
        medium = "Cat6a"
        transceiver = "10GBASE-T"
        attenuation_warning = "Copper attenuation and insertion loss must be validated for long patch runs; keep runs within 100 m."
        explanation = (
            f"Selected Cat6a because the link distance is {distance_m} m, which is within the 100-metre copper channel limit. "
            "This satisfies the IEEE Ethernet reach objective for structured twisted-pair cabling."
        )
    elif distance_m <= 400:
        medium = "OM4 Multimode Fiber"
        transceiver = "10GBASE-SR, 850nm"
        attenuation_warning = "Modal dispersion and connector loss should be reviewed; OM4 is suitable for short-to-medium campus backbones."
        explanation = (
            f"Selected OM4 multimode fiber because the link distance is {distance_m} m, which exceeds the copper limit but remains within the "
            "practical reach of multimode fiber for backbone runs."
        )
    else:
        medium = "OS2 Single-Mode Fiber"
        transceiver = "10GBASE-LR"
        attenuation_warning = "Single-mode fiber is required for long-haul links; optical attenuation and connector loss should be checked per link budget."
        explanation = (
            f"Selected OS2 single-mode fiber because the required transmission distance is {distance_m} m, which exceeds the multimode reach and "
            "requires a long-distance optical medium with lower attenuation."
        )

    if medium_hint and medium_hint.lower() == "copper" and distance_m > 100:
        raise PhysicalDistanceViolationError(
            "A manually requested copper link beyond 100 metres violates the standard physical distance limit."
        )

    return MediaRecommendation(
        selected_medium=medium,
        transceiver=transceiver,
        transmission_distance_m=distance_m,
        attenuation_warning=attenuation_warning,
        explanation=explanation,
    )


def media_summary(profile_name: str, distance_m: int, medium_hint: Optional[str] = None, explicit_copper_request: bool = False) -> Dict[str, object]:
    recommendation = choose_media(distance_m, medium_hint=medium_hint, explicit_copper_request=explicit_copper_request)
    return {
        "profile": profile_name,
        "selected_medium": recommendation.selected_medium,
        "transceiver": recommendation.transceiver,
        "distance_m": distance_m,
        "attenuation_warning": recommendation.attenuation_warning,
        "explanation": recommendation.explanation,
    }
