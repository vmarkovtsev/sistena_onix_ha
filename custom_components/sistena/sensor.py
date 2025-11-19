"""Support for Sistena Onix sensors."""

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DATA_DEVICES
from .climate import Regulator


class SistenaSensor(SensorEntity):
    """Base sensor class for Sistena Onix sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        regulator: Regulator,
        device_class: SensorDeviceClass,
        state_class: SensorStateClass,
        unit: str,
    ) -> None:
        """Initialize the sensor."""
        self._regulator = regulator
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return f"{self._regulator.unique_id}_{self.cls_name.lower()}"

    @property
    def cls_name(self) -> str:
        """Return the class name of the sensor."""
        return type(self).__name__.removesuffix("Sensor")
    
    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._regulator.name}_{self.cls_name}"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return the device info."""
        info = self._regulator.device_info.copy()
        info["name"] = self.name
        return info


class TemperatureSensor(SistenaSensor):
    """Temperature sensor for Sistena Onix devices."""

    def __init__(self, regulator: Regulator) -> None:
        """Initialize the temperature sensor."""
        super().__init__(
            regulator,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            UnitOfTemperature.CELSIUS,
        )

    @property
    def native_value(self) -> float:
        return self._regulator.current_temperature


class HumiditySensor(SistenaSensor):
    """Humidity sensor for Sistena Onix devices."""

    def __init__(self, regulator: Regulator) -> None:
        """Initialize the humidity sensor."""
        super().__init__(
            regulator,
            SensorDeviceClass.HUMIDITY,
            SensorStateClass.MEASUREMENT,
            "%",
        )

    @property
    def native_value(self) -> float:
        return self._regulator.current_humidity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][config_entry.entry_id]
    devices = data[DATA_DEVICES]

    entries = []
    for device in devices:
        entries.extend([TemperatureSensor(device), HumiditySensor(device)])

    async_add_entities(entries)
