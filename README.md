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
- Uses Norges Bank's published decimal precision as the initial display precision.
- Provides downloadable diagnostics from the integration menu.
- Creates a repair notification if a selected currency disappears from the API.
- Can optionally create a sensor for Norges Bank's policy rate (styringsrenten).

Example entity:

- `sensor.exchange_rate_nok_eur`
- Friendly name: `Exchange rate NOK/EUR` (localized by Home Assistant)
- State: latest Norges Bank quotation
- Unit: `NOK`
- Attributes: currency, currency name, quote currency, base amount, observation date and source.

Optional policy-rate entity:

- `sensor.norges_bank_policy_rate`
- Friendly name: `Policy rate` / `Styringsrente`
- State: latest published policy rate
- Unit: `%`
- Attributes: instrument type (`KPRA`), tenor (`SD`), unit measure (`R`), collection (`E`), observation date and source.

## Installation

### HACS

1. Install and configure [HACS](https://hacs.xyz/) if it is not already available.
2. Open HACS in Home Assistant.
3. Open the menu in the upper-right corner and select **Custom repositories**.
4. Enter `https://github.com/bkflatekvaal/ha-norges-bank` as the repository URL.
5. Select **Integration** as the category, then select **Add**.
6. Find **Norges Bank** in HACS and select **Download**.
7. Restart Home Assistant.
8. Go to **Settings → Devices & services → Add integration**, search for **Norges Bank**, and select the currencies to monitor.

### Manual installation

1. Download this repository from [GitHub](https://github.com/bkflatekvaal/ha-norges-bank).
2. Copy `custom_components/norges_bank` into `<config>/custom_components/norges_bank` on the Home Assistant system.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration**, search for **Norges Bank**, and select the currencies to monitor.

To update a manual installation, replace the existing `custom_components/norges_bank` directory with the directory from the new release and restart Home Assistant.

## Run tests

Home Assistant 2026.8 requires Python 3.14.2 or newer.

```shell
python -m pip install -e ".[test]"
pytest
ruff check .
ruff format --check .
```

## API endpoints

Metadata:

`https://data.norges-bank.no/api/data/EXR/?format=sdmx-json&detail=nodata&locale=no`

Rates are requested as one combined series, for example:

`https://data.norges-bank.no/api/data/EXR/B.EUR+GBP+USD.NOK.SP?...`

The parser intentionally resolves SDMX dimensions and attributes by their IDs rather than relying on fixed positions where possible.

## License

This project is licensed under the [MIT License](LICENSE).
