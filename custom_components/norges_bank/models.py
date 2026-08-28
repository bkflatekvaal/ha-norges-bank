"""Data models for the Norges Bank integration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CurrencyInfo:
    """Metadata about a currency series."""

    code: str
    name: str
    unit_multiplier: int = 0
    decimal_places: int | None = None

    @property
    def base_amount(self) -> int:
        """Return the quoted number of base currency units."""
        return 10**self.unit_multiplier


@dataclass(frozen=True, slots=True)
class ExchangeRate:
    """Latest exchange rate observation."""

    currency: CurrencyInfo
    value: float
    observation_date: str
