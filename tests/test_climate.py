"""Tests for Sistena Onix climate integration."""

from unittest.mock import Mock, patch

from homeassistant.const import UnitOfTemperature
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

from custom_components.sistena.climate import (
    RawRegulator,
    Regulator,
)
from custom_components.sistena.sensor import (
    TemperatureSensor,
    HumiditySensor,
)


def test_raw_regulator_creation():
    """Test RawRegulator creation from JSON data."""
    # Sample JSON data similar to what would come from the API
    json_data = {
        "device": {
            "_id": "test_device_id",
            "MAC": "00:11:22:33:44:55",
            "status": "online",
            "fwName": "test_fw",
            "version": "1.0.0",
            "dBm": "-50",
            "ipPublic": "192.168.1.100",
            "lastboot": "2023-01-01T00:00:00Z",
            "dateOfRegister": 1672531200000,  # Jan 1, 2023
            "model": {
                "model": "test_model",
                "deviceDescription": "Test Device",
                "icon": "test_icon",
            },
            "registers": {
                "0": 123,
                "1": 456,
                "2": 789,
                "3": 1,  # status
                "4": 0,  # selection_of_operation
                "5": 1,  # mode_operation (heat)
                "6": 0,  # contact_operation
                "7": 0,  # selection_normal_eco (teclado)
                "8": 0,  # mode_normal_eco (normal)
                "9": 0,  # contact_normal_eco
                "10": 250,  # instruction_temperature_cold_normal
                "11": 240,  # instruction_temperature_cold_eco
                "12": 260,  # instruction_temperature_hot_normal
                "13": 255,  # instruction_temperature_hot_eco
                "14": 140,  # histeresis_stage_suelo_radiante
                "15": 150,  # histeresis_stage_fan-coil_cold/hot
                "16": 0,  # mode_fan (continuous)
                "17": 0,  # speed_fan_ac (auto)
                "18": 180,  # difference_speeds/histeresis_speeds
                "19": 190,  # proportional_band_fan_ec
                "20": 200,  # speed_min/max
                "21": 210,  # mode_dryer
                "22": 220,  # instruction_dryer/histeresis_dryer
                "23": 230,  # valve_suelo_radiante
                "24": 240,  # offset_temperature
                "25": 250,  # offset_humidity
                "26": 250,  # temperature * 10 = 25.0
                "27": 500,  # humidity * 10 = 50.0
                "28": 1,  # mode_cold_hot_actual (heat)
                "29": 0,  # mode_normal_eco_actual (normal)
                "30": 230,  # instruction_temperature_actual
                "31": 310,  # state_valve_suelo_radiante
                "32": 320,  # state_valve_fan-coil
                "33": 330,  # fan_ac_state/fan_ec_speed
                "34": 340,  # state_dryer
                "35": 12,  # firmware version 1.2
            },
        }
    }

    # Create RawRegulator instance
    raw_regulator = RawRegulator.from_json(json_data)

    # Check basic properties
    assert raw_regulator.id == "test_device_id"
    assert raw_regulator.mac == "00:11:22:33:44:55"
    assert raw_regulator.device_model == "test_model"

    # Check parsed properties
    assert raw_regulator.parsed_properties["temperature"] == 25.0
    assert raw_regulator.parsed_properties["relative_humidity"] == 50.0
    assert raw_regulator.parsed_properties["version_firmware"] == "1.2"


def test_regulator_entity():
    """Test Regulator entity creation and properties."""
    # Create mock API
    api = Mock()

    # Create RawRegulator
    raw_regulator = RawRegulator(
        id="test_device_id",
        mac="00:11:22:33:44:55",
        status="online",
        fw_name="test_fw",
        version="1.0.0",
        dbm="-50",
        ip_public="192.168.1.100",
        lastboot="2023-01-01T00:00:00Z",
        date_of_register=Mock(),
        device_model="test_model",
        device_description="Test Device",
        icon="test_icon",
        registers=[0] * 100,
    )

    # Set up some parsed properties for testing
    raw_regulator._parsed_properties = {
        "temperature": 25.0,
        "relative_humidity": 50.0,
        "instruction_temperature_actual": 22.0,
        "mode_cold_hot_actual": "heat",
        "mode_normal_eco_actual": "normal",
        "speed_fan_ac": "auto",
        "version_firmware": "1.2",
    }

    # Create Regulator entity
    regulator = Regulator(raw_regulator, api, "Test Name")

    # Check basic properties
    assert regulator.unique_id == "test_device_id"
    assert regulator.name == "Test Name"
    assert regulator.current_temperature == 25.0
    assert regulator.target_temperature == 22.0
    assert regulator.current_humidity == 50.0
    assert regulator.temperature_unit == UnitOfTemperature.CELSIUS


def test_sensor_entity():
    """Test SistenaSensor base class - this is a base class and should not be instantiated directly."""
    # The SistenaSensor is a base class that should be extended by specific sensor classes
    # We'll test the specific sensor classes instead
    pass


def test_temperature_sensor():
    """Test TemperatureSensor class."""
    # Create mock regulator
    mock_regulator = Mock()
    mock_regulator.unique_id = "test_device_id"
    mock_regulator.name = "Test Name"
    mock_regulator.device_info = {
        "identifiers": {("sistena", "test_device_id")},
        "name": "Test Name",
        "model": "test_model",
        "sw_version": "1.2",
        "hw_version": "1.0.0",
        "manufacturer": "Giacomini",
    }
    mock_regulator.current_temperature = 25.0

    # Create TemperatureSensor
    sensor = TemperatureSensor(mock_regulator)

    # Check properties
    assert sensor.unique_id == "test_device_id_temperature"
    # The name is generated as "{regulator.name}_Temperature" where regulator.name is "Test Name"
    assert sensor.name == "Test Name_Temperature"
    assert sensor.device_class == SensorDeviceClass.TEMPERATURE
    assert sensor.state_class == SensorStateClass.MEASUREMENT
    assert sensor.native_unit_of_measurement == UnitOfTemperature.CELSIUS
    assert sensor.native_value == 25.0


def test_humidity_sensor():
    """Test HumiditySensor class."""
    # Create mock regulator
    mock_regulator = Mock()
    mock_regulator.unique_id = "test_device_id"
    mock_regulator.name = "Test Name"
    mock_regulator.device_info = {
        "identifiers": {("sistena", "test_device_id")},
        "name": "Test Name",
        "model": "test_model",
        "sw_version": "1.2",
        "hw_version": "1.0.0",
        "manufacturer": "Giacomini",
    }
    mock_regulator.current_humidity = 50.0

    # Create HumiditySensor
    sensor = HumiditySensor(mock_regulator)

    # Check properties
    assert sensor.unique_id == "test_device_id_humidity"
    assert sensor.name == "Test Name_Humidity"
    assert sensor.device_class == SensorDeviceClass.HUMIDITY
    assert sensor.state_class == SensorStateClass.MEASUREMENT
    assert sensor.native_unit_of_measurement == "%"
    assert sensor.native_value == 50.0
