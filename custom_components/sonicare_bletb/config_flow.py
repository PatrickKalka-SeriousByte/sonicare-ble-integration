"""Config flow for SonicareBLETB integration."""
from __future__ import annotations

import logging
from typing import Any

from bluetooth_data_tools import human_readable_name
from sonicare_bletb import BLEAK_EXCEPTIONS, SonicareBLETB
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.const import CONF_ADDRESS
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, LOCAL_NAMES

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SonicareBLETB."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle the bluetooth discovery step."""
        _LOGGER.debug("Bluetooth discovery received: %s", discovery_info)

        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {
            "name": human_readable_name(
                None, discovery_info.name, discovery_info.address
            )
        }
        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the user step to pick discovered device."""
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            _LOGGER.debug("User selected address: %s", address)

            discovery_info = self._discovered_devices[address]
            local_name = discovery_info.name
            _LOGGER.debug("Initializing device: %s (%s)", local_name, discovery_info.address)

            await self.async_set_unique_id(
                discovery_info.address, raise_on_progress=False
            )
            self._abort_if_unique_id_configured()

            sonicare_ble = SonicareBLETB(discovery_info.device)
            try:
                await sonicare_ble.initialise()
            except BLEAK_EXCEPTIONS as e:
                _LOGGER.warning("Connection failed to %s: %s", address, e)
                errors["base"] = "cannot_connect"
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error during initialise: %s", e)
                errors["base"] = "unknown"
            else:
                _LOGGER.debug("Initialization succeeded, stopping device")
                await sonicare_ble.stop()
                return self.async_create_entry(
                    title=local_name,
                    data={CONF_ADDRESS: discovery_info.address},
                )

        if discovery := self._discovery_info:
            _LOGGER.debug("Using direct discovery: %s", discovery.address)
            self._discovered_devices[discovery.address] = discovery
        else:
            current_addresses = self._async_current_ids()
            _LOGGER.debug("Running manual discovery...")
            for discovery in async_discovered_service_info(self.hass):
                _LOGGER.debug("Found device: %s (%s)", discovery.name, discovery.address)

                if discovery.address in current_addresses:
                    _LOGGER.debug("Skipping already configured device: %s", discovery.address)
                    continue
                if discovery.address in self._discovered_devices:
                    _LOGGER.debug("Skipping already discovered device: %s", discovery.address)
                    continue
                if not any(
                    discovery.name.startswith(local_name)
                    for local_name in LOCAL_NAMES
                ):
                    _LOGGER.debug(
                        "Device %s (%s) does not match LOCAL_NAMES %s → skipped",
                        discovery.address, discovery.name, LOCAL_NAMES
                    )
                    continue

                _LOGGER.debug("Accepted device: %s (%s)", discovery.name, discovery.address)
                self._discovered_devices[discovery.address] = discovery

        if not self._discovered_devices:
            _LOGGER.warning("No matching Sonicare devices found.")
            return self.async_abort(reason="no_devices_found")

        _LOGGER.debug("Presenting selection form with devices: %s", list(self._discovered_devices.keys()))
        data_schema = vol.Schema(
            {
                vol.Required(CONF_ADDRESS): vol.In(
                    {
                        service_info.address: f"{service_info.name} ({service_info.address})"
                        for service_info in self._discovered_devices.values()
                    }
                ),
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
