"""Tests for the Norges Bank data coordinator."""

from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.norges_bank.api import NorgesBankConnectionError
from custom_components.norges_bank.const import CONF_CURRENCIES, DOMAIN
from custom_components.norges_bank.coordinator import NorgesBankCoordinator


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
