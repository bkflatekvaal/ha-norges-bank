"""Config flow for Norges Bank."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api import NorgesBankApi, NorgesBankApiError
from .const import CONF_CURRENCIES, DEFAULT_CURRENCIES, DOMAIN
from .models import CurrencyInfo


def _currency_selector(
    currencies: dict[str, CurrencyInfo],
) -> SelectSelector:
    """Build the currency multi-select."""
    options = [
        SelectOptionDict(value=code, label=f"{info.name}, {code}")
        for code, info in currencies.items()
    ]
    return SelectSelector(
        SelectSelectorConfig(
            options=options,
            multiple=True,
            mode=SelectSelectorMode.DROPDOWN,
        )
    )


class NorgesBankConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Norges Bank."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle initial setup."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        api = NorgesBankApi(async_get_clientsession(self.hass))

        try:
            currencies = await api.async_get_currencies()
        except NorgesBankApiError:
            return self.async_abort(reason="cannot_connect")

        available_defaults = [code for code in DEFAULT_CURRENCIES if code in currencies]

        if user_input is not None:
            selected = list(user_input[CONF_CURRENCIES])
            if not selected:
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema(
                        {
                            vol.Required(
                                CONF_CURRENCIES,
                                default=available_defaults,
                            ): _currency_selector(currencies)
                        }
                    ),
                    errors={"base": "select_currency"},
                )

            return self.async_create_entry(
                title="Norges Bank",
                data={CONF_CURRENCIES: selected},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_CURRENCIES,
                        default=available_defaults,
                    ): _currency_selector(currencies)
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        _config_entry: ConfigEntry,
    ) -> OptionsFlowWithReload:
        """Return the options flow."""
        return NorgesBankOptionsFlow()


class NorgesBankOptionsFlow(OptionsFlowWithReload):
    """Allow changing selected currencies."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Manage currencies."""
        api = NorgesBankApi(async_get_clientsession(self.hass))

        try:
            currencies = await api.async_get_currencies()
        except NorgesBankApiError:
            return self.async_abort(reason="cannot_connect")

        configured = list(
            self.config_entry.options.get(
                CONF_CURRENCIES,
                self.config_entry.data.get(CONF_CURRENCIES, DEFAULT_CURRENCIES),
            )
        )
        current = [code for code in configured if code in currencies]

        if user_input is not None:
            selected = list(user_input[CONF_CURRENCIES])
            if not selected:
                return self.async_show_form(
                    step_id="init",
                    data_schema=vol.Schema(
                        {
                            vol.Required(
                                CONF_CURRENCIES,
                                default=current,
                            ): _currency_selector(currencies)
                        }
                    ),
                    errors={"base": "select_currency"},
                )

            return self.async_create_entry(data={CONF_CURRENCIES: selected})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_CURRENCIES,
                        default=current,
                    ): _currency_selector(currencies)
                }
            ),
        )
