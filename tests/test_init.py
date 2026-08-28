"""Tests for Norges Bank config-entry setup."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryNotReady
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.norges_bank import async_setup_entry
from custom_components.norges_bank.api import NorgesBankConnectionError
from custom_components.norges_bank.const import CONF_CURRENCIES, DOMAIN


async def test_setup_entry(
    hass: HomeAssistant, mock_api: AsyncMock, rates: dict
) -> None:
    """Setup fetches metadata and performs the first coordinated refresh."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_CURRENCIES: ["EUR"]})
    entry.add_to_hass(hass)

    with patch.object(hass.config_entries, "async_forward_entry_setups") as forward:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.runtime_data.data == rates
    forward.assert_awaited_once()


async def test_setup_entry_retries_metadata_failure(hass: HomeAssistant) -> None:
    """Temporary metadata failures should enter Home Assistant's retry flow."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_CURRENCIES: ["EUR"]})

    with (
        patch(
            "custom_components.norges_bank.NorgesBankApi.async_get_currencies",
            side_effect=NorgesBankConnectionError("offline"),
        ),
        pytest.raises(ConfigEntryNotReady),
    ):
        await async_setup_entry(hass, entry)


async def test_setup_entry_creates_issue_for_removed_currency(
    hass: HomeAssistant, mock_api: AsyncMock
) -> None:
    """A selected currency missing from metadata should create a repair issue."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_CURRENCIES: ["EUR", "JPY"]})
    entry.add_to_hass(hass)

    with (
        patch("custom_components.norges_bank.ir.async_create_issue") as create_issue,
        patch.object(hass.config_entries, "async_forward_entry_setups"),
    ):
        await async_setup_entry(hass, entry)

    assert entry.runtime_data.selected_currencies == ["EUR"]
    create_issue.assert_called_once()
    assert create_issue.call_args.kwargs["translation_placeholders"] == {
        "currencies": "JPY"
    }


async def test_setup_entry_clears_removed_currency_issue(
    hass: HomeAssistant, mock_api: AsyncMock
) -> None:
    """Setup should clear an obsolete removed-currency issue."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_CURRENCIES: ["EUR"]})
    entry.add_to_hass(hass)

    with (
        patch("custom_components.norges_bank.ir.async_delete_issue") as delete_issue,
        patch.object(hass.config_entries, "async_forward_entry_setups"),
    ):
        await async_setup_entry(hass, entry)

    delete_issue.assert_called_once_with(hass, DOMAIN, "removed_currencies")
