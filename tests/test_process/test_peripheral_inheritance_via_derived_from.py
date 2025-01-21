from typing import Callable
import pytest

from svdsuite.process import ProcessException, ProcessWarning
from svdsuite.model.process import Device, IRegister
from svdsuite.model.types import AccessType, ProtectionStringType, EnumeratedTokenType


def test_simple_inheritance_backward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "peripheral_inheritance_via_derivedfrom/simple_inheritance_backward_reference.svd"
    )

    assert len(device.peripherals) == 2
    assert len(device.peripherals[1].registers_clusters) == 1
    assert len(device.peripherals[1].address_blocks) == 1
    assert device.peripherals[1].address_blocks[0].offset == 0x0
    assert device.peripherals[1].address_blocks[0].size == 0x1000
    assert device.peripherals[1].address_blocks[0].usage == EnumeratedTokenType.REGISTERS
    assert isinstance(device.peripherals[1].registers_clusters[0], IRegister)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"


def test_simple_inheritance_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "peripheral_inheritance_via_derivedfrom/simple_inheritance_forward_reference.svd"
    )

    assert len(device.peripherals) == 2
    assert len(device.peripherals[0].registers_clusters) == 1
    assert len(device.peripherals[0].address_blocks) == 1
    assert device.peripherals[0].address_blocks[0].offset == 0x0
    assert device.peripherals[0].address_blocks[0].size == 0x1000
    assert device.peripherals[0].address_blocks[0].usage == EnumeratedTokenType.REGISTERS
    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"


def test_value_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/value_inheritance.svd")

    assert len(device.peripherals) == 2
    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].version == "1.0"
    assert device.peripherals[1].description == "PeripheralA Description"
    assert device.peripherals[1].alternate_peripheral == "PeripheralC"
    assert device.peripherals[1].group_name == "PeripheralsGroup"
    assert device.peripherals[1].prepend_to_name == "Prefix"
    assert device.peripherals[1].append_to_name == "Suffix"
    assert device.peripherals[1].header_struct_name is None  # Not inherited in svdconv
    assert device.peripherals[1].disable_condition == "0 == 0"
    assert device.peripherals[1].base_address == 0x40002000
    assert device.peripherals[1].size == 16
    assert device.peripherals[1].access == AccessType.WRITE_ONLY
    assert device.peripherals[1].protection == ProtectionStringType.SECURE
    assert device.peripherals[1].reset_value == 0xDEADBEEF
    assert device.peripherals[1].reset_mask == 0xDEADC0DE

    assert len(device.peripherals[1].address_blocks) == 1
    assert device.peripherals[1].address_blocks[0].offset == 0x0
    assert device.peripherals[1].address_blocks[0].size == 0x1000
    assert device.peripherals[1].address_blocks[0].usage == EnumeratedTokenType.REGISTERS

    assert len(device.peripherals[1].interrupts) == 0

    assert isinstance(device.peripherals[1].registers_clusters[0], IRegister)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"


def test_override_behavior(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/override_behavior.svd")

    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].version == "2.0"
    assert device.peripherals[1].description == "PeripheralB Description"
    assert device.peripherals[1].alternate_peripheral == "PeripheralD"
    assert device.peripherals[1].group_name == "PeripheralsGroup2"
    assert device.peripherals[1].prepend_to_name == "Prefix2"
    assert device.peripherals[1].append_to_name == "Suffix2"
    assert device.peripherals[1].header_struct_name == "HeaderStructName2"
    assert device.peripherals[1].disable_condition == "1 == 1"
    assert device.peripherals[1].base_address == 0x40002000
    assert device.peripherals[1].size == 64
    assert device.peripherals[1].access == AccessType.WRITE_ONCE
    assert device.peripherals[1].protection == ProtectionStringType.NON_SECURE
    assert device.peripherals[1].reset_value == 0x0F0F0F0F
    assert device.peripherals[1].reset_mask == 0xABABABAB

    assert len(device.peripherals[1].address_blocks) == 1
    assert device.peripherals[1].address_blocks[0].offset == 0x0
    assert device.peripherals[1].address_blocks[0].size == 0x2000
    assert device.peripherals[1].address_blocks[0].usage == EnumeratedTokenType.REGISTERS

    assert len(device.peripherals[1].interrupts) == 1
    assert device.peripherals[1].interrupts[0].name == "InterruptC"
    assert device.peripherals[1].interrupts[0].description == "InterruptC Description"
    assert device.peripherals[1].interrupts[0].value == 2

    assert len(device.peripherals[1].registers_clusters) == 2
    assert isinstance(device.peripherals[1].registers_clusters[0], IRegister)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert isinstance(device.peripherals[1].registers_clusters[1], IRegister)
    assert device.peripherals[1].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[1].registers_clusters[1].address_offset == 0x8


def test_multiple_inheritance_backward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "peripheral_inheritance_via_derivedfrom/multiple_inheritance_backward_reference.svd"
    )

    assert len(device.peripherals) == 3

    assert device.peripherals[1].name == "PeripheralB"
    assert len(device.peripherals[1].registers_clusters) == 1
    assert len(device.peripherals[1].address_blocks) == 1
    assert device.peripherals[1].address_blocks[0].offset == 0x0
    assert device.peripherals[1].address_blocks[0].size == 0x1000
    assert device.peripherals[1].address_blocks[0].usage == EnumeratedTokenType.REGISTERS
    assert isinstance(device.peripherals[1].registers_clusters[0], IRegister)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"

    assert device.peripherals[2].name == "PeripheralC"
    assert len(device.peripherals[2].registers_clusters) == 1
    assert len(device.peripherals[2].address_blocks) == 1
    assert device.peripherals[2].address_blocks[0].offset == 0x0
    assert device.peripherals[2].address_blocks[0].size == 0x1000
    assert device.peripherals[2].address_blocks[0].usage == EnumeratedTokenType.REGISTERS
    assert isinstance(device.peripherals[2].registers_clusters[0], IRegister)
    assert device.peripherals[2].registers_clusters[0].name == "RegisterA"


def test_multiple_inheritance_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "peripheral_inheritance_via_derivedfrom/multiple_inheritance_forward_reference.svd"
    )

    assert len(device.peripherals) == 3

    assert device.peripherals[0].name == "PeripheralA"
    assert len(device.peripherals[0].registers_clusters) == 1
    assert len(device.peripherals[0].address_blocks) == 1
    assert device.peripherals[0].address_blocks[0].offset == 0x0
    assert device.peripherals[0].address_blocks[0].size == 0x1000
    assert device.peripherals[0].address_blocks[0].usage == EnumeratedTokenType.REGISTERS
    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"

    assert device.peripherals[1].name == "PeripheralB"
    assert len(device.peripherals[1].registers_clusters) == 1
    assert len(device.peripherals[1].address_blocks) == 1
    assert device.peripherals[1].address_blocks[0].offset == 0x0
    assert device.peripherals[1].address_blocks[0].size == 0x1000
    assert device.peripherals[1].address_blocks[0].usage == EnumeratedTokenType.REGISTERS
    assert isinstance(device.peripherals[1].registers_clusters[0], IRegister)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"


def test_multiple_inheritance_backward_and_forward_reference_with_value_override(
    get_processed_device_from_testfile: Callable[[str], Device]
):
    device = get_processed_device_from_testfile(
        "peripheral_inheritance_via_derivedfrom/"
        "multiple_inheritance_backward_and_forward_reference_with_value_override.svd"
    )

    assert len(device.peripherals) == 3

    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].prepend_to_name == "Prepend"
    assert device.peripherals[0].append_to_name == "Append2"
    assert device.peripherals[0].disable_condition == "1 == 1"
    assert device.peripherals[0].base_address == 0x40001000
    assert device.peripherals[0].size == 64
    assert len(device.peripherals[0].address_blocks) == 1
    assert device.peripherals[0].address_blocks[0].offset == 0x0
    assert device.peripherals[0].address_blocks[0].size == 0x1000
    assert device.peripherals[0].address_blocks[0].usage == EnumeratedTokenType.REGISTERS
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 64

    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].prepend_to_name == "Prepend"
    assert device.peripherals[1].append_to_name == "Append2"
    assert device.peripherals[1].disable_condition == "1 == 1"
    assert device.peripherals[1].base_address == 0x40002000
    assert device.peripherals[1].size == 128
    assert len(device.peripherals[1].address_blocks) == 1
    assert device.peripherals[1].address_blocks[0].offset == 0x0
    assert device.peripherals[1].address_blocks[0].size == 0x1000
    assert device.peripherals[1].address_blocks[0].usage == EnumeratedTokenType.REGISTERS
    assert len(device.peripherals[1].registers_clusters) == 1
    assert isinstance(device.peripherals[1].registers_clusters[0], IRegister)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[0].size == 128

    assert device.peripherals[2].name == "PeripheralC"
    assert device.peripherals[2].prepend_to_name == "Prepend"
    assert device.peripherals[2].append_to_name == "Append"
    assert device.peripherals[2].disable_condition == "0 == 0"
    assert device.peripherals[2].base_address == 0x40003000
    assert device.peripherals[2].size == 16
    assert len(device.peripherals[2].address_blocks) == 1
    assert device.peripherals[2].address_blocks[0].offset == 0x0
    assert device.peripherals[2].address_blocks[0].size == 0x1000
    assert device.peripherals[2].address_blocks[0].usage == EnumeratedTokenType.REGISTERS
    assert len(device.peripherals[2].registers_clusters) == 1
    assert isinstance(device.peripherals[2].registers_clusters[0], IRegister)
    assert device.peripherals[2].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[2].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[2].registers_clusters[0].size == 16


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="Circular inheritance is not supported")
def test_circular_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/circular_inheritance.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason=(
        "RegisterA is already defined in PeripheralB and cannot be inherited from PeripheralA "
        "because it has the same name"
    ),
)
def test_register_inheritance_same_name(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/register_inheritance_same_name.svd")


def test_register_inheritance_same_address(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile(
            "peripheral_inheritance_via_derivedfrom/register_inheritance_same_address.svd"
        )

    assert len(device.peripherals) == 2
    assert device.peripherals[1].name == "PeripheralB"
    assert len(device.peripherals[1].registers_clusters) == 2
    assert isinstance(device.peripherals[1].registers_clusters[0], IRegister)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert isinstance(device.peripherals[1].registers_clusters[1], IRegister)
    assert device.peripherals[1].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[1].registers_clusters[1].address_offset == 0x0


def test_register_inheritance_same_address_dim(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile(
            "peripheral_inheritance_via_derivedfrom/register_inheritance_same_address_dim.svd"
        )

    assert len(device.peripherals) == 2
    assert device.peripherals[1].name == "PeripheralB"
    assert len(device.peripherals[1].registers_clusters) == 4

    assert isinstance(device.peripherals[1].registers_clusters[0], IRegister)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA0"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[1].registers_clusters[1], IRegister)
    assert device.peripherals[1].registers_clusters[1].name == "RegisterB0"
    assert device.peripherals[1].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[1].size == 32

    assert isinstance(device.peripherals[1].registers_clusters[2], IRegister)
    assert device.peripherals[1].registers_clusters[2].name == "RegisterA1"
    assert device.peripherals[1].registers_clusters[2].address_offset == 0x4
    assert device.peripherals[1].registers_clusters[2].size == 32

    assert isinstance(device.peripherals[1].registers_clusters[3], IRegister)
    assert device.peripherals[1].registers_clusters[3].name == "RegisterB1"
    assert device.peripherals[1].registers_clusters[3].address_offset == 0x4
    assert device.peripherals[1].registers_clusters[3].size == 32


def test_register_inheritance_overlap_address(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile(
            "peripheral_inheritance_via_derivedfrom/register_inheritance_overlap_address.svd"
        )

    assert len(device.peripherals) == 2
    assert device.peripherals[1].name == "PeripheralB"
    assert len(device.peripherals[1].registers_clusters) == 2
    assert isinstance(device.peripherals[1].registers_clusters[0], IRegister)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[0].size == 32
    assert isinstance(device.peripherals[1].registers_clusters[1], IRegister)
    assert device.peripherals[1].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[1].registers_clusters[1].address_offset == 0x2
    assert device.peripherals[1].registers_clusters[1].size == 16


def test_register_inheritance_oversized_field(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile(
            "peripheral_inheritance_via_derivedfrom/register_inheritance_oversized_field.svd"
        )

    assert len(device.peripherals) == 2

    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].size == 32
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1
    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 31

    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].size == 16
    assert len(device.peripherals[1].registers_clusters) == 1
    assert isinstance(device.peripherals[1].registers_clusters[0], IRegister)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[0].size == 16
    assert len(device.peripherals[1].registers_clusters[0].fields) == 1
    assert device.peripherals[1].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[1].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[1].registers_clusters[0].fields[0].msb == 31


def test_register_properties_inheritance_size_adjustment(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "peripheral_inheritance_via_derivedfrom/register_properties_inheritance_size_adjustment.svd"
    )

    assert len(device.peripherals) == 4

    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].size == 32
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].size == 32

    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].size == 16
    assert len(device.peripherals[1].registers_clusters) == 1
    assert isinstance(device.peripherals[1].registers_clusters[0], IRegister)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].size == 16

    assert device.peripherals[2].name == "PeripheralC"
    assert device.peripherals[2].size == 32
    assert len(device.peripherals[2].registers_clusters) == 1
    assert isinstance(device.peripherals[2].registers_clusters[0], IRegister)
    assert device.peripherals[2].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[2].registers_clusters[0].size == 32

    assert device.peripherals[3].name == "PeripheralD"
    assert device.peripherals[3].size == 32
    assert len(device.peripherals[3].registers_clusters) == 1
    assert isinstance(device.peripherals[3].registers_clusters[0], IRegister)
    assert device.peripherals[3].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[3].registers_clusters[0].size == 32


def test_same_address(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/same_address.svd")

    assert len(device.peripherals) == 2
    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].base_address == 0x40001000
    assert len(device.peripherals[0].registers_clusters) == 1
    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].base_address == 0x40001000
    assert len(device.peripherals[1].registers_clusters) == 1


def test_block_overlap(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/block_overlap.svd")

    assert len(device.peripherals) == 2
    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].base_address == 0x40001000
    assert len(device.peripherals[0].registers_clusters) == 1
    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].base_address == 0x40001004
    assert len(device.peripherals[1].registers_clusters) == 1


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Two peripherals cannot have the same name",
)
def test_same_name(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/same_name.svd")


def test_alternate_peripheral(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/alternate_peripheral.svd")

    assert len(device.peripherals) == 2
    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].base_address == 0x40001000
    assert len(device.peripherals[0].registers_clusters) == 1
    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].base_address == 0x40001000
    assert device.peripherals[1].alternate_peripheral == "PeripheralA"
    assert len(device.peripherals[1].registers_clusters) == 1


def test_alternate_peripheral_overlap(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "peripheral_inheritance_via_derivedfrom/alternate_peripheral_overlap.svd"
    )

    assert len(device.peripherals) == 2
    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].base_address == 0x40001000
    assert len(device.peripherals[0].registers_clusters) == 1
    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].base_address == 0x40001004
    assert device.peripherals[1].alternate_peripheral == "PeripheralA"
    assert len(device.peripherals[1].registers_clusters) == 1


def test_register_inheritance_alternate_group(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "peripheral_inheritance_via_derivedfrom/register_inheritance_alternate_group.svd"
    )

    assert len(device.peripherals) == 2
    assert device.peripherals[1].name == "PeripheralB"
    assert len(device.peripherals[1].registers_clusters) == 2
    assert isinstance(device.peripherals[1].registers_clusters[0], IRegister)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[0].size == 32
    assert device.peripherals[1].registers_clusters[0].alternate_group is None
    assert isinstance(device.peripherals[1].registers_clusters[1], IRegister)
    assert device.peripherals[1].registers_clusters[1].name == "RegisterA_RegisterX"
    assert device.peripherals[1].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[1].size == 32
    assert device.peripherals[1].registers_clusters[1].alternate_group == "RegisterX"


def test_register_inheritance_alternate_register(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "peripheral_inheritance_via_derivedfrom/register_inheritance_alternate_register.svd"
    )

    assert len(device.peripherals) == 2
    assert device.peripherals[1].name == "PeripheralB"
    assert len(device.peripherals[1].registers_clusters) == 2
    assert isinstance(device.peripherals[1].registers_clusters[0], IRegister)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[0].size == 32
    assert device.peripherals[1].registers_clusters[0].alternate_register is None
    assert isinstance(device.peripherals[1].registers_clusters[1], IRegister)
    assert device.peripherals[1].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[1].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[1].size == 32
    assert device.peripherals[1].registers_clusters[1].alternate_register == "RegisterA"


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="Can't derive from self")
def test_derive_from_self(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/derive_from_self.svd")
