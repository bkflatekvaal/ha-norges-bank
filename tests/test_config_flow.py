"""Tests for the Norges Bank config and options flows."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.norges_bank.api import NorgesBankConnectionError
from custom_components.norges_bank.const import (
    CONF_CURRENCIES,
    CONF_INCLUDE_POLICY_RATE,
    DOMAIN,
)
from custom_components.norges_bank.models import PolicyRate


async def test_user_flow(hass: HomeAssistant, currencies: dict) -> None:
    """A user can select currencies and create the sole entry."""
    with (
        patch(
            "custom_components.norges_bank.config_flow.NorgesBankApi.async_get_currencies",
            return_value=currencies,
        ),
        patch(
            "custom_components.norges_bank.config_flow.NorgesBankApi.async_get_policy_rate",
            return_value=PolicyRate(4.25, "2026-08-26", 2),
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] is FlowResultType.FORM

        with patch(
            "custom_components.norges_bank.async_setup_entry", return_value=True
        ):
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                {
                    CONF_CURRENCIES: ["EUR", "SEK"],
                    CONF_INCLUDE_POLICY_RATE: True,
                },
            )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        CONF_CURRENCIES: ["EUR", "SEK"],
        CONF_INCLUDE_POLICY_RATE: True,
    }


async def test_user_flow_policy_rate_connection_error(
    hass: HomeAssistant, currencies: dict
) -> None:
    """Policy-rate data should be validated before configuration is saved."""
    with (
        patch(
            "custom_components.norges_bank.config_flow.NorgesBankApi.async_get_currencies",
            return_value=currencies,
        ),
        patch(
            "custom_components.norges_bank.config_flow.NorgesBankApi.async_get_policy_rate",
            side_effect=NorgesBankConnectionError,
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_CURRENCIES: ["EUR"],
                CONF_INCLUDE_POLICY_RATE: True,
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_requires_currency(
    hass: HomeAssistant, currencies: dict
) -> None:
    """At least one currency is required."""
    with patch(
        "custom_components.norges_bank.config_flow.NorgesBankApi.async_get_currencies",
        return_value=currencies,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_CURRENCIES: []}
        )

    assert result["errors"] == {"base": "select_currency"}


async def test_user_flow_connection_error(hass: HomeAssistant) -> None:
    """An unavailable API aborts setup with a useful reason."""
    with patch(
        "custom_components.norges_bank.config_flow.NorgesBankApi.async_get_currencies",
        side_effect=NorgesBankConnectionError,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "cannot_connect"


async def test_user_flow_aborts_if_already_configured(hass: HomeAssistant) -> None:
    """Only one Norges Bank config entry is allowed."""
    MockConfigEntry(domain=DOMAIN, unique_id=DOMAIN).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_options_flow(hass: HomeAssistant, currencies: dict) -> None:
    """Options update the selected currencies."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_CURRENCIES: ["EUR"]})
    entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.norges_bank.config_flow.NorgesBankApi.async_get_currencies",
            return_value=currencies,
        ),
        patch.object(hass.config_entries, "async_reload"),
    ):
        result = await hass.config_entries.options.async_init(entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {CONF_CURRENCIES: ["SEK"]}
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options == {
        CONF_CURRENCIES: ["SEK"],
        CONF_INCLUDE_POLICY_RATE: False,
    }


async def test_options_flow_requires_currency(
    hass: HomeAssistant, currencies: dict
) -> None:
    """Options cannot remove every currency sensor."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_CURRENCIES: ["EUR"]})
    entry.add_to_hass(hass)

    with patch(
        "custom_components.norges_bank.config_flow.NorgesBankApi.async_get_currencies",
        return_value=currencies,
    ):
        result = await hass.config_entries.options.async_init(entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {CONF_CURRENCIES: []}
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "select_currency"}


async def test_options_flow_connection_error(hass: HomeAssistant) -> None:
    """An unavailable metadata API aborts the options flow."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_CURRENCIES: ["EUR"]})
    entry.add_to_hass(hass)

    with patch(
        "custom_components.norges_bank.config_flow.NorgesBankApi.async_get_currencies",
        side_effect=NorgesBankConnectionError,
    ):
        result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "cannot_connect"
