"""Diagnostics support for Norges Bank."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import NorgesBankConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: NorgesBankConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    return {
        "entry": {
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_exception": (
                str(coordinator.last_exception)
                if coordinator.last_exception is not None
                else None
            ),
            "selected_currencies": coordinator.selected_currencies,
        },
        "currencies": {
            code: {
                "name": currency.name,
                "base_amount": currency.base_amount,
                "decimal_places": currency.decimal_places,
            }
            for code, currency in coordinator.currencies.items()
        },
        "rates": {
            code: {
                "value": rate.value,
                "observation_date": rate.observation_date,
            }
            for code, rate in coordinator.data.items()
        },
    }
