import pytest

from src.engines.media_engine import PhysicalDistanceViolationError, choose_media


def test_distance_100m_uses_cat6a():
    media = choose_media(100)
    assert media.selected_medium == "Cat6a"
    assert media.transceiver == "10GBASE-T"


def test_distance_101m_uses_om4():
    media = choose_media(101)
    assert media.selected_medium == "OM4 Multimode Fiber"
    assert media.transceiver == "10GBASE-SR, 850nm"


def test_distance_400m_uses_om4():
    media = choose_media(400)
    assert media.selected_medium == "OM4 Multimode Fiber"


def test_distance_401m_uses_os2():
    media = choose_media(401)
    assert media.selected_medium == "OS2 Single-Mode Fiber"
    assert "10GBASE-LR" in media.transceiver


def test_explicit_copper_over_100m_raises():
    with pytest.raises(PhysicalDistanceViolationError):
        choose_media(150, explicit_copper_request=True)
