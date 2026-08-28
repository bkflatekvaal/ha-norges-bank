"""Sensor platform for Norges Bank."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_BASE_AMOUNT,
    ATTR_CURRENCY,
    ATTR_CURRENCY_NAME,
    ATTR_OBSERVATION_DATE,
    ATTR_QUOTE_CURRENCY,
    ATTR_SOURCE,
    DOMAIN,
    QUOTE_CURRENCY,
    SOURCE_NAME,
)
from .coordinator import NorgesBankCoordinator
from .models import CurrencyInfo

# Use specific MDI symbols where there is a well-known dedicated icon.
# All others get a generic cash icon, or cash-100 for 100-unit quotations.
CURRENCY_ICONS: dict[str, str] = {
    "EUR": "mdi:currency-eur",
    "USD": "mdi:currency-usd",
    "GBP": "mdi:currency-gbp",
    "JPY": "mdi:currency-jpy",
    "INR": "mdi:currency-inr",
    "RUB": "mdi:currency-rub",
    "CNY": "mdi:currency-cny",
    "KRW": "mdi:currency-krw",
    "TRY": "mdi:currency-try",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[NorgesBankCoordinator],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Norges Bank sensors."""
    coordinator = entry.runtime_data

    async_add_entities(
        NorgesBankExchangeRateSensor(coordinator, coordinator.currencies[code])
        for code in coordinator.selected_currencies
        if code in coordinator.currencies
    )


class NorgesBankExchangeRateSensor(
    CoordinatorEntity[NorgesBankCoordinator],
    SensorEntity,
):
    """Latest Norges Bank exchange rate."""

    _attr_has_entity_name = False
    _attr_native_unit_of_measurement = "NOK"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: NorgesBankCoordinator,
        currency: CurrencyInfo,
    ) -> None:
        super().__init__(coordinator)
        self.currency = currency

        self._attr_unique_id = f"{DOMAIN}_{currency.code.lower()}"
        self._attr_name = f"{currency.name}, {currency.code}"
        self._attr_icon = CURRENCY_ICONS.get(
            currency.code,
            "mdi:cash-100" if currency.base_amount == 100 else "mdi:cash",
        )

    @property
    def native_value(self) -> float | None:
        """Return the latest published rate."""
        rate = self.coordinator.data.get(self.currency.code)
        return rate.value if rate else None

    @property
    def available(self) -> bool:
        """Return whether this currency has a current value."""
        return super().available and self.currency.code in self.coordinator.data

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return useful source metadata."""
        rate = self.coordinator.data.get(self.currency.code)

        return {
            ATTR_CURRENCY: self.currency.code,
            ATTR_CURRENCY_NAME: self.currency.name,
            ATTR_QUOTE_CURRENCY: QUOTE_CURRENCY,
            ATTR_BASE_AMOUNT: self.currency.base_amount,
            ATTR_OBSERVATION_DATE: rate.observation_date if rate else None,
            ATTR_SOURCE: SOURCE_NAME,
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return one logical device for the service."""
        return DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="Norges Bank – Valutakurser",
            manufacturer="Norges Bank",
            model="Exchange Rates (EXR)",
            configuration_url="https://data.norges-bank.no/",
        )
