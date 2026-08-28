"""Tests for the Norges Bank SDMX parser."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.norges_bank.api import (
    NorgesBankApi,
    NorgesBankResponseError,
    _resolve_attributes,
)


def _series_dimensions() -> list[dict]:
    return [
        {"id": "FREQ", "values": [{"id": "B"}]},
        {
            "id": "BASE_CUR",
            "values": [
                {"id": "EUR", "name": "Euro"},
                {"id": "SEK", "name": "Svenske kroner"},
            ],
        },
        {"id": "QUOTE_CUR", "values": [{"id": "NOK"}]},
        {"id": "TENOR", "values": [{"id": "SP"}]},
    ]


async def test_get_latest_rates_parses_captured_response() -> None:
    """Parse the structure returned by the live Norges Bank endpoint."""
    fixture = Path(__file__).parent / "fixtures" / "latest_rates.json"
    api = NorgesBankApi(MagicMock())
    api._get_json = AsyncMock(return_value=json.loads(fixture.read_text("utf-8")))

    result = await api.async_get_latest_rates(["USD", "DKK", "SEK", "GBP", "EUR"])

    assert {code: rate.value for code, rate in result.items()} == {
        "DKK": 145.52,
        "USD": 9.3405,
        "GBP": 12.686,
        "EUR": 10.877,
        "SEK": 98.14,
    }
    assert result["DKK"].currency.base_amount == 100
    assert result["SEK"].currency.base_amount == 100
    assert result["USD"].currency.base_amount == 1
    assert result["DKK"].currency.decimal_places == 2
    assert result["USD"].currency.decimal_places == 4
    assert {rate.observation_date for rate in result.values()} == {"2026-08-27"}


async def test_get_policy_rate_selects_sd_series() -> None:
    """The policy-rate parser should select SD, not the related OL or RR rates."""
    fixture = Path(__file__).parent / "fixtures" / "policy_rate.json"
    api = NorgesBankApi(MagicMock())
    api._get_json = AsyncMock(return_value=json.loads(fixture.read_text("utf-8")))

    result = await api.async_get_policy_rate()

    assert result.value == 4.25
    assert result.observation_date == "2026-08-26"
    assert result.decimal_places == 2


async def test_get_latest_rates_uses_combined_request_and_latest_valid_value(
    currencies: dict,
) -> None:
    """The parser should keep quotations and skip a null newest observation."""
    api = NorgesBankApi(MagicMock())
    api._get_json = AsyncMock(
        return_value={
            "data": {
                "structure": {
                    "dimensions": {
                        "series": _series_dimensions(),
                        "observation": [
                            {
                                "id": "TIME_PERIOD",
                                "values": [
                                    {"id": "2026-08-26"},
                                    {"id": "2026-08-27"},
                                    {"id": "2026-08-28"},
                                ],
                            }
                        ],
                    },
                    "attributes": {"series": []},
                },
                "dataSets": [
                    {
                        "series": {
                            "0:0:0:0": {"observations": {"0": [11.7], "2": [None]}},
                            "0:1:0:0": {"observations": {"1": [105.2]}},
                        }
                    }
                ],
            }
        }
    )

    result = await api.async_get_latest_rates(["SEK", "EUR", "EUR"], currencies)

    assert result["EUR"].value == 11.7
    assert result["EUR"].observation_date == "2026-08-26"
    assert result["SEK"].value == 105.2
    url = api._get_json.await_args.args[0]
    assert "/B.EUR+SEK.NOK.SP" in url


async def test_get_currencies_resolves_unit_multiplier() -> None:
    """Metadata attributes should define the published base amount."""
    api = NorgesBankApi(MagicMock())
    api._get_json = AsyncMock(
        return_value={
            "data": {
                "structure": {
                    "dimensions": {"series": _series_dimensions()},
                    "attributes": {
                        "series": [
                            {"id": "DECIMALS", "values": [{"id": "4"}]},
                            {"id": "UNIT_MULT", "values": [{"id": "2"}]},
                        ]
                    },
                },
                "dataSets": [{"series": {"0:1:0:0": {"attributes": [0, 0]}}}],
            }
        }
    )

    result = await api.async_get_currencies()

    assert result["SEK"].base_amount == 100
    assert result["SEK"].decimal_places == 4


async def test_get_currencies_rejects_invalid_response() -> None:
    """Invalid metadata should raise a domain-specific response error."""
    api = NorgesBankApi(MagicMock())
    api._get_json = AsyncMock(return_value={"data": {}})

    with pytest.raises(NorgesBankResponseError):
        await api.async_get_currencies()


def test_resolve_attributes_ignores_invalid_indexes() -> None:
    """Malformed optional attributes should not break the response."""
    definitions = [{"id": "UNIT_MULT", "values": [{"id": "2"}]}]
    assert _resolve_attributes(definitions, [99]) == {}
