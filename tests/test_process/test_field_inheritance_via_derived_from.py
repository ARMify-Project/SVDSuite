from typing import Callable
import pytest

from svdsuite.process import ProcessException
from svdsuite.model.process import Device, Register
from svdsuite.model.types import (
    AccessType,
    EnumUsageType,
    ModifiedWriteValuesType,
    ReadActionType,
)


def test_simple_inheritance_backward_reference_same_scope(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "field_inheritance_via_derivedfrom/simple_inheritance_backward_reference_same_scope.svd"
    )

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


def test_simple_inheritance_forward_reference_same_scope(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "field_inheritance_via_derivedfrom/simple_inheritance_forward_reference_same_scope.svd"
    )

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


def test_simple_inheritance_backward_reference_different_scope(
    get_processed_device_from_testfile: Callable[[str], Device]
):
    device = get_processed_device_from_testfile(
        "field_inheritance_via_derivedfrom/simple_inheritance_backward_reference_different_scope.svd"
    )

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1
    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 0
    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    rega_enum_container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]
    assert rega_enum_container.name == "FieldAEnumeratedValue"
    assert rega_enum_container.usage == EnumUsageType.READ_WRITE
    assert len(rega_enum_container.enumerated_values) == 2
    assert rega_enum_container.enumerated_values[0].name == "0b0"
    assert rega_enum_container.enumerated_values[0].description == "Description for 0b0"
    assert rega_enum_container.enumerated_values[0].value == 0b0
    assert rega_enum_container.enumerated_values[0].is_default is False
    assert rega_enum_container.enumerated_values[1].name == "0b1"
    assert rega_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert rega_enum_container.enumerated_values[1].value == 0b1
    assert rega_enum_container.enumerated_values[1].is_default is False

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert len(device.peripherals[0].registers_clusters[1].fields) == 1
    assert device.peripherals[0].registers_clusters[1].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[1].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[1].fields[0].msb == 0
    assert len(device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers) == 1
    regb_enum_container = device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers[0]
    assert regb_enum_container.name == "FieldAEnumeratedValue"
    assert regb_enum_container.usage == EnumUsageType.READ_WRITE
    assert len(regb_enum_container.enumerated_values) == 2
    assert regb_enum_container.enumerated_values[0].name == "0b0"
    assert regb_enum_container.enumerated_values[0].description == "Description for 0b0"
    assert regb_enum_container.enumerated_values[0].value == 0b0
    assert regb_enum_container.enumerated_values[0].is_default is False
    assert regb_enum_container.enumerated_values[1].name == "0b1"
    assert regb_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert regb_enum_container.enumerated_values[1].value == 0b1
    assert regb_enum_container.enumerated_values[1].is_default is False


def test_simple_inheritance_forward_reference_different_scope(
    get_processed_device_from_testfile: Callable[[str], Device]
):
    device = get_processed_device_from_testfile(
        "field_inheritance_via_derivedfrom/simple_inheritance_forward_reference_different_scope.svd"
    )

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1
    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 0
    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    rega_enum_container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]
    assert rega_enum_container.name == "FieldAEnumeratedValue"
    assert rega_enum_container.usage == EnumUsageType.READ_WRITE
    assert len(rega_enum_container.enumerated_values) == 2
    assert rega_enum_container.enumerated_values[0].name == "0b0"
    assert rega_enum_container.enumerated_values[0].description == "Description for 0b0"
    assert rega_enum_container.enumerated_values[0].value == 0b0
    assert rega_enum_container.enumerated_values[0].is_default is False
    assert rega_enum_container.enumerated_values[1].name == "0b1"
    assert rega_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert rega_enum_container.enumerated_values[1].value == 0b1
    assert rega_enum_container.enumerated_values[1].is_default is False

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert len(device.peripherals[0].registers_clusters[1].fields) == 1
    assert device.peripherals[0].registers_clusters[1].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[1].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[1].fields[0].msb == 0
    assert len(device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers) == 1
    regb_enum_container = device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers[0]
    assert regb_enum_container.name == "FieldAEnumeratedValue"
    assert regb_enum_container.usage == EnumUsageType.READ_WRITE
    assert len(regb_enum_container.enumerated_values) == 2
    assert regb_enum_container.enumerated_values[0].name == "0b0"
    assert regb_enum_container.enumerated_values[0].description == "Description for 0b0"
    assert regb_enum_container.enumerated_values[0].value == 0b0
    assert regb_enum_container.enumerated_values[0].is_default is False
    assert regb_enum_container.enumerated_values[1].name == "0b1"
    assert regb_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert regb_enum_container.enumerated_values[1].value == 0b1
    assert regb_enum_container.enumerated_values[1].is_default is False


def test_value_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("field_inheritance_via_derivedfrom/value_inheritance.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].fields) == 2

    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].description == "FieldA description"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].access == AccessType.READ_WRITE
    assert (
        device.peripherals[0].registers_clusters[0].fields[0].modified_write_values
        == ModifiedWriteValuesType.ONE_TO_CLEAR
    )
    assert device.peripherals[0].registers_clusters[0].fields[0].write_constraint is not None
    assert device.peripherals[0].registers_clusters[0].fields[0].write_constraint.write_as_read is True
    assert device.peripherals[0].registers_clusters[0].fields[0].read_action == ReadActionType.MODIFY
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
    assert device.peripherals[0].registers_clusters[0].fields[1].description == "FieldA description"
    assert device.peripherals[0].registers_clusters[0].fields[1].lsb == 1
    assert device.peripherals[0].registers_clusters[0].fields[1].msb == 1
    assert device.peripherals[0].registers_clusters[0].fields[1].access == AccessType.READ_WRITE
    assert (
        device.peripherals[0].registers_clusters[0].fields[1].modified_write_values
        == ModifiedWriteValuesType.ONE_TO_CLEAR
    )
    assert device.peripherals[0].registers_clusters[0].fields[1].write_constraint is not None
    assert device.peripherals[0].registers_clusters[0].fields[1].write_constraint.write_as_read is True
    assert device.peripherals[0].registers_clusters[0].fields[1].read_action == ReadActionType.MODIFY
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


def test_override_behavior(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("field_inheritance_via_derivedfrom/override_behavior.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].fields) == 2

    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].description == "FieldA description"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].access == AccessType.READ_WRITE
    assert (
        device.peripherals[0].registers_clusters[0].fields[0].modified_write_values
        == ModifiedWriteValuesType.ONE_TO_CLEAR
    )
    assert device.peripherals[0].registers_clusters[0].fields[0].write_constraint is not None
    assert device.peripherals[0].registers_clusters[0].fields[0].write_constraint.write_as_read is True
    assert device.peripherals[0].registers_clusters[0].fields[0].read_action == ReadActionType.MODIFY
    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    fielda_enum_container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]
    assert fielda_enum_container.name == "FieldAEnumeratedValue"
    assert fielda_enum_container.usage == EnumUsageType.READ
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
    assert device.peripherals[0].registers_clusters[0].fields[1].description == "FieldB description"
    assert device.peripherals[0].registers_clusters[0].fields[1].lsb == 1
    assert device.peripherals[0].registers_clusters[0].fields[1].msb == 1
    assert device.peripherals[0].registers_clusters[0].fields[1].access == AccessType.READ_ONLY
    assert (
        device.peripherals[0].registers_clusters[0].fields[1].modified_write_values
        == ModifiedWriteValuesType.ONE_TO_SET
    )
    assert device.peripherals[0].registers_clusters[0].fields[1].write_constraint is not None
    assert device.peripherals[0].registers_clusters[0].fields[1].write_constraint.use_enumerated_values is True
    assert device.peripherals[0].registers_clusters[0].fields[1].read_action == ReadActionType.CLEAR
    assert len(device.peripherals[0].registers_clusters[0].fields[1].enumerated_value_containers) == 2

    fieldb_enum_container1 = device.peripherals[0].registers_clusters[0].fields[1].enumerated_value_containers[0]
    assert fieldb_enum_container1.name == "FieldAEnumeratedValue"
    assert fieldb_enum_container1.usage == EnumUsageType.READ
    assert len(fieldb_enum_container1.enumerated_values) == 2
    assert fieldb_enum_container1.enumerated_values[0].name == "0b0"
    assert fieldb_enum_container1.enumerated_values[0].description == "Description for 0b0"
    assert fieldb_enum_container1.enumerated_values[0].value == 0b0
    assert fieldb_enum_container1.enumerated_values[0].is_default is False
    assert fieldb_enum_container1.enumerated_values[1].name == "0b1"
    assert fieldb_enum_container1.enumerated_values[1].description == "Description for 0b1"
    assert fieldb_enum_container1.enumerated_values[1].value == 0b1
    assert fieldb_enum_container1.enumerated_values[1].is_default is False

    fieldb_enum_container2 = device.peripherals[0].registers_clusters[0].fields[1].enumerated_value_containers[1]
    assert fieldb_enum_container2.name == "FieldBEnumeratedValue"
    assert fieldb_enum_container2.usage == EnumUsageType.WRITE
    assert len(fieldb_enum_container2.enumerated_values) == 2
    assert fieldb_enum_container2.enumerated_values[0].name == "0b0"
    assert fieldb_enum_container2.enumerated_values[0].description == "Description for 0b0"
    assert fieldb_enum_container2.enumerated_values[0].value == 0b0
    assert fieldb_enum_container2.enumerated_values[0].is_default is False
    assert fieldb_enum_container2.enumerated_values[1].name == "0b1"
    assert fieldb_enum_container2.enumerated_values[1].description == "Description for 0b1"
    assert fieldb_enum_container2.enumerated_values[1].value == 0b1
    assert fieldb_enum_container2.enumerated_values[1].is_default is False


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Field 'FieldB' (<enumeratedValues> 'FieldAEnumeratedValue'): 'read-write' container already defined",
)
def test_enumerated_value_inheritance_error(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("field_inheritance_via_derivedfrom/enumerated_value_inheritance_error.svd")


def test_multiple_inheritance_backward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "field_inheritance_via_derivedfrom/multiple_inheritance_backward_reference.svd"
    )

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].fields) == 3

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

    assert device.peripherals[0].registers_clusters[0].fields[2].name == "FieldC"
    assert device.peripherals[0].registers_clusters[0].fields[2].lsb == 2
    assert device.peripherals[0].registers_clusters[0].fields[2].msb == 2
    assert len(device.peripherals[0].registers_clusters[0].fields[2].enumerated_value_containers) == 1
    fieldc_enum_container = device.peripherals[0].registers_clusters[0].fields[2].enumerated_value_containers[0]
    assert fieldc_enum_container.name == "FieldAEnumeratedValue"
    assert fieldc_enum_container.usage == EnumUsageType.READ_WRITE
    assert len(fieldc_enum_container.enumerated_values) == 2
    assert fieldc_enum_container.enumerated_values[0].name == "0b0"
    assert fieldc_enum_container.enumerated_values[0].description == "Description for 0b0"
    assert fieldc_enum_container.enumerated_values[0].value == 0b0
    assert fieldc_enum_container.enumerated_values[0].is_default is False
    assert fieldc_enum_container.enumerated_values[1].name == "0b1"
    assert fieldc_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fieldc_enum_container.enumerated_values[1].value == 0b1
    assert fieldc_enum_container.enumerated_values[1].is_default is False


def test_multiple_inheritance_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "field_inheritance_via_derivedfrom/multiple_inheritance_forward_reference.svd"
    )

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].fields) == 3

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

    assert device.peripherals[0].registers_clusters[0].fields[2].name == "FieldC"
    assert device.peripherals[0].registers_clusters[0].fields[2].lsb == 2
    assert device.peripherals[0].registers_clusters[0].fields[2].msb == 2
    assert len(device.peripherals[0].registers_clusters[0].fields[2].enumerated_value_containers) == 1
    fieldc_enum_container = device.peripherals[0].registers_clusters[0].fields[2].enumerated_value_containers[0]
    assert fieldc_enum_container.name == "FieldAEnumeratedValue"
    assert fieldc_enum_container.usage == EnumUsageType.READ_WRITE
    assert len(fieldc_enum_container.enumerated_values) == 2
    assert fieldc_enum_container.enumerated_values[0].name == "0b0"
    assert fieldc_enum_container.enumerated_values[0].description == "Description for 0b0"
    assert fieldc_enum_container.enumerated_values[0].value == 0b0
    assert fieldc_enum_container.enumerated_values[0].is_default is False
    assert fieldc_enum_container.enumerated_values[1].name == "0b1"
    assert fieldc_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fieldc_enum_container.enumerated_values[1].value == 0b1
    assert fieldc_enum_container.enumerated_values[1].is_default is False


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="Circular inheritance is not supported")
def test_circular_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("field_inheritance_via_derivedfrom/circular_inheritance.svd")


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="FieldA overlaps with FieldB")
def test_same_bit_range(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("field_inheritance_via_derivedfrom/same_bit_range.svd")


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="FieldA overlaps with FieldB")
def test_overlap_bit_range(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("field_inheritance_via_derivedfrom/overlap_bit_range.svd")


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="Can't derive from self")
def test_derive_from_self(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("field_inheritance_via_derivedfrom/derive_from_self.svd")
