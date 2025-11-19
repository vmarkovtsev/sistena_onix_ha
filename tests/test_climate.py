"""Tests for Sistena Onix climate integration."""

import pytest
from unittest.mock import Mock, patch

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

from custom_components.sistena.climate import (
    RawRegulator,
    Regulator,
    SistenaSensor,
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
                "26": 250,  # temperature * 10 = 25.0
                "27": 500,  # humidity * 10 = 50.0
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
    """Test SistenaSensor base class."""
    # Create mock regulator
    mock_regulator = Mock()
    mock_regulator.unique_id = "test_device_id"
    mock_regulator._raw_regulator.parsed_properties = {"test_key": "test_value"}

    # Create SistenaSensor
    sensor = SistenaSensor(
        mock_regulator,
        "Test Sensor",
        "test_key",
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        UnitOfTemperature.CELSIUS,
    )

    # Check properties
    assert sensor.unique_id == "test_device_id_test_key"
    assert sensor.name == "Test Sensor"
    assert sensor.device_class == SensorDeviceClass.TEMPERATURE
    assert sensor.state_class == SensorStateClass.MEASUREMENT
    assert sensor.native_unit_of_measurement == UnitOfTemperature.CELSIUS
    assert sensor.native_value == "test_value"


def test_temperature_sensor():
    """Test TemperatureSensor class."""
    # Create mock regulator
    mock_regulator = Mock()
    mock_regulator.unique_id = "test_device_id"
    mock_regulator._raw_regulator.parsed_properties = {"temperature": 25.0}

    # Create TemperatureSensor
    sensor = TemperatureSensor(mock_regulator)

    # Check properties
    assert sensor.unique_id == "test_device_id_temperature"
    assert sensor.name == "Temperature"
    assert sensor.device_class == SensorDeviceClass.TEMPERATURE
    assert sensor.state_class == SensorStateClass.MEASUREMENT
    assert sensor.native_unit_of_measurement == UnitOfTemperature.CELSIUS
    assert sensor.native_value == 25.0


def test_humidity_sensor():
    """Test HumiditySensor class."""
    # Create mock regulator
    mock_regulator = Mock()
    mock_regulator.unique_id = "test_device_id"
    mock_regulator._raw_regulator.parsed_properties = {"relative_humidity": 50.0}

    # Create HumiditySensor
    sensor = HumiditySensor(mock_regulator)

    # Check properties
    assert sensor.unique_id == "test_device_id_relative_humidity"
    assert sensor.name == "Humidity"
    assert sensor.device_class == SensorDeviceClass.HUMIDITY
    assert sensor.state_class == SensorStateClass.MEASUREMENT
    assert sensor.native_unit_of_measurement == "%"
    assert sensor.native_value == 50.0
