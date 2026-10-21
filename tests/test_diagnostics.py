"""Tests for Norges Bank diagnostics."""

import json
from unittest.mock import MagicMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

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
    coordinator.include_policy_rate = True
    entry = MagicMock()
    entry.data = {"currencies": ["EUR", "SEK"]}
    entry.options = {}
    entry.runtime_data = coordinator

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["coordinator"]["last_update_success"] is True
    assert result["configuration"] == {"include_policy_rate": True}
    json.dumps(result, allow_nan=False)
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


@pytest.mark.parametrize("data", [None, {}])
async def test_diagnostics_excludes_private_configuration_and_errors(
    hass: HomeAssistant, currencies: dict, data: dict | None
) -> None:
    """Neither arbitrary entry fields nor network error details may leak."""
    coordinator = MagicMock()
    coordinator.last_update_success = False
    coordinator.last_exception = UpdateFailed(
        "https://private-user:secret-password@192.168.1.42/?token=secret-token "
        "C:/Users/private-user/config"
    )
    coordinator.selected_currencies = ["EUR"]
    coordinator.include_policy_rate = False
    coordinator.currencies = currencies
    coordinator.data = data
    coordinator.policy_rate = None
    entry = MagicMock()
    entry.data = {
        "currencies": ["EUR"],
        "password": "secret-password",
        "future_field": {"nested": "private-user"},
    }
    entry.options = {"token": "secret-token", "host": "192.168.1.42"}
    entry.title = "private-title"
    entry.unique_id = "private-unique-id"
    entry.runtime_data = coordinator

    result = await async_get_config_entry_diagnostics(hass, entry)
    serialized = json.dumps(result, allow_nan=False)

    assert result["coordinator"]["last_exception"] == "UpdateFailed"
    assert result["rates"] == {}
    assert result["policy_rate"] is None
    for private_value in (
        "private-user",
        "secret-password",
        "secret-token",
        "192.168.1.42",
        "private-title",
        "private-unique-id",
        "future_field",
    ):
        assert private_value not in serialized
    assert entry.data["password"] == "secret-password"
    assert entry.options["token"] == "secret-token"
