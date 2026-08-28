"""Sensor platform for Norges Bank."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_BASE_AMOUNT,
    ATTR_COLLECTION,
    ATTR_CURRENCY,
    ATTR_CURRENCY_NAME,
    ATTR_INSTRUMENT_TYPE,
    ATTR_OBSERVATION_DATE,
    ATTR_QUOTE_CURRENCY,
    ATTR_SOURCE,
    ATTR_TENOR,
    ATTR_UNIT_MEASURE,
    DOMAIN,
    QUOTE_CURRENCY,
    SOURCE_NAME,
)
from .coordinator import NorgesBankCoordinator
from .models import CurrencyInfo

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
    if coordinator.include_policy_rate:
        async_add_entities([NorgesBankPolicyRateSensor(coordinator)])


class NorgesBankExchangeRateSensor(
    CoordinatorEntity[NorgesBankCoordinator], SensorEntity
):
    """Latest Norges Bank exchange rate."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "NOK"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, coordinator: NorgesBankCoordinator, currency: CurrencyInfo
    ) -> None:
        """Initialize an exchange-rate sensor."""
        super().__init__(coordinator)
        self.currency = currency
        self.entity_id = f"sensor.exchange_rate_nok_{currency.code.lower()}"
        self._attr_unique_id = f"{DOMAIN}_{currency.code.lower()}"
        self._attr_translation_key = "exchange_rate"
        self._attr_translation_placeholders = {
            "base_currency": currency.code,
            "quote_currency": QUOTE_CURRENCY,
        }
        self._attr_suggested_display_precision = currency.decimal_places
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


class NorgesBankPolicyRateSensor(
    CoordinatorEntity[NorgesBankCoordinator], SensorEntity
):
    """Latest Norges Bank policy rate."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:sack-percent"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_translation_key = "policy_rate"
    _attr_unique_id = f"{DOMAIN}_policy_rate"

    def __init__(self, coordinator: NorgesBankCoordinator) -> None:
        """Initialize the policy-rate sensor."""
        super().__init__(coordinator)
        self.entity_id = "sensor.norges_bank_policy_rate"

    @property
    def native_value(self) -> float | None:
        """Return the latest published policy rate."""
        rate = self.coordinator.policy_rate
        return rate.value if rate else None

    @property
    def suggested_display_precision(self) -> int | None:
        """Return the precision published by Norges Bank."""
        rate = self.coordinator.policy_rate
        return rate.decimal_places if rate else None

    @property
    def available(self) -> bool:
        """Return whether the policy rate has a current value."""
        return super().available and self.coordinator.policy_rate is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return useful source metadata."""
        rate = self.coordinator.policy_rate
        return {
            ATTR_INSTRUMENT_TYPE: "KPRA",
            ATTR_TENOR: "SD",
            ATTR_UNIT_MEASURE: "R",
            ATTR_COLLECTION: "E",
            ATTR_OBSERVATION_DATE: rate.observation_date if rate else None,
            ATTR_SOURCE: SOURCE_NAME,
        }
