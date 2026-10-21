"""Isolated calendar-provider identity guard for research entry points.

This module does NOT modify the Phase4-frozen calendar adapter
(`calendar.py`). It verifies, from installed distribution metadata, that the
actually-installed lunar-python version matches the pinned provider before a
research computation trusts its Jie output.

What this verifies: the installed distribution's reported version equals the
pin. What it does NOT verify: wheel content hashes, package provenance, or
independent astronomical accuracy. Field names below express only the
actually-verified scope.
"""
from importlib.metadata import PackageNotFoundError, version as _installed_version

from .calendar import PROVIDER

PINNED_PROVIDER_NAME = "lunar-python"
PINNED_PROVIDER_VERSION = "1.4.8"


def provider_identity():
    """Verify the actually-installed calendar provider matches the pin.

    Returns the verified identity dict; raises ValueError when the provider
    package is missing or a different version is installed. This reads the
    installed distribution metadata (not a hand-written string), so a
    wrongly installed package cannot masquerade as the pinned provider.
    When the source cannot be reliably confirmed, this raises instead of
    returning an identity claim.
    """
    try:
        installed = _installed_version(PINNED_PROVIDER_NAME)
    except PackageNotFoundError as exc:
        raise ValueError(
            "Calendar provider lunar-python is not installed; source unverifiable") from exc
    if installed != PINNED_PROVIDER_VERSION:
        raise ValueError(
            "Calendar provider version mismatch: installed %s != pinned %s; source unverifiable"
            % (installed, PINNED_PROVIDER_VERSION))
    return {"provider": PINNED_PROVIDER_NAME, "installed_version": installed,
            "pinned": PROVIDER, "installed_version_matches_pin": True}
