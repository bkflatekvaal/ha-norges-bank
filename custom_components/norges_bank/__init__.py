"""Norges Bank integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry, ConfigEntryNotReady
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NorgesBankApi, NorgesBankApiError
from .const import CONF_CURRENCIES, DEFAULT_CURRENCIES, DOMAIN
from .coordinator import NorgesBankCoordinator

PLATFORMS = [Platform.SENSOR]

type NorgesBankConfigEntry = ConfigEntry[NorgesBankCoordinator]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NorgesBankConfigEntry,
) -> bool:
    """Set up Norges Bank from a config entry."""
    api = NorgesBankApi(async_get_clientsession(hass))
    try:
        currencies = await api.async_get_currencies()
    except NorgesBankApiError as err:
        raise ConfigEntryNotReady(
            f"Error communicating with Norges Bank: {err}"
        ) from err

    configured = entry.options.get(
        CONF_CURRENCIES,
        entry.data.get(CONF_CURRENCIES, DEFAULT_CURRENCIES),
    )
    missing = sorted(set(configured) - currencies.keys())
    if missing:
        ir.async_create_issue(
            hass,
            DOMAIN,
            "removed_currencies",
            is_fixable=False,
            is_persistent=False,
            severity=ir.IssueSeverity.ERROR,
            translation_key="removed_currencies",
            translation_placeholders={"currencies": ", ".join(missing)},
        )
    else:
        ir.async_delete_issue(hass, DOMAIN, "removed_currencies")

    coordinator = NorgesBankCoordinator(hass, entry, api, currencies)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: NorgesBankConfigEntry,
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
