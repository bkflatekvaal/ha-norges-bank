"""Data update coordinator for Norges Bank."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NorgesBankApi, NorgesBankApiError
from .const import CONF_CURRENCIES, DEFAULT_CURRENCIES, DOMAIN, UPDATE_INTERVAL
from .models import CurrencyInfo, ExchangeRate

_LOGGER = logging.getLogger(__name__)


class NorgesBankCoordinator(DataUpdateCoordinator[dict[str, ExchangeRate]]):
    """Coordinate exchange-rate updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: NorgesBankApi,
        currencies: dict[str, CurrencyInfo],
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.entry = entry
        self.api = api
        self.currencies = currencies

    @property
    def selected_currencies(self) -> list[str]:
        """Return selected currency codes."""
        configured = self.entry.options.get(
            CONF_CURRENCIES,
            self.entry.data.get(CONF_CURRENCIES, DEFAULT_CURRENCIES),
        )
        return [code for code in configured if code in self.currencies]

    async def _async_update_data(self) -> dict[str, ExchangeRate]:
        try:
            data = await self.api.async_get_latest_rates(
                self.selected_currencies,
                self.currencies,
            )
        except NorgesBankApiError as err:
            raise UpdateFailed(f"Error communicating with Norges Bank: {err}") from err

        # Don't fail the whole coordinator if one selected currency has no fresh
        # observation, but expose whatever the API did return.
        return data
