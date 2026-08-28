"""Constants for the Norges Bank integration."""

from datetime import timedelta

DOMAIN = "norges_bank"

API_BASE = "https://data.norges-bank.no/api/data/EXR"
METADATA_URL = (
    f"{API_BASE}/"
    "?apisrc=ha-norges-bank"
    "&format=sdmx-json"
    "&includeMetrics=true"
    "&detail=nodata"
    "&locale=no"
)

CONF_CURRENCIES = "currencies"

DEFAULT_CURRENCIES = ["EUR", "USD", "GBP", "SEK", "DKK"]
UPDATE_INTERVAL = timedelta(hours=6)

FREQUENCY = "B"
QUOTE_CURRENCY = "NOK"
TENOR = "SP"

ATTR_CURRENCY = "currency"
ATTR_CURRENCY_NAME = "currency_name"
ATTR_QUOTE_CURRENCY = "quote_currency"
ATTR_BASE_AMOUNT = "base_amount"
ATTR_OBSERVATION_DATE = "observation_date"
ATTR_SOURCE = "source"

SOURCE_NAME = "Norges Bank"
