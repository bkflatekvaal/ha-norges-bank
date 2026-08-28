"""Shared fixtures for Norges Bank tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest

from custom_components.norges_bank.models import CurrencyInfo, ExchangeRate, PolicyRate


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable loading custom integrations in Home Assistant tests."""


@pytest.fixture
def currencies() -> dict[str, CurrencyInfo]:
    """Return representative currency metadata."""
    return {
        "EUR": CurrencyInfo("EUR", "Euro", decimal_places=4),
        "SEK": CurrencyInfo(
            "SEK", "Svenske kroner", unit_multiplier=2, decimal_places=2
        ),
    }


@pytest.fixture
def rates(currencies: dict[str, CurrencyInfo]) -> dict[str, ExchangeRate]:
    """Return representative exchange rates."""
    return {
        "EUR": ExchangeRate(currencies["EUR"], 11.75, "2026-08-27"),
        "SEK": ExchangeRate(currencies["SEK"], 105.2, "2026-08-27"),
    }


@pytest.fixture
def mock_api(
    currencies: dict[str, CurrencyInfo], rates: dict[str, ExchangeRate]
) -> Generator[AsyncMock]:
    """Mock the Norges Bank API client."""
    with patch("custom_components.norges_bank.NorgesBankApi", autospec=True) as api:
        api.return_value.async_get_currencies.return_value = currencies
        api.return_value.async_get_latest_rates.return_value = rates
        api.return_value.async_get_policy_rate.return_value = PolicyRate(
            4.25, "2026-08-26", decimal_places=2
        )
        yield api.return_value
