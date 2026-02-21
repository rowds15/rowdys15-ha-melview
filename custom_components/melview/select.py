"""MelView select entities."""

from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_SENSOR
from .coordinator import MelViewCoordinator
from .entity import MelViewBaseEntity
from .melview import VERTICAL_VANE, HORIZONTAL_VANE

_LOGGER = logging.getLogger(__name__)


class MelViewVerticalVaneSelect(MelViewBaseEntity, SelectEntity):
    """Vertical vane position select entity."""

    _attr_has_entity_name = True
    _attr_translation_key = "vertical_vane"

    def __init__(self, coordinator: MelViewCoordinator):
        """Initialize vertical vane select."""
        super().__init__(coordinator, coordinator.device)
        self._device = coordinator.device
        self._attr_unique_id = f"{coordinator.device.get_id()}_vertical_vane"

    @property
    def current_option(self) -> str | None:
        """Return current vertical vane position."""
        code = self.coordinator.data.get("airdir")
        return VERTICAL_VANE.get(code)

    @property
    def options(self) -> list[str]:
        """Return available vertical vane positions."""
        return list(VERTICAL_VANE.values())

    async def async_select_option(self, option: str) -> None:
        """Set vertical vane position."""
        _LOGGER.debug("Select vertical vane: %s", option)
        if await self._device.async_set_vertical_vane(option):
            await self.coordinator.async_refresh()


class MelViewHorizontalVaneSelect(MelViewBaseEntity, SelectEntity):
    """Horizontal vane position select entity."""

    _attr_has_entity_name = True
    _attr_translation_key = "horizontal_vane"

    def __init__(self, coordinator: MelViewCoordinator):
        """Initialize horizontal vane select."""
        super().__init__(coordinator, coordinator.device)
        self._device = coordinator.device
        self._attr_unique_id = f"{coordinator.device.get_id()}_horizontal_vane"

    @property
    def current_option(self) -> str | None:
        """Return current horizontal vane position."""
        code = self.coordinator.data.get("airdirh")
        return HORIZONTAL_VANE.get(code)

    @property
    def options(self) -> list[str]:
        """Return available horizontal vane positions."""
        return list(HORIZONTAL_VANE.values())

    async def async_select_option(self, option: str) -> None:
        """Set horizontal vane position."""
        _LOGGER.debug("Select horizontal vane: %s", option)
        if await self._device.async_set_horizontal_vane(option):
            await self.coordinator.async_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MelView select entities."""
    coordinators: list[MelViewCoordinator] = entry.runtime_data
    entities = []

    # Only create select entities if sensor option enabled
    if entry.options.get(CONF_SENSOR, True):
        for coordinator in coordinators:
            # Skip ERV units
            if coordinator.device.get_unit_type() == "ERV":
                continue

            # Add vertical vane select if supported
            if getattr(coordinator.device, "has_vertical_vane", False):
                entities.append(MelViewVerticalVaneSelect(coordinator))

            # Add horizontal vane select if supported
            if getattr(coordinator.device, "has_horizontal_vane", False):
                entities.append(MelViewHorizontalVaneSelect(coordinator))

    async_add_entities(entities, update_before_add=True)
