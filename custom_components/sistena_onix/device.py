"""
Sistena Onix Device Class.

This module defines the Device class for interacting with Sistena Onix devices.
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode, FAN_AUTO, FAN_HIGH, FAN_LOW, FAN_OFF, TEMP_CELSIUS
from homeassistant.core import callback
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import SistenaOnixAPI
from .const import DOMAIN


@dataclass(slots=True)
class RawRegulator:
    """Represents a Sistena Onix device."""
    
    id: str
    mac: str
    status: str
    fw_name: str
    version: str
    dbm: str
    ip_public: str
    lastboot: str
    date_of_register: datetime
    device_model: str
    device_description: str
    icon: str
    
    registers: list[int]
    
    _parsed_properties: dict[str, bool | int | float | str] = field(default_factory=dict)

    @property
    def parsed_properties(self) -> dict[str, bool | int | float | str]:
        return self._parsed_properties
    
    def __post_init__(self):
        """Initialize additional properties after dataclass initialization."""
        self._parse_registers()
    
    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> "RawRegulator":
        """Create a RawRegulator instance from JSON data."""
        try:
            return cls._from_json(json_data)
        except KeyError as e:
            raise ValueError(f"Missing required key in JSON data: {e}") from None
    
    @classmethod
    def _from_json(cls, json_data: dict[str, Any]) -> "RawRegulator":
        """Internal method to create RawRegulator instance from JSON data."""
        # Extract device data
        device_data = json_data["device"]
        
        # Extract basic device information
        id_val = device_data["_id"]
        mac = device_data["MAC"]
        status = device_data["status"]
        fw_name = device_data["fwName"]
        version = device_data["version"]
        dbm = device_data["dBm"]
        ip_public = device_data["ipPublic"]
        lastboot = device_data["lastboot"]
        
        # Parse date_of_register
        date_of_register = datetime.fromtimestamp(device_data["dateOfRegister"] / 1000, UTC)
        
        # Extract model information
        model_data = device_data["model"]
        device_model = model_data["model"]
        device_description = model_data["deviceDescription"]
        icon = model_data["icon"]
        
        # Extract registers
        registers = device_data["registers"]
        
        # Create and return instance
        return cls(
            id=id_val,
            mac=mac,
            status=status,
            fw_name=fw_name,
            version=version,
            dbm=dbm,
            ip_public=ip_public,
            lastboot=lastboot,
            date_of_register=date_of_register,
            device_model=device_model,
            device_description=device_description,
            icon=icon,
            registers=registers,
        )
    
    def _parse_registers(self):
        """Parse the raw registers into a more accessible format."""
        # Parse registers with special handling for multi-byte registers
        registers = self.registers
        _parsed_properties = self._parsed_properties

        # register 0
        _parsed_properties["device_id"] = registers[0]
        # register 1 not interesting
        # register 2 upper byte
        try:
            _parsed_properties["config_suelo_radiante"] = [
                "no", "cooling", "heating", "cooling and heating"
            ][(registers[2] & 0xFF00) >> 8]
        except IndexError:
            _parsed_properties["config_suelo_radiante"] = "error"
        # register 2 lower byte
        try:
            _parsed_properties["config_fan-coil"] = [
                "no", "cooling", "heating", "cooling and heating"
            ][registers[2] & 0x00FF]
        except IndexError:
            _parsed_properties["config_fan-coil"] = "error"
        # register 3
        _parsed_properties["status"] = bool(registers[3])
        # register 4
        try:
            _parsed_properties["selection_of_operation"] = [
                "teclado", "entrada digital", "modbus"
            ][registers[4]]
        except IndexError:
            _parsed_properties["selection_of_operation"] = "error"
        # register 5
        _parsed_properties["mode_operation"] = "heat" if registers[5] else "cool" 
        # register 6
        try:
            _parsed_properties["contact_operation"] = [
                "abierto (frío), cerrado (calor)",
                "abierto (calor), cerrado (frío)",
            ][registers[6]]
        except IndexError:
            _parsed_properties["contact_operation"] = "error"
        # register 7
        try:
            _parsed_properties["selection_normal_eco"] = [
                "teclado", "entrada digital", "modbus"
            ][registers[7]]
        except IndexError:
            _parsed_properties["selection_normal_eco"] = "error"
        # register 8
        _parsed_properties["mode_normal_eco"] = "eco" if registers[8] else "normal"
        # register 9
        try:
            _parsed_properties["contact_normal_eco"] = [
                "abierto (normal), cerrado (eco)",
                "abierto (eco), cerrado (normal)",
            ][registers[9]]
        except IndexError:
            _parsed_properties["contact_normal_eco"] = "error"
        # register 10
        _parsed_properties["instruction_temperature_cold_normal"] = registers[10]
        # register 11
        _parsed_properties["instruction_temperature_cold_eco"] = registers[11]
        # register 12
        _parsed_properties["instruction_temperature_hot_normal"] = registers[12]
        # register 13
        _parsed_properties["instruction_temperature_hot_eco"] = registers[13]
        # register 14
        _parsed_properties["histeresis_stage_suelo_radiante"] = registers[14] / 10.0
        # register 15 upper byte
        _parsed_properties["histeresis_stage_fan-coil_cold"] = ((registers[15] & 0xFF00) >> 8) / 10.0
        # register 15 lower byte
        _parsed_properties["histeresis_stage_fan-coil_hot"] = registers[15] & 0x00FF / 10.0
        # register 16
        _parsed_properties["mode_fan"] = "continuous" if registers[16] == 0 else "auto"
        # register 17
        try:
            _parsed_properties["speed_fan_ac"] = [
                "auto", "low", "high"
            ][registers[17]]
        except IndexError:
            _parsed_properties["speed_fan_ac"] = "error"
        # register 18 upper byte
        _parsed_properties["difference_speeds"] = (registers[18] & 0xFF00) >> 8 / 10.0
        # register 18 lower byte
        _parsed_properties["histeresis_speeds"] = registers[18] & 0x00FF / 10.0
        # register 19
        _parsed_properties["proportional_band_fan_ec"] = registers[19] / 10.0
        # register 20 upper byte
        _parsed_properties["speed_min"] = (registers[20] & 0xFF00) >> 8
        # register 20 lower byte
        _parsed_properties["speed_max"] = registers[20] & 0x00FF
        # register 21
        try:
            _parsed_properties["mode_dryer"] = [
                "no", "cooling", "heating", "cooling and heating"
            ][registers[21]]
        except IndexError:
            _parsed_properties["mode_dryer"] = "error"
        # register 22 upper byte
        _parsed_properties["instruction_dryer"] = (registers[22] & 0xFF00) >> 8
        # register 22 lower byte
        _parsed_properties["histeresis_dryer"] = registers[22] & 0x00FF
        # register 23
        _parsed_properties["valve_suelo_radiante"] = "closed" if registers[23] else "open"
        # register 24
        _parsed_properties["offset_temperature"] = registers[24] / 10.0
        # register 25
        _parsed_properties["offset_humidity"] = registers[25] / 10.0
        # register 26
        _parsed_properties["temperature"] = registers[26] / 10.0
        # register 27
        _parsed_properties["relative_humidity"] = registers[27] / 10.0
        # register 28
        _parsed_properties["mode_cold_hot_actual"] = "heat" if registers[28] else "cool"
        # register 29
        _parsed_properties["mode_normal_eco_actual"] = "eco" if registers[29] else "normal"
        # register 30
        _parsed_properties["instruction_temperature_actual"] = registers[30]
        # register 31
        _parsed_properties["state_valve_suelo_radiante"] = bool(registers[31])
        # register 32
        _parsed_properties["state_valve_fan-coil"] = bool(registers[32])
        # register 33 upper byte
        try:
            _parsed_properties["fan_ac_state"] = [
                "off", "on velocidad baja", "on velocidad alta"
            ][(registers[33] & 0xFF00) >> 8]
        except IndexError:
            _parsed_properties["fan_ac_state"] = "error"
        # register 33 lower byte
        _parsed_properties["fan_ec_speed"] = registers[33] & 0x00FF
        # register 34
        _parsed_properties["state_dryer"] = bool(registers[34])
        # register 35
        _parsed_properties["version_firmware"] = "%d.%d" % divmod(registers[35], 10)

    def get_args_for_temperature(self, temperature: float) -> tuple[int, int]:
        """Generate POST body for setting temperature."""
        # Determine the correct register based on current HVAC mode and preset mode
        hvac_mode = self.parsed_properties["mode_cold_hot_actual"]
        preset_mode = self.parsed_properties["mode_normal_eco_actual"]
        
        # Choose register based on heating/cooling and eco/normal states
        if hvac_mode == "cool":
            if preset_mode == "eco":
                register = 11  # instruction_temperature_cold_eco
            else:
                register = 10  # instruction_temperature_cold_normal
        else:  # heat mode
            if preset_mode == "eco":
                register = 13  # instruction_temperature_hot_eco
            else:
                register = 12  # instruction_temperature_hot_normal
                
        return register, int(temperature)
    
    def get_args_for_operation(self, mode: Literal["heat", "cool"]) -> tuple[int, int]:
        """Generate POST body for setting temperature."""
        # Assuming temperature is sent to register 30 (instruction_temperature_actual)
        return 5, int(mode == "heat")
    
    def get_args_for_fan_speed(self, speed: Literal["auto", "low", "high"]) -> tuple[int, int]:
        match speed:
            case "auto":
                register_value = 0
            case "low":
                register_value = 1
            case "high":
                register_value = 2
            case _:
                raise AsserionError(f"Bad speed: {speed}")
        return 17, register_value
    
    def get_args_for_normal_eco(self, normal_eco: Literal["eco", "normal"]) -> tuple[int, int]:
        return 8, int(normal_eco == "eco")

    def get_args_for_on_off(self, state: bool) -> tuple[int, int]:
        """Generate POST body for setting device on/off state."""
        # Register 3 controls the device status
        return 3, int(state)


class Regulator(ClimateEntity):
    """Climate entity for Sistena Onix regulator devices."""
    
    _attr_has_entity_name = True
    
    def __init__(self, raw_regulator: RawRegulator, api: SistenaOnixAPI) -> None:
        """Initialize the regulator entity."""
        self._raw_regulator = raw_regulator
        self._api = api
        
    @property
    def unique_id(self) -> str:
        """Return the unique ID of the regulator."""
        return self._raw_regulator.id
        
    @property
    def name(self) -> str:
        """Return the name of the regulator."""
        return self._raw_regulator.device_description
        
    @property
    def device_info(self) -> dict[str, Any]:
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self._raw_regulator.id)},
            "name": self._raw_regulator.device_description,
            "model": self._raw_regulator.device_model,
            "sw_version": self._raw_regulator.parsed_properties["version_firmware"],
            "hw_version": self._raw_regulator.version,
            "manufacturer": "Giacomini",
        }
        
    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return self._raw_regulator.parsed_properties["temperature"]
        
    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement for temperature."""
        return TEMP_CELSIUS
        
    @property
    def target_temperature(self) -> float:
        """Return the target temperature."""
        return self._raw_regulator.parsed_properties["instruction_temperature_actual"]
    
    @property
    def current_humidity(self) -> float:
        """Return the current relative humidity."""
        return self._raw_regulator.parsed_properties["relative_humidity"]

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode."""
        if not self._raw_regulator.status:
            return HVACMode.OFF
        match self._raw_regulator.parsed_properties["mode_cold_hot_actual"]:
            case "heat":
                return HVACMode.HEAT
            case "cool":
                return HVACMode.COOL
        return HVACMode.OFF
        
    @property
    def preset_mode(self) -> str:
        """Return the current preset mode."""
        return self._raw_regulator.parsed_properties["mode_normal_eco_actual"]
        
    @property
    def preset_modes(self) -> list[str]:
        """Return the list of available preset modes."""
        return ["normal", "eco"]
        
    @property
    def fan_mode(self) -> str:
        """Return the current fan mode."""
        match self._raw_regulator.parsed_properties["speed_fan_ac"]:
            case "auto":
                return FAN_AUTO
            case "low":
                return FAN_LOW
            case "high":
                return FAN_HIGH
        return FAN_OFF
        
    @property
    def fan_modes(self) -> list[str]:
        """Return the list of available fan modes."""
        return [FAN_OFF, FAN_LOW, FAN_HIGH, FAN_AUTO]
        
    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return 10
        
    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return 40
        
    async def set_temperature(self, temperature: float) -> None:
        """Set new target temperature."""
        # Get the register and value to set
        register, value = self._raw_regulator.get_args_for_temperature(temperature)
        
        # Send command to device via API
        await self._api.async_set_register_value(
            self._raw_regulator.id, 
            register, 
            value
        )
        
        # Update the corresponding register and parsed properties
        self._raw_regulator.registers[register] = value
        self._raw_regulator._parsed_properties["instruction_temperature_actual"] = value
        
    async def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new HVAC mode."""
        # Get the register and value to set
        register, value = self._raw_regulator.get_args_for_operation(
            "heat" if hvac_mode == HVACMode.HEAT else "cool"
        )
        
        # Send command to device via API
        await self._api.async_set_register_value(
            self._raw_regulator.id, 
            register, 
            value
        )
        
        # Update the corresponding register and parsed properties
        self._raw_regulator.registers[register] = value
        self._raw_regulator._parsed_properties["mode_cold_hot_actual"] = "heat" if value else "cool"
        
    async def set_fan_mode(self, fan_mode: str) -> None:
        """Set new fan mode."""
        match fan_mode:
            case FAN_AUTO:
                speed = "auto"
            case FAN_LOW:
                speed = "low"
            case FAN_HIGH:
                speed = "high"
            case _:
                return
            
        # Get the register and value to set
        register, value = self._raw_regulator.get_args_for_fan_speed(speed)
        
        # Send command to device via API
        await self._api.async_set_register_value(
            self._raw_regulator.id, 
            register, 
            value
        )
        
        # Update the corresponding register and parsed properties
        self._raw_regulator.registers[register] = value
        self._raw_regulator._parsed_properties["speed_fan_ac"] = speed
        
    async def set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        # Get the register and value to set
        register, value = self._raw_regulator.get_args_for_normal_eco(preset_mode)
        
        # Send command to device via API
        await self._api.async_set_register_value(
            self._raw_regulator.id, 
            register, 
            value
        )
        
        # Update the corresponding register and parsed properties
        self._raw_regulator.registers[register] = value
        self._raw_regulator._parsed_properties["mode_normal_eco_actual"] = preset_mode

    async def turn_on(self) -> None:
        """Turn the device on."""
        # Get the register and value to set
        register, value = self._raw_regulator.get_args_for_on_off(True)
        
        # Send command to device via API
        await self._api.async_set_register_value(
            self._raw_regulator.id,
            register,
            value,
        )
        
        # Update the corresponding register and parsed properties
        self._raw_regulator.registers[register] = value
        self._raw_regulator._parsed_properties["status"] = True

    async def turn_off(self) -> None:
        """Turn the device off."""
        # Get the register and value to set
        register, value = self._raw_regulator.get_args_for_on_off(False)
        
        # Send command to device via API
        await self._api.async_set_register_value(
            self._raw_regulator.id,
            register,
            value,
        )
        
        # Update the corresponding register and parsed properties
        self._raw_regulator.registers[register] = value
        self._raw_regulator._parsed_properties["status"] = False

    async def async_update(self) -> None:
        """Update the regulator entity with latest data."""
        # Get the latest device data from the API
        device_data = await self._api.async_get_device(self._raw_regulator.id)
        
        # If we got valid data, update the raw regulator
        if device_data is not None:
            self._raw_regulator = RawRegulator.from_json(device_data)

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return (
            ClimateEntityFeature.TARGET_TEMPERATURE |
            ClimateEntityFeature.FAN_MODE |
            ClimateEntityFeature.PRESET_MODE |
            ClimateEntityFeature.TURN_OFF |
            ClimateEntityFeature.TURN_ON
        )
    