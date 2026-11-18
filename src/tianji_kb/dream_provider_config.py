"""Dream adapter provider settings (Line C preparation, TJ-028.1).

Reads ONLY from the trusted process environment (``TIANJI_AI_*``). No
credential is stored, logged, or returned by this module: the API key
never leaves the settings dict handed to the transport, and
:meth:`describe` exposes only the driver, the endpoint host, the model
name, and whether credentials are present -- never the key itself and
never the full endpoint URL.

When no provider is configured (or the configuration is invalid) the
module reports ``configured=False`` instead of raising: the dream
adapter then fails closed (``explain=false``, ``ai_enabled`` stays
``False``, the lookup layer is unchanged). This module does NOT enable
user-facing AI and does NOT perform any model call.
"""
from .ai_providers import settings_from_environment
from .explanation import ExplanationFailure
from .model_client import _safe_url

# Environment names the dream adapter honours. Anything else in the
# environment is ignored; credentials are never read from files, URLs,
# or request payloads.
ENV_PROVIDER = "TIANJI_AI_PROVIDER"
ENV_BASE_URL = "TIANJI_AI_BASE_URL"
ENV_API_KEY = "TIANJI_AI_API_KEY"
ENV_MODEL = "TIANJI_AI_MODEL"

_NOT_CONFIGURED = {
    "configured": False,
    "driver": None,
    "endpoint": None,
    "model": None,
    "timeout": None,
    "max_tokens": None,
    "reason": "not_configured",
    "settings": None,
}


def load_dream_provider_config():
    """Return the dream provider configuration from the trusted environment.

    The returned dict always has the keys ``configured``, ``driver``,
    ``endpoint``, ``model``, ``timeout``, ``max_tokens``, ``reason`` and
    ``settings``. ``settings`` is the ``ai_providers`` settings dict
    (which carries the API key) and is present ONLY when
    ``configured`` is True; callers must pass it straight to the
    transport and never log, serialise, or embed it elsewhere.

    ``reason`` is ``'not_configured'`` when the provider is disabled or
    absent, and ``'invalid_configuration'`` when the environment values
    fail validation. Neither case raises.
    """
    try:
        settings = settings_from_environment()
    except (ExplanationFailure, ValueError):
        return {**_NOT_CONFIGURED, "reason": "invalid_configuration"}
    if settings is None:
        return dict(_NOT_CONFIGURED)
    return {
        "configured": True,
        "driver": settings["driver"],
        "endpoint": settings["endpoint"],
        "model": settings["model"],
        "timeout": settings["timeout"],
        "max_tokens": settings["max_tokens"],
        "reason": None,
        "settings": settings,
    }


def describe(config):
    """Return a log-safe description of a provider configuration.

    Never includes the API key or the full endpoint URL (a credential
    could be smuggled into the path, query, or fragment). The endpoint
    is reduced to scheme + host via the same safe-URL helper the model
    client uses for its logs.
    """
    if not isinstance(config, dict):
        return {"configured": False, "reason": "invalid_configuration"}
    endpoint = config.get("endpoint")
    return {
        "configured": bool(config.get("configured")),
        "driver": config.get("driver"),
        "endpoint_host": _safe_url(endpoint) if endpoint else None,
        "model": config.get("model"),
        "reason": config.get("reason"),
    }


def provider_configured():
    """True only when a usable provider (driver + endpoint + key) is set.

    Reads the real process environment. Tests should patch
    ``os.environ`` (``unittest.mock.patch.dict``) the way the existing
    model-client tests do; this function never writes the environment.
    """
    return bool(load_dream_provider_config().get("configured"))
