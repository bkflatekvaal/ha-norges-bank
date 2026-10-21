# Norges Bank for Home Assistant

Follow exchange rates and the Norwegian policy rate (styringsrenten) in Home Assistant using public data from Norges Bank. No account or API key is needed.

Requires **Home Assistant 2026.8.0 or newer**.

## Features

- Choose the currencies you want to follow, with one sensor per currency.
- Optionally include a policy-rate sensor.
- Updates automatically every six hours.
- Shows the latest published observation and its date, including over weekends and holidays.
- Available in English and Norwegian Bokmål.

Rates are quoted in Norwegian kroner (NOK). Some currencies are quoted per **100 units**, rather than per unit. The sensor's `base_amount` attribute shows the amount used by Norges Bank.

## Installation

### With HACS

For now, add this integration as a custom repository in [HACS](https://hacs.xyz/).

1. Open **HACS** in Home Assistant.
2. Open the menu and select **Custom repositories**.
3. Enter `https://github.com/bkflatekvaal/ha-norges-bank` and select **Integration** as the category.
4. Select **Add**, then find **Norges Bank** in HACS and download it.
5. Restart Home Assistant.
6. Follow the setup instructions below.

### Manual installation

1. Download the code from [this repository](https://github.com/bkflatekvaal/ha-norges-bank) and extract it.
2. Copy the `custom_components/norges_bank` folder into the `custom_components` folder in your Home Assistant configuration directory. Create `custom_components` if it does not exist.
3. Restart Home Assistant.
4. Follow the setup instructions below.

## Setup

After installation, [set up Norges Bank in Home Assistant](https://my.home-assistant.io/redirect/config_flow_start/?domain=norges_bank), or follow these steps:

1. Go to **Settings > Devices & services > Add integration**.
2. Search for **Norges Bank**.
3. Select the currencies you want to follow and whether to include the policy rate.

To change your selection later, open **Settings > Devices & services > Norges Bank > Configure**. No YAML configuration is needed.

Example sensors:

| Sensor | What it shows |
| --- | --- |
| `sensor.exchange_rate_nok_eur` | The latest published EUR quotation in NOK |
| `sensor.norges_bank_policy_rate` | The latest published policy rate in percent |

## Updates

With HACS, download available updates from HACS and restart Home Assistant.

For a manual installation, replace the `custom_components/norges_bank` folder with the updated folder and restart Home Assistant.

## Help and diagnostics

If data is unavailable, check your internet connection. The integration retries temporary connection failures automatically. If a selected currency is no longer offered, Home Assistant shows a repair notification.

You can download diagnostics from the integration menu when reporting a problem. The integration includes selected currencies, public rate data and update status, and excludes raw configuration and error messages. Home Assistant also adds standard system information, including the time zone and installed custom integrations.

Report problems in [GitHub Issues](https://github.com/bkflatekvaal/ha-norges-bank/issues).

## Changelog and license

See the [changelog](CHANGELOG.md) for changes. This project uses the [MIT License](LICENSE).
