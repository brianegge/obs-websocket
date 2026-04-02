"""Button platform for OBS WebSocket."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import OBSConfigEntry, OBSCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: OBSConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up OBS WebSocket buttons from a config entry."""
    coordinator = entry.runtime_data.coordinator

    async_add_entities(
        [
            OBSStartStreamButton(coordinator, entry),
            OBSStopStreamButton(coordinator, entry),
        ]
    )


class OBSButtonBase(CoordinatorEntity[OBSCoordinator], ButtonEntity):
    """Base class for OBS buttons."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: OBSCoordinator, entry: OBSConfigEntry) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"OBS Studio ({entry.data['host']})",
            manufacturer="OBS Project",
            sw_version=None,
        )
        self._connection = coordinator.connection


class OBSStartStreamButton(OBSButtonBase):
    """Button to start OBS streaming."""

    _attr_translation_key = "start_stream"

    def __init__(self, coordinator: OBSCoordinator, entry: OBSConfigEntry) -> None:
        """Initialize."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_start_stream"

    async def async_press(self) -> None:
        """Press the button to start streaming."""
        try:
            await self._connection.async_start_stream()
        except Exception as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="start_stream_failed",
                translation_placeholders={
                    "host": self._connection.host,
                    "error": str(err),
                },
            ) from err


class OBSStopStreamButton(OBSButtonBase):
    """Button to stop OBS streaming."""

    _attr_translation_key = "stop_stream"

    def __init__(self, coordinator: OBSCoordinator, entry: OBSConfigEntry) -> None:
        """Initialize."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_stop_stream"

    async def async_press(self) -> None:
        """Press the button to stop streaming."""
        try:
            await self._connection.async_stop_stream()
        except Exception as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="stop_stream_failed",
                translation_placeholders={
                    "host": self._connection.host,
                    "error": str(err),
                },
            ) from err
