"""Tests for Norges Bank diagnostics."""

from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant

from custom_components.norges_bank.diagnostics import (
    async_get_config_entry_diagnostics,
)
from custom_components.norges_bank.models import PolicyRate


async def test_config_entry_diagnostics(
    hass: HomeAssistant, currencies: dict, rates: dict
) -> None:
    """Diagnostics should contain useful serializable runtime information."""
    coordinator = MagicMock()
    coordinator.last_update_success = True
    coordinator.last_exception = None
    coordinator.selected_currencies = ["EUR", "SEK"]
    coordinator.currencies = currencies
    coordinator.data = rates
    coordinator.policy_rate = PolicyRate(4.25, "2026-08-26", decimal_places=2)
    entry = MagicMock()
    entry.data = {"currencies": ["EUR", "SEK"]}
    entry.options = {}
    entry.runtime_data = coordinator

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["coordinator"]["last_update_success"] is True
    assert result["currencies"]["SEK"] == {
        "name": "Svenske kroner",
        "base_amount": 100,
        "decimal_places": 2,
    }
    assert result["rates"]["EUR"] == {
        "value": 11.75,
        "observation_date": "2026-08-27",
    }
    assert result["policy_rate"] == {
        "value": 4.25,
        "observation_date": "2026-08-26",
        "decimal_places": 2,
    }
