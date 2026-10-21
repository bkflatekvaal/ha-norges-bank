# Changelog

## Unreleased

- Correct the duplicate-setup test to expect Home Assistant's built-in
  `single_instance_allowed` abort reason.
- Temporarily omit the optional Marketplace category because the published
  Hassfest validator rejects the `categories` manifest field. Restore Finance
  when the validator supports it.

## v0.1.1

Patch release prepared on 2026-10-21. Requires Home Assistant 2026.8.0 or newer.

- Add the Finance category for Marketplace discovery and a direct integration
  setup link in the README.
- Fix CI installation so Home Assistant scans real directories instead of
  editable-install import hooks.
- Run repair-notification setup tests through Home Assistant's config-entry
  lifecycle.
- Correct the Norwegian Bokmål spelling in the README.

No changes to exchange-rate or policy-rate sensor behavior. Existing
configuration is preserved.

## v0.1.0

First release, prepared on 2026-10-21. Requires Home Assistant 2026.8.0 or newer.

### Features

- Exchange-rate sensors using Norges Bank's public SDMX-JSON API, with no account
  or credentials required.
- UI setup and configuration with a dynamically loaded currency list and one
  sensor per selected currency.
- Combined exchange-rate requests and automatic updates every six hours.
- Published quotation amounts and decimal precision are preserved, including
  100-unit quotations. Sensor attributes include the quotation amount, observation
  date and source.
- Optional policy-rate sensor (styringsrenten).
- English and Norwegian Bokmål translations, localized sensor names and stable
  sensor identifiers.
- Repair notifications when selected currencies disappear from the API, and
  retry handling for temporary connection failures.
- Downloadable diagnostics with public rate data and update status.
- HACS metadata, integration icons and logos, installation instructions, and an
  MIT license.

### Fixes and privacy

- Diagnostics omit configuration dictionaries, entry titles and identifiers, and
  raw exception messages. Only the exception class name is exported, preventing
  credentials, URLs and local network details in error messages from leaking.
- Diagnostics handle missing coordinator rate data.
- Rate parsing selects the latest valid observation by date, regardless of the
  order of SDMX indexes.
- Invalid numbers, non-finite values and invalid observation indexes are skipped
  so an older valid observation can still be used.

Home Assistant adds its own standard system and integration information around
the integration's diagnostics, including the time zone and installed custom
integrations.

### Development

- Tests cover API parsing, configuration, setup, coordinator updates, sensors and
  diagnostics, including regression tests for private data in diagnostics.
- GitHub Actions includes HACS validation, Hassfest, Python tests and Ruff checks.
- The Home Assistant test plugin is pinned to match Home Assistant 2026.8.0.
- Explicit package discovery and test dependencies support editable installs
  with the test extras.

## Development history before the first release

The repository has no earlier version tags or published releases. The entries
below summarize the existing Git commits; they are not separate releases.
All five commits are dated 2026-08-28.

| Commit | Changes |
| --- | --- |
| [27b8e70](https://github.com/bkflatekvaal/ha-norges-bank/commit/27b8e70f93b1e08ab76509ba137c0e01515a71d7) | Added the optional policy-rate sensor, configuration toggle, API parsing and tests. |
| [18dfe8e](https://github.com/bkflatekvaal/ha-norges-bank/commit/18dfe8ebeca8b040522ace6d3409b2b2e8de3119) | Added the MIT license, localized entity names, stable sensor IDs and issue-tracker link. |
| [7063567](https://github.com/bkflatekvaal/ha-norges-bank/commit/7063567626d069809f1152491e65b61f1c6da577) | Added tests, diagnostics, repair notifications, HACS/Hassfest validation, brand assets and published display precision. |
| [1a3c748](https://github.com/bkflatekvaal/ha-norges-bank/commit/1a3c748a988e576e235d2db0f8af28eb62d581d6) | Implemented the exchange-rate integration, UI configuration, combined requests, six-hour polling, sensors, translations and HACS metadata. |
| [2f425bf](https://github.com/bkflatekvaal/ha-norges-bank/commit/2f425bfc868af65957b4eeaec8700e9305504f85) | Initialized the repository with Git attributes. |
