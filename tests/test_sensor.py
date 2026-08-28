"""Tests for Norges Bank exchange-rate sensors."""

from unittest.mock import MagicMock

from custom_components.norges_bank.models import PolicyRate
from custom_components.norges_bank.sensor import (
    NorgesBankExchangeRateSensor,
    NorgesBankPolicyRateSensor,
)


def test_sensor_preserves_published_quotation(currencies: dict, rates: dict) -> None:
    """The state and attributes expose the API quotation unchanged."""
    coordinator = MagicMock()
    coordinator.data = rates
    coordinator.last_update_success = True
    sensor = NorgesBankExchangeRateSensor(coordinator, currencies["SEK"])

    assert sensor.has_entity_name
    assert sensor.entity_id == "sensor.exchange_rate_nok_sek"
    assert sensor.translation_key == "exchange_rate"
    assert sensor.translation_placeholders == {
        "base_currency": "SEK",
        "quote_currency": "NOK",
    }
    assert sensor.native_value == 105.2
    assert sensor.native_unit_of_measurement == "NOK"
    assert sensor.suggested_display_precision == 2
    assert sensor.extra_state_attributes == {
        "currency": "SEK",
        "currency_name": "Svenske kroner",
        "quote_currency": "NOK",
        "base_amount": 100,
        "observation_date": "2026-08-27",
        "source": "Norges Bank",
    }


def test_policy_rate_sensor() -> None:
    """The optional policy-rate sensor should expose the published observation."""
    coordinator = MagicMock()
    coordinator.last_update_success = True
    coordinator.policy_rate = PolicyRate(4.25, "2026-08-26", decimal_places=2)
    sensor = NorgesBankPolicyRateSensor(coordinator)

    assert sensor.entity_id == "sensor.norges_bank_policy_rate"
    assert sensor.unique_id == "norges_bank_policy_rate"
    assert sensor.native_value == 4.25
    assert sensor.native_unit_of_measurement == "%"
    assert sensor.suggested_display_precision == 2
    assert sensor.extra_state_attributes == {
        "instrument_type": "KPRA",
        "tenor": "SD",
        "unit_measure": "R",
        "collection": "E",
        "observation_date": "2026-08-26",
        "source": "Norges Bank",
    }
