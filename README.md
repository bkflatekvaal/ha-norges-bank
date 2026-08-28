# Norges Bank for Home Assistant

Custom Home Assistant integration for exchange rates from Norges Bank's open EXR API.

## What it does

- UI/config-flow only; no YAML configuration.
- Loads the current list of available currencies dynamically from Norges Bank metadata.
- Lets the user select multiple currencies.
- Creates one sensor per selected currency.
- Uses one combined EXR request for all selected currencies.
- Uses Norges Bank's published quotation unchanged, including 100-unit quotations such as SEK/DKK where applicable.
- Stores the quotation amount in the `base_amount` attribute.
- Uses the latest available business-day observation and keeps the observation date as an attribute.
- Currency selection can be changed later through **Configure**.
- Polls every 6 hours.

Example entity:

- `sensor.norges_bank_eur`
- Friendly name: `Euro, EUR`
- State: latest Norges Bank quotation
- Unit: `NOK`
- Attributes: currency, currency name, quote currency, base amount, observation date and source.

## Install for development

Copy:

`custom_components/norges_bank`

to:

`<config>/custom_components/norges_bank`

Restart Home Assistant, then go to:

**Settings → Devices & services → Add integration → Norges Bank**

## API endpoints

Metadata:

`https://data.norges-bank.no/api/data/EXR/?format=sdmx-json&detail=nodata&locale=no`

Rates are requested as one combined series, for example:

`https://data.norges-bank.no/api/data/EXR/B.EUR+GBP+USD.NOK.SP?...`

## Notes for Codex / next iteration

Good next steps:

1. Run Home Assistant `hassfest` and `pytest` against the target HA version.
2. Verify the exact SDMX `UNIT_MULT` attribute resolution against live responses for DKK/SEK/JPY.
3. Add tests with captured, sanitized API fixtures.
4. Consider using the SDMX `DECIMALS` metadata to control suggested display precision.
5. Add diagnostics.
6. Add repairs if the API removes a previously selected currency.
7. Add HACS validation workflow and hassfest workflow before publishing.
8. Add brand assets only after repository naming/domain are final.

The parser intentionally resolves SDMX dimensions and attributes by their IDs rather than relying on fixed positions where possible.
