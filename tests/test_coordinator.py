"""Tests for the Norges Bank data coordinator."""

from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.norges_bank.api import NorgesBankConnectionError
from custom_components.norges_bank.const import (
    CONF_CURRENCIES,
    CONF_INCLUDE_POLICY_RATE,
    DOMAIN,
)
from custom_components.norges_bank.coordinator import NorgesBankCoordinator
from custom_components.norges_bank.models import PolicyRate


async def test_update_failure_is_reported(
    hass: HomeAssistant, currencies: dict
) -> None:
    """API failures should become coordinator update failures."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_CURRENCIES: ["EUR"]})
    api = AsyncMock()
    api.async_get_latest_rates.side_effect = NorgesBankConnectionError("offline")
    coordinator = NorgesBankCoordinator(hass, entry, api, currencies)

    with pytest.raises(UpdateFailed, match="Norges Bank"):
        await coordinator._async_update_data()


async def test_policy_rate_is_fetched_when_enabled(
    hass: HomeAssistant, currencies: dict, rates: dict
) -> None:
    """The coordinator should fetch the policy rate only when selected."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_CURRENCIES: ["EUR"],
            CONF_INCLUDE_POLICY_RATE: True,
        },
    )
    api = AsyncMock()
    api.async_get_latest_rates.return_value = rates
    api.async_get_policy_rate.return_value = PolicyRate(4.25, "2026-08-26", 2)
    coordinator = NorgesBankCoordinator(hass, entry, api, currencies)

    result = await coordinator._async_update_data()

    assert result == rates
    assert coordinator.policy_rate == PolicyRate(4.25, "2026-08-26", 2)
    api.async_get_policy_rate.assert_awaited_once_with()
