from typing import Callable
import pytest

from svdsuite.process import ProcessException, ProcessWarning
from svdsuite.model.process import Device, Register
from svdsuite.model.types import (
    AccessType,
    ProtectionStringType,
    DataTypeType,
    ModifiedWriteValuesType,
    ReadActionType,
)


def test_simple_inheritance_backward_reference_same_scope(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "register_inheritance_via_derivedfrom/simple_inheritance_backward_reference_same_scope.svd"
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
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 2

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert len(device.peripherals[0].registers_clusters[1].fields) == 1
    assert device.peripherals[0].registers_clusters[1].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[1].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[1].fields[0].msb == 2


def test_simple_inheritance_forward_reference_same_scope(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "register_inheritance_via_derivedfrom/simple_inheritance_forward_reference_same_scope.svd"
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
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 2

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert len(device.peripherals[0].registers_clusters[1].fields) == 1
    assert device.peripherals[0].registers_clusters[1].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[1].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[1].fields[0].msb == 2


def test_simple_inheritance_backward_reference_different_scope(
    get_processed_device_from_testfile: Callable[[str], Device]
):
    device = get_processed_device_from_testfile(
        "register_inheritance_via_derivedfrom/simple_inheritance_backward_reference_different_scope.svd"
    )

    assert len(device.peripherals) == 2

    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1
    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 2

    assert len(device.peripherals[1].registers_clusters) == 1
    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[0].size == 32
    assert len(device.peripherals[1].registers_clusters[0].fields) == 1
    assert device.peripherals[1].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[1].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[1].registers_clusters[0].fields[0].msb == 2


def test_simple_inheritance_forward_reference_different_scope(
    get_processed_device_from_testfile: Callable[[str], Device]
):
    device = get_processed_device_from_testfile(
        "register_inheritance_via_derivedfrom/simple_inheritance_forward_reference_different_scope.svd"
    )

    assert len(device.peripherals) == 2

    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1
    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 2

    assert len(device.peripherals[1].registers_clusters) == 1
    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[0].size == 32
    assert len(device.peripherals[1].registers_clusters[0].fields) == 1
    assert device.peripherals[1].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[1].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[1].registers_clusters[0].fields[0].msb == 2


def test_value_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("register_inheritance_via_derivedfrom/value_inheritance.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].display_name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].description == "RegisterA description"
    assert device.peripherals[0].registers_clusters[0].alternate_register == "RegisterC"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 16
    assert device.peripherals[0].registers_clusters[0].access == AccessType.READ_ONLY
    assert device.peripherals[0].registers_clusters[0].protection == ProtectionStringType.SECURE
    assert device.peripherals[0].registers_clusters[0].reset_value == 0xDEAD
    assert device.peripherals[0].registers_clusters[0].reset_mask == 0xC0DE
    assert device.peripherals[0].registers_clusters[0].data_type == DataTypeType.UINT32_T
    assert device.peripherals[0].registers_clusters[0].modified_write_values == ModifiedWriteValuesType.ONE_TO_CLEAR
    assert device.peripherals[0].registers_clusters[0].write_constraint is not None
    assert device.peripherals[0].registers_clusters[0].write_constraint.write_as_read is True
    assert device.peripherals[0].registers_clusters[0].read_action == ReadActionType.MODIFY
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1
    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 2
    assert device.peripherals[0].registers_clusters[0].fields[0].access == AccessType.READ_ONLY
    assert device.peripherals[0].registers_clusters[0].fields[0].write_constraint is not None
    assert device.peripherals[0].registers_clusters[0].fields[0].write_constraint.write_as_read is True

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].display_name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].description == "RegisterA description"
    assert device.peripherals[0].registers_clusters[1].alternate_register == "RegisterC"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x2
    assert device.peripherals[0].registers_clusters[1].size == 16
    assert device.peripherals[0].registers_clusters[1].access == AccessType.READ_ONLY
    assert device.peripherals[0].registers_clusters[1].protection == ProtectionStringType.SECURE
    assert device.peripherals[0].registers_clusters[1].reset_value == 0xDEAD
    assert device.peripherals[0].registers_clusters[1].reset_mask == 0xC0DE
    assert device.peripherals[0].registers_clusters[1].data_type == DataTypeType.UINT32_T
    assert device.peripherals[0].registers_clusters[1].modified_write_values == ModifiedWriteValuesType.ONE_TO_CLEAR
    assert device.peripherals[0].registers_clusters[1].write_constraint is not None
    assert device.peripherals[0].registers_clusters[1].write_constraint.write_as_read is True
    assert device.peripherals[0].registers_clusters[1].read_action == ReadActionType.MODIFY
    assert len(device.peripherals[0].registers_clusters[1].fields) == 1
    assert device.peripherals[0].registers_clusters[1].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[1].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[1].fields[0].msb == 2
    assert device.peripherals[0].registers_clusters[1].fields[0].access == AccessType.READ_ONLY
    assert device.peripherals[0].registers_clusters[1].fields[0].write_constraint is not None
    assert device.peripherals[0].registers_clusters[1].fields[0].write_constraint.write_as_read is True


def test_override_behavior(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("register_inheritance_via_derivedfrom/override_behavior.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].display_name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].description == "RegisterA description"
    assert device.peripherals[0].registers_clusters[0].alternate_register == "RegisterC"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 16
    assert device.peripherals[0].registers_clusters[0].access == AccessType.READ_ONLY
    assert device.peripherals[0].registers_clusters[0].protection == ProtectionStringType.SECURE
    assert device.peripherals[0].registers_clusters[0].reset_value == 0xDEAD
    assert device.peripherals[0].registers_clusters[0].reset_mask == 0xC0DE
    assert device.peripherals[0].registers_clusters[0].data_type == DataTypeType.UINT32_T
    assert device.peripherals[0].registers_clusters[0].modified_write_values == ModifiedWriteValuesType.ONE_TO_CLEAR
    assert device.peripherals[0].registers_clusters[0].write_constraint is not None
    assert device.peripherals[0].registers_clusters[0].write_constraint.write_as_read is True
    assert device.peripherals[0].registers_clusters[0].read_action == ReadActionType.MODIFY
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1
    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 2
    assert device.peripherals[0].registers_clusters[0].fields[0].access == AccessType.READ_ONLY
    assert device.peripherals[0].registers_clusters[0].fields[0].write_constraint is not None
    assert device.peripherals[0].registers_clusters[0].fields[0].write_constraint.write_as_read is True

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].display_name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].description == "RegisterB description"
    assert device.peripherals[0].registers_clusters[1].alternate_register == "RegisterD"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x2
    assert device.peripherals[0].registers_clusters[1].size == 8
    assert device.peripherals[0].registers_clusters[1].access == AccessType.WRITE_ONLY
    assert device.peripherals[0].registers_clusters[1].protection == ProtectionStringType.NON_SECURE
    assert device.peripherals[0].registers_clusters[1].reset_value == 0xAB
    assert device.peripherals[0].registers_clusters[1].reset_mask == 0xDE
    assert device.peripherals[0].registers_clusters[1].data_type == DataTypeType.UINT8_T
    assert device.peripherals[0].registers_clusters[1].modified_write_values == ModifiedWriteValuesType.ONE_TO_SET
    assert device.peripherals[0].registers_clusters[1].write_constraint is not None
    assert device.peripherals[0].registers_clusters[1].write_constraint.use_enumerated_values is True
    assert device.peripherals[0].registers_clusters[1].read_action == ReadActionType.SET
    assert len(device.peripherals[0].registers_clusters[1].fields) == 2
    assert device.peripherals[0].registers_clusters[1].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[1].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[1].fields[0].msb == 2
    assert device.peripherals[0].registers_clusters[1].fields[0].access == AccessType.WRITE_ONLY
    assert device.peripherals[0].registers_clusters[1].fields[0].write_constraint is not None
    assert device.peripherals[0].registers_clusters[1].fields[0].write_constraint.use_enumerated_values is True
    assert device.peripherals[0].registers_clusters[1].fields[1].name == "FieldB"
    assert device.peripherals[0].registers_clusters[1].fields[1].lsb == 3
    assert device.peripherals[0].registers_clusters[1].fields[1].msb == 4
    assert device.peripherals[0].registers_clusters[1].fields[1].access == AccessType.WRITE_ONLY
    assert device.peripherals[0].registers_clusters[1].fields[1].write_constraint is not None
    assert device.peripherals[0].registers_clusters[1].fields[1].write_constraint.use_enumerated_values is True


def test_multiple_inheritance_backward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "register_inheritance_via_derivedfrom/multiple_inheritance_backward_reference.svd"
    )

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 3

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1
    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 2

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert len(device.peripherals[0].registers_clusters[1].fields) == 1
    assert device.peripherals[0].registers_clusters[1].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[1].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[1].fields[0].msb == 2

    assert isinstance(device.peripherals[0].registers_clusters[2], Register)
    assert device.peripherals[0].registers_clusters[2].name == "RegisterC"
    assert device.peripherals[0].registers_clusters[2].address_offset == 0x8
    assert device.peripherals[0].registers_clusters[2].size == 32
    assert len(device.peripherals[0].registers_clusters[2].fields) == 1
    assert device.peripherals[0].registers_clusters[2].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[2].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[2].fields[0].msb == 2


def test_multiple_inheritance_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "register_inheritance_via_derivedfrom/multiple_inheritance_forward_reference.svd"
    )

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 3

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1
    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 2

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert len(device.peripherals[0].registers_clusters[1].fields) == 1
    assert device.peripherals[0].registers_clusters[1].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[1].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[1].fields[0].msb == 2

    assert isinstance(device.peripherals[0].registers_clusters[2], Register)
    assert device.peripherals[0].registers_clusters[2].name == "RegisterC"
    assert device.peripherals[0].registers_clusters[2].address_offset == 0x8
    assert device.peripherals[0].registers_clusters[2].size == 32
    assert len(device.peripherals[0].registers_clusters[2].fields) == 1
    assert device.peripherals[0].registers_clusters[2].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[2].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[2].fields[0].msb == 2


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="Circular inheritance is not supported")
def test_circular_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("register_inheritance_via_derivedfrom/circular_inheritance.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="FieldA is already defined in RegisterA and cannot be inherited because it has the same name",
)
def test_field_inheritance_same_name(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("register_inheritance_via_derivedfrom/field_inheritance_same_name.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="FieldA overlaps with FieldB",
)
def test_field_inheritance_same_bit_range(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("register_inheritance_via_derivedfrom/field_inheritance_same_bit_range.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="FieldA overlaps with FieldB",
)
def test_field_inheritance_overlap_bit_range(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("register_inheritance_via_derivedfrom/field_inheritance_overlap_bit_range.svd")


def test_same_address(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("register_inheritance_via_derivedfrom/same_address.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1
    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 2

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert len(device.peripherals[0].registers_clusters[1].fields) == 1
    assert device.peripherals[0].registers_clusters[1].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[1].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[1].fields[0].msb == 2


def test_register_overlap(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("register_inheritance_via_derivedfrom/register_overlap.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1
    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 2

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x2
    assert device.peripherals[0].registers_clusters[1].size == 16
    assert len(device.peripherals[0].registers_clusters[1].fields) == 1
    assert device.peripherals[0].registers_clusters[1].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[1].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[1].fields[0].msb == 2


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="Can't derive from self")
def test_derive_from_self(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("register_inheritance_via_derivedfrom/derive_from_self.svd")
