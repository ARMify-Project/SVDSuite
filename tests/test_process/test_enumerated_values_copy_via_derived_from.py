from typing import Callable
import pytest

from svdsuite.process import ProcessException
from svdsuite.model.process import Device, Register
from svdsuite.model.types import EnumUsageType


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="Two containers require usage types read and write")
def test_backward_reference_same_scope(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("enum_copy_via_derivedfrom/backward_reference_same_scope.svd")


def test_backward_reference_different_scope(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("enum_copy_via_derivedfrom/backward_reference_different_scope.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].fields) == 2

    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 0
    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    fielda_enum_container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]
    assert fielda_enum_container.name == "FieldAEnumeratedValue"
    assert fielda_enum_container.usage == EnumUsageType.READ_WRITE
    assert len(fielda_enum_container.enumerated_values) == 2
    assert fielda_enum_container.enumerated_values[0].name == "0b0"
    assert fielda_enum_container.enumerated_values[0].description == "Description for 0b0"
    assert fielda_enum_container.enumerated_values[0].value == 0b0
    assert fielda_enum_container.enumerated_values[0].is_default is False
    assert fielda_enum_container.enumerated_values[1].name == "0b1"
    assert fielda_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fielda_enum_container.enumerated_values[1].value == 0b1
    assert fielda_enum_container.enumerated_values[1].is_default is False

    assert device.peripherals[0].registers_clusters[0].fields[1].name == "FieldB"
    assert device.peripherals[0].registers_clusters[0].fields[1].lsb == 1
    assert device.peripherals[0].registers_clusters[0].fields[1].msb == 1
    assert len(device.peripherals[0].registers_clusters[0].fields[1].enumerated_value_containers) == 1
    fieldb_enum_container = device.peripherals[0].registers_clusters[0].fields[1].enumerated_value_containers[0]
    assert fieldb_enum_container.name == "FieldAEnumeratedValue"
    assert fieldb_enum_container.usage == EnumUsageType.READ_WRITE
    assert len(fieldb_enum_container.enumerated_values) == 2
    assert fieldb_enum_container.enumerated_values[0].name == "0b0"
    assert fieldb_enum_container.enumerated_values[0].description == "Description for 0b0"
    assert fieldb_enum_container.enumerated_values[0].value == 0b0
    assert fieldb_enum_container.enumerated_values[0].is_default is False
    assert fieldb_enum_container.enumerated_values[1].name == "0b1"
    assert fieldb_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fieldb_enum_container.enumerated_values[1].value == 0b1
    assert fieldb_enum_container.enumerated_values[1].is_default is False


def test_forward_reference_different_scope(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("enum_copy_via_derivedfrom/forward_reference_different_scope.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].fields) == 2

    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 0
    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    fielda_enum_container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]
    assert fielda_enum_container.name == "FieldAEnumeratedValue"
    assert fielda_enum_container.usage == EnumUsageType.READ_WRITE
    assert len(fielda_enum_container.enumerated_values) == 2
    assert fielda_enum_container.enumerated_values[0].name == "0b0"
    assert fielda_enum_container.enumerated_values[0].description == "Description for 0b0"
    assert fielda_enum_container.enumerated_values[0].value == 0b0
    assert fielda_enum_container.enumerated_values[0].is_default is False
    assert fielda_enum_container.enumerated_values[1].name == "0b1"
    assert fielda_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fielda_enum_container.enumerated_values[1].value == 0b1
    assert fielda_enum_container.enumerated_values[1].is_default is False

    assert device.peripherals[0].registers_clusters[0].fields[1].name == "FieldB"
    assert device.peripherals[0].registers_clusters[0].fields[1].lsb == 1
    assert device.peripherals[0].registers_clusters[0].fields[1].msb == 1
    assert len(device.peripherals[0].registers_clusters[0].fields[1].enumerated_value_containers) == 1
    fieldb_enum_container = device.peripherals[0].registers_clusters[0].fields[1].enumerated_value_containers[0]
    assert fieldb_enum_container.name == "FieldAEnumeratedValue"
    assert fieldb_enum_container.usage == EnumUsageType.READ_WRITE
    assert len(fieldb_enum_container.enumerated_values) == 2
    assert fieldb_enum_container.enumerated_values[0].name == "0b0"
    assert fieldb_enum_container.enumerated_values[0].description == "Description for 0b0"
    assert fieldb_enum_container.enumerated_values[0].value == 0b0
    assert fieldb_enum_container.enumerated_values[0].is_default is False
    assert fieldb_enum_container.enumerated_values[1].name == "0b1"
    assert fieldb_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fieldb_enum_container.enumerated_values[1].value == 0b1
    assert fieldb_enum_container.enumerated_values[1].is_default is False
