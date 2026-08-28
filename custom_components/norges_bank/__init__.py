"""Norges Bank integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NorgesBankApi
from .const import DOMAIN
from .coordinator import NorgesBankCoordinator

PLATFORMS = [Platform.SENSOR]

type NorgesBankConfigEntry = ConfigEntry[NorgesBankCoordinator]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NorgesBankConfigEntry,
) -> bool:
    """Set up Norges Bank from a config entry."""
    api = NorgesBankApi(async_get_clientsession(hass))
    currencies = await api.async_get_currencies()

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
