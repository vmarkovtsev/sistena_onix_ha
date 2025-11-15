"""
Sistena Onix Device Class.

This module defines the Device class for interacting with Sistena Onix devices.
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any


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
                "no", "en frío", "en calor", "en frío y calor"
            ][(registers[2] & 0xFF00) >> 8]
        except IndexError:
            _parsed_properties["config_suelo_radiante"] = "error"
        # register 2 lower byte
        try:
            _parsed_properties["config_fan-coil"] = [
                "no", "en frío", "en calor", "en frío y calor"
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
        _parsed_properties["mode_operation"] = "calor" if registers[5] else "frío" 
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
        _parsed_properties["mode_fan"] = "continuo" if registers[16] == 0 else "auto"
        # register 17
        try:
            _parsed_properties["speed_fan_ac"] = [
                "automática", "baja", "alta"
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
                "no", "frío", "calor", "frío y calor"
            ][registers[21]]
        except IndexError:
            _parsed_properties["mode_dryer"] = "error"
        # register 22 upper byte
        _parsed_properties["instruction_dryer"] = (registers[22] & 0xFF00) >> 8
        # register 22 lower byte
        _parsed_properties["histeresis_dryer"] = registers[22] & 0x00FF
        # register 23
        _parsed_properties["valve_suelo_radiante"] = "deshabilitada" if registers[23] else "habilitada"
        # register 24
        _parsed_properties["offset_temperature"] = registers[24] / 10.0
        # register 25
        _parsed_properties["offset_humedad"] = registers[25] / 10.0
        # register 26
        _parsed_properties["temperature"] = registers[26] / 10.0
        # register 27
        _parsed_properties["relative_humidity"] = registers[27] / 10.0
        # register 28
        _parsed_properties["mode_cold_hot_actual"] = "calor" if registers[28] else "frío"
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
    