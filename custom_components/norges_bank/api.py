"""Norges Bank SDMX-JSON API client."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import (
    API_BASE,
    FREQUENCY,
    METADATA_URL,
    QUOTE_CURRENCY,
    TENOR,
)
from .models import CurrencyInfo, ExchangeRate

_LOGGER = logging.getLogger(__name__)


class NorgesBankApiError(Exception):
    """Base API error."""


class NorgesBankConnectionError(NorgesBankApiError):
    """Connection error."""


class NorgesBankResponseError(NorgesBankApiError):
    """Unexpected API response."""


class NorgesBankApi:
    """Small client for Norges Bank's SDMX-JSON exchange-rate API."""

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def async_get_currencies(self) -> dict[str, CurrencyInfo]:
        """Return available business-day spot currencies quoted in NOK."""
        payload = await self._get_json(METADATA_URL)

        try:
            data = payload["data"]
            structure = data["structure"]
            dataset = data["dataSets"][0]
            dimensions = structure["dimensions"]["series"]
            series = dataset["series"]
        except (KeyError, IndexError, TypeError) as err:
            raise NorgesBankResponseError("Invalid metadata response") from err

        dim_ids = [dimension["id"] for dimension in dimensions]
        dim_values = {
            dimension["id"]: dimension.get("values", []) for dimension in dimensions
        }

        required = {"FREQ", "BASE_CUR", "QUOTE_CUR", "TENOR"}
        if not required.issubset(dim_ids):
            raise NorgesBankResponseError("Required EXR dimensions are missing")

        currencies: dict[str, CurrencyInfo] = {}

        for series_key, series_data in series.items():
            key_parts = series_key.split(":")
            if len(key_parts) != len(dim_ids):
                continue

            selected: dict[str, dict[str, Any]] = {}
            invalid = False
            for dim_id, raw_index in zip(dim_ids, key_parts, strict=True):
                try:
                    selected[dim_id] = dim_values[dim_id][int(raw_index)]
                except (ValueError, IndexError):
                    invalid = True
                    break
            if invalid:
                continue

            if (
                selected["FREQ"]["id"] != FREQUENCY
                or selected["QUOTE_CUR"]["id"] != QUOTE_CURRENCY
                or selected["TENOR"]["id"] != TENOR
            ):
                continue

            base = selected["BASE_CUR"]
            code = str(base["id"])
            name = str(base.get("name") or code)

            # The metadata response contains UNIT_MULT as a series attribute.
            # Resolve it generically instead of relying on a fixed attribute index.
            attributes = _resolve_attributes(
                structure.get("attributes", {}).get("series", []),
                series_data.get("attributes", []),
            )
            unit_multiplier = _safe_int(attributes.get("UNIT_MULT", {}).get("id"), 0)
            decimal_places = _optional_int(attributes.get("DECIMALS", {}).get("id"))

            currencies[code] = CurrencyInfo(
                code=code,
                name=name,
                unit_multiplier=unit_multiplier,
                decimal_places=decimal_places,
            )

        if not currencies:
            raise NorgesBankResponseError("No NOK spot currencies found in metadata")

        return dict(sorted(currencies.items()))

    async def async_get_latest_rates(
        self,
        currencies: list[str],
        currency_info: dict[str, CurrencyInfo] | None = None,
    ) -> dict[str, ExchangeRate]:
        """Fetch the latest available rate for each selected currency."""
        if not currencies:
            return {}

        # A 14-day lookback safely spans weekends and ordinary holiday periods.
        end_period = date.today()
        start_period = end_period - timedelta(days=14)

        codes = "+".join(sorted(set(currencies)))
        url = (
            f"{API_BASE}/{FREQUENCY}.{codes}.{QUOTE_CURRENCY}.{TENOR}"
            "?format=sdmx-json"
            f"&startPeriod={start_period.isoformat()}"
            f"&endPeriod={end_period.isoformat()}"
            "&locale=no"
        )
        payload = await self._get_json(url)

        try:
            data = payload["data"]
            structure = data["structure"]
            dataset = data["dataSets"][0]
            dimensions = structure["dimensions"]
            series_dimensions = dimensions["series"]
            observation_dimensions = dimensions["observation"]
            series = dataset["series"]
        except (KeyError, IndexError, TypeError) as err:
            raise NorgesBankResponseError("Invalid exchange-rate response") from err

        series_dim_ids = [dimension["id"] for dimension in series_dimensions]
        series_dim_values = {
            dimension["id"]: dimension.get("values", [])
            for dimension in series_dimensions
        }

        time_dimension = next(
            (
                dimension
                for dimension in observation_dimensions
                if dimension.get("id") == "TIME_PERIOD"
            ),
            None,
        )
        if time_dimension is None:
            raise NorgesBankResponseError("TIME_PERIOD dimension is missing")

        time_values = time_dimension.get("values", [])
        result: dict[str, ExchangeRate] = {}

        for series_key, series_data in series.items():
            key_parts = series_key.split(":")
            if len(key_parts) != len(series_dim_ids):
                continue

            selected: dict[str, dict[str, Any]] = {}
            invalid = False
            for dim_id, raw_index in zip(series_dim_ids, key_parts, strict=True):
                try:
                    selected[dim_id] = series_dim_values[dim_id][int(raw_index)]
                except (ValueError, IndexError):
                    invalid = True
                    break
            if invalid:
                continue

            base = selected.get("BASE_CUR")
            if not base:
                continue

            code = str(base["id"])
            observations = series_data.get("observations", {})
            if not observations:
                continue

            valid_observations: list[tuple[int, list[Any]]] = []
            for raw_index, observation in observations.items():
                try:
                    index = int(raw_index)
                except (TypeError, ValueError):
                    continue
                if observation and observation[0] is not None:
                    valid_observations.append((index, observation))

            if not valid_observations:
                continue

            latest_index, observation = max(valid_observations)

            try:
                value = float(observation[0])
                time_value = time_values[latest_index]
                observation_date = str(
                    time_value.get("id") or time_value.get("name") or ""
                )
            except (ValueError, TypeError, IndexError):
                continue

            info = None if currency_info is None else currency_info.get(code)
            if info is None:
                attrs = _resolve_attributes(
                    structure.get("attributes", {}).get("series", []),
                    series_data.get("attributes", []),
                )
                unit_multiplier = _safe_int(attrs.get("UNIT_MULT", {}).get("id"), 0)
                decimal_places = _optional_int(attrs.get("DECIMALS", {}).get("id"))
                info = CurrencyInfo(
                    code=code,
                    name=str(base.get("name") or code),
                    unit_multiplier=unit_multiplier,
                    decimal_places=decimal_places,
                )

            result[code] = ExchangeRate(
                currency=info,
                value=value,
                observation_date=observation_date,
            )

        return result

    async def _get_json(self, url: str) -> dict[str, Any]:
        try:
            async with self._session.get(url, timeout=20) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (ClientError, TimeoutError, ValueError) as err:
            raise NorgesBankConnectionError(str(err)) from err

        if not isinstance(payload, dict):
            raise NorgesBankResponseError("API returned a non-object response")
        return payload


def _resolve_attributes(
    definitions: list[dict[str, Any]],
    values: list[int | None],
) -> dict[str, dict[str, Any]]:
    """Resolve SDMX indexed attributes to their value objects."""
    resolved: dict[str, dict[str, Any]] = {}

    for definition, raw_index in zip(definitions, values, strict=False):
        if raw_index is None:
            continue
        try:
            resolved[definition["id"]] = definition.get("values", [])[int(raw_index)]
        except (KeyError, IndexError, TypeError, ValueError):
            continue

    return resolved


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
