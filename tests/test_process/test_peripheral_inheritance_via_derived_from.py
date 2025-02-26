"""
For this feature, test cases cover scenarios where a derived peripheral inherits properties from a base peripheral,
ensuring correct behavior when values are inherited.
"""

from typing import Callable
import pytest

from svdsuite.process import ProcessException, ProcessWarning
from svdsuite.model.process import Device, Register
from svdsuite.model.types import AccessType, ProtectionStringType, EnumeratedTokenType


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_inheritance_backward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    The derived peripheral (PeripheralB) is declared **after** the base peripheral (PeripheralA), representing the
    typical and straightforward inheritance scenario. The test ensures that peripheral PeripheralB correctly
    inherits register RegisterA from Peripheral PeripheralA.

    **Expected Outcome:** The device is processed correctly, and peripheral inheritance functions as expected.
    PeripheralB correctly inherits the register `RegisterA` from PeripheralA. The device contains two peripherals,
    with PeripheralB having one register and one address block. The address block in PeripheralB starts at offset
    `0x0`, has a size of `0x1000`, and is used for registers. The inherited register is correctly identified as
    `RegisterA`.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile(
        "peripheral_inheritance_via_derivedfrom/simple_inheritance_backward_reference.svd"
    )

    assert len(device.peripherals) == 2
    assert len(device.peripherals[1].registers_clusters) == 1
    assert len(device.peripherals[1].address_blocks) == 1
    assert device.peripherals[1].address_blocks[0].offset == 0x0
    assert device.peripherals[1].address_blocks[0].size == 0x1000
    assert device.peripherals[1].address_blocks[0].usage == EnumeratedTokenType.REGISTERS
    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_inheritance_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    The derived peripheral (PeripheralA) is declared before the base peripheral (PeripheralB), but PeripheralA
    inherits from PeripheralB. This tests the parser's ability to handle forward references, resolving references
    to elements defined later in the SVD file.

    **Expected Outcome:** The parser successfully resolves the forward reference where PeripheralA inherits from
    PeripheralB, despite PeripheralB being declared later in the SVD file. The device contains two peripherals,
    with PeripheralA having one register and one address block. The address block in PeripheralA starts at offset
    `0x0`, has a size of `0x1000`, and is used for registers. The inherited register is correctly identified as
    `RegisterA`.

    **Processable with svdconv:** no - `svdconv` can't handle forward references over different peripherals.
    """

    device = get_processed_device_from_testfile(
        "peripheral_inheritance_via_derivedfrom/simple_inheritance_forward_reference.svd"
    )

    assert len(device.peripherals) == 2
    assert len(device.peripherals[0].registers_clusters) == 1
    assert len(device.peripherals[0].address_blocks) == 1
    assert device.peripherals[0].address_blocks[0].offset == 0x0
    assert device.peripherals[0].address_blocks[0].size == 0x1000
    assert device.peripherals[0].address_blocks[0].usage == EnumeratedTokenType.REGISTERS
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_value_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test ensures that child elements from a base peripheral (PeripheralA) are correctly inherited by a
    derived peripheral (PeripheralB).

    **Expected Outcome:** The derived peripheral, PeripheralB, inherits the correct values from PeripheralA.
    PeripheralB should have the `name` "PeripheralB", `version` "1.0", `description` "PeripheralA Description", an
    `alternatePeripheral` of "PeripheralC", a `groupName` "PeripheralsGroup", a `prependToName` "Prefix", and a
    `appendToName` "Suffix". The `header_struct_name` is not inherited, which corresponds to the behavior of
    svdconv, but the `disable_condition` is set to `"0 == 0"`. Additionally, PeripheralB should have a base
    address of `0x40002000`, a `size` of 16 bits, `access` type of `WRITE_ONLY`, `protection` type `SECURE`, a
    `resetValue` of `0xDEADBEEF`, and a `resetMask` of `0xDEADC0DE`. PeripheralB has one address block starting at
    offset `0x0`, with a size of `0x1000` and usage for registers. PeripheralB contains no interrupts, and it
    correctly inherits the register `RegisterA`.

    **Processable with svdconv:** no - see Github issue [#1796](https://github.com/Open-CMSIS-
    Pack/devtools/issues/1796)
    """

    device = get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/value_inheritance.svd")

    assert len(device.peripherals) == 2
    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].version == "1.0"
    assert device.peripherals[1].description == "PeripheralA Description"
    assert device.peripherals[1].alternate_peripheral == "PeripheralB"
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

    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_override_behavior(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks whether specific values of a derived peripheral can override the inherited values from a base
    peripheral. It ensures that modifications to values like `name`, `version`, `description`, and others in the
    derived peripheral are applied correctly, while still inheriting the base peripheral's structure when not
    explicitly overridden.

    **Expected Outcome:** The derived peripheral, PeripheralB, correctly overrides inherited values from the base
    peripheral. PeripheralB should have the `name` "PeripheralB", `version` "2.0", `description` "PeripheralB
    Description", an `alternatePeripheral` of "PeripheralD", a `groupName` "PeripheralsGroup2", a `prependToName`
    "Prefix2", and a `appendToName` "Suffix2". Additionally, the `header_struct_name` is correctly set to
    "HeaderStructName2", and the `disable_condition` is `"1 == 1"`. PeripheralB should also have a base address of
    `0x40002000`, a `size` of 64 bits, `access` type `WRITE_ONCE`, `protection` type `NON_SECURE`, a `resetValue`
    of `0x0F0F0F0F`, and a `resetMask` of `0xABABABAB`. PeripheralB contains one address block starting at offset
    `0x0`, with a size of `0x2000` and usage for registers. It also contains one interrupt, named `InterruptC`,
    with a description "InterruptC Description" and a value of 2. Additionally, PeripheralB contains two
    registers: `RegisterA` with an address offset of `0x0`, and `RegisterB` with an address offset of `0x8`.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/override_behavior.svd")

    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].version == "2.0"
    assert device.peripherals[1].description == "PeripheralB Description"
    assert device.peripherals[1].alternate_peripheral == "PeripheralA"
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
    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert isinstance(device.peripherals[1].registers_clusters[1], Register)
    assert device.peripherals[1].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[1].registers_clusters[1].address_offset == 0x8


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_multiple_inheritance_backward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test ensures that inheritance across multiple peripherals works as expected, where PeripheralB is derived
    first, and only afterward, PeripheralC can be derived from PeripheralB. It verifies that PeripheralC correctly
    inherits from PeripheralB, which in turn inherits from a base peripheral.

    **Expected Outcome:** The device should contain three peripherals, with PeripheralB and PeripheralC correctly
    following the inheritance chain. PeripheralB inherits from the base peripheral and contains one register and
    one address block. PeripheralC inherits from PeripheralB, maintaining the inherited structure. PeripheralB has
    the name "PeripheralB", one register named `RegisterA`, and one address block with an offset of `0x0`, a size
    of `0x1000`, and usage for registers. PeripheralC, derived from PeripheralB, has the name "PeripheralC", also
    contains the register `RegisterA`, and has an identical address block with an offset of `0x0`, a size of
    `0x1000`, and usage for registers. The inheritance process between multiple peripherals is handled correctly.

    **Processable with svdconv:** yes
    """

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
    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"

    assert device.peripherals[2].name == "PeripheralC"
    assert len(device.peripherals[2].registers_clusters) == 1
    assert len(device.peripherals[2].address_blocks) == 1
    assert device.peripherals[2].address_blocks[0].offset == 0x0
    assert device.peripherals[2].address_blocks[0].size == 0x1000
    assert device.peripherals[2].address_blocks[0].usage == EnumeratedTokenType.REGISTERS
    assert isinstance(device.peripherals[2].registers_clusters[0], Register)
    assert device.peripherals[2].registers_clusters[0].name == "RegisterA"


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_multiple_inheritance_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test ensures that inheritance across multiple peripherals is correctly handled when forward references
    are involved, where PeripheralA inherits from PeripheralB, and PeripheralB inherits from PeripheralC.

    **Expected Outcome:** The device should contain three peripherals. PeripheralC is the base peripheral and contains
    one register named `RegisterA` and one address block with an offset of `0x0`, a size of `0x1000`, and usage
    for registers. PeripheralB inherits from PeripheralC and should correctly include the inherited register
    `RegisterA` and the address block with the same properties. Finally, PeripheralA, which inherits from
    PeripheralB, also includes the inherited register `RegisterA` and the same address block structure. The test
    verifies that forward inheritance through multiple peripherals works correctly, even though `svdconv` is not
    capable of processing forward references over different peripherals.

    **Processable with svdconv:** no - `svdconv` can't handle forward references over different peripherals.
    """

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
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"

    assert device.peripherals[1].name == "PeripheralB"
    assert len(device.peripherals[1].registers_clusters) == 1
    assert len(device.peripherals[1].address_blocks) == 1
    assert device.peripherals[1].address_blocks[0].offset == 0x0
    assert device.peripherals[1].address_blocks[0].size == 0x1000
    assert device.peripherals[1].address_blocks[0].usage == EnumeratedTokenType.REGISTERS
    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_multiple_inheritance_backward_and_forward_reference_with_value_override(
    get_processed_device_from_testfile: Callable[[str], Device]
):
    """
    This test ensures that multiple inheritance involving both backward and forward references is handled
    correctly, with value overrides applied at each level. Specifically, PeripheralC is the base peripheral,
    PeripheralA inherits from PeripheralC, and PeripheralB inherits from PeripheralA. Additionally, the test
    verifies that the `size` value specified at the peripheral level is correctly propagated down to the
    registers.

    **Expected Outcome:** The device contains three peripherals, each correctly inheriting properties from the
    previous peripheral and overriding specific values where necessary. The `size` value defined at each
    peripheral level is inherited by the registers within those peripherals. PeripheralA inherits from PeripheralC
    and overrides certain values while maintaining the inheritance structure. It has the `name` "PeripheralA", a
    `prependToName` of "Prepend", an `appendToName` of "Append2", a `disableCondition` of "1 == 1", a
    `baseAddress` of `0x40001000`, and a `size` of 64 bits. It contains one address block with an offset of `0x0`,
    a size of `0x1000`, and usage for registers. PeripheralA also inherits the register `RegisterA` from
    PeripheralC, with the overridden `size` of 64 bits and an address offset of `0x0`. PeripheralB, which inherits
    from PeripheralA, overrides the `baseAddress`, `size`, and the size of the inherited register. It has the
    `name` "PeripheralB", a `prependToName` of "Prepend", an `appendToName` of "Append2", a `disableCondition` of
    "1 == 1", a `baseAddress` of `0x40002000`, and a `size` of 128 bits. It contains one address block with an
    offset of `0x0`, a size of `0x1000`, and usage for registers. The register `RegisterA` is inherited from
    PeripheralA, but with the size of 128 bits, correctly reflecting the peripheral-level override. PeripheralC is
    the base peripheral and defines the initial values. It has the `name` "PeripheralC", a `prependToName` of
    "Prepend", an `appendToName` of "Append", a `disableCondition` of "0 == 0", a `baseAddress` of `0x40003000`,
    and a `size` of 16 bits. It contains one address block with an offset of `0x0`, a size of `0x1000`, and usage
    for registers. The register `RegisterA` is defined at this level with an address offset of `0x0` and a size of
    16 bits. The test confirms that the inheritance chain works as expected, with value overrides properly
    applied, and that the `size` value specified at the peripheral level is correctly propagated to the registers
    within those peripherals, even though `svdconv` cannot handle forward references over different peripherals.

    **Processable with svdconv:** no - `svdconv` can't handle forward references over different peripherals.
    """

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
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
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
    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
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
    assert isinstance(device.peripherals[2].registers_clusters[0], Register)
    assert device.peripherals[2].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[2].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[2].registers_clusters[0].size == 16


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="Circular inheritance is not supported")
def test_circular_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test ensures that the parser correctly identifies and handles circular inheritance, where three
    peripherals, `PeripheralA`, `PeripheralB`, and `PeripheralC`, attempt to inherit from each other, creating a
    loop. Circular references should be detected, and the parser should raise an appropriate error to prevent
    infinite recursion or incorrect parsing.

    **Expected Outcome:** The parser should detect the circular inheritance between `PeripheralA`, `PeripheralB`, and
    `PeripheralC`, and fail with an error indicating that circular inheritance is not supported. The test should
    raise a `ProcessException` or an equivalent error, ensuring that the parser does not attempt to resolve the
    circular references and avoids potential infinite loops.

    **Processable with svdconv:** no - although `svdconv` fails to process this test case, it is not due to the
    detection of circular inheritance but because `svdconv` does not support forward references over different
    peripherals.
    """

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
    """
    This test ensures that the parser correctly handles the case where a register in a derived peripheral has the
    same name as an inherited register from a base peripheral. The test verifies whether the parser raises an
    error when a register with the same name is defined both in the base and the derived peripheral, which would
    create a naming conflict.

    **Expected Outcome:** The parser should detect that `RegisterA` is already defined in `PeripheralB` and cannot be
    inherited from `PeripheralA` due to the naming conflict. The parser is expected to raise a `ProcessException`
    or an equivalent error indicating that the register inheritance cannot proceed because the register name is
    already in use in the derived peripheral.

    **Processable with svdconv:** yes
    """

    get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/register_inheritance_same_name.svd")


def test_register_inheritance_same_address(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test ensures that the parser correctly handles cases where a register is derived from another peripheral,
    so that two registers within the same peripheral are assigned the same address. Although `svdconv` generally
    raises an error when two registers share the same address, for compatibility with older `svdconv` versions, a
    warning is generated in [some situations](https://github.com/Open-CMSIS-
    Pack/devtools/blob/44643999691347946562c526fc0474194f865c74/tools/svdconv/SVDModel/src/SvdPeripheral.cpp#L721)
    (e.g., when using `dim`). For a parser designed to work with both new and old SVD files, it is recommended to
    allow registers with the same addresses but issue a warning to the user.

    **Expected Outcome:** The parser should detect that `RegisterA` and `RegisterB` are assigned the same address
    (`0x00000000`) within peripheral `PeripheralB`. Instead of failing, the parser should successfully process the
    SVD file but issue a warning (`ProcessWarning`) to inform the user about the address conflict. The device
    should contain two peripherals, and the second peripheral should have two registers, `RegisterA` and
    `RegisterB`, both with an address offset of `0x0`.

    **Processable with svdconv:** no - see subfeature test case description
    """

    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile(
            "peripheral_inheritance_via_derivedfrom/register_inheritance_same_address.svd"
        )

    assert len(device.peripherals) == 2
    assert device.peripherals[1].name == "PeripheralB"
    assert len(device.peripherals[1].registers_clusters) == 2
    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert isinstance(device.peripherals[1].registers_clusters[1], Register)
    assert device.peripherals[1].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[1].registers_clusters[1].address_offset == 0x0


def test_register_inheritance_same_address_dim(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test is similar to the one above, but in this case, `dim` is used, which causes `svdconv` to issue a
    warning instead of an error for compatibility reasons.

    **Expected Outcome:** The parser should successfully process the SVD file without errors, even though `RegisterA0`
    and `RegisterB0` share the same address offset of `0x0`, and `RegisterA1` and `RegisterB1` share the address
    offset of `0x4`. Each register has a size of 32 bits, resulting in overlapping addresses. While this overlap
    occurs, the parser should continue processing and, as recommended, may issue a warning to inform the user
    about the overlapping addresses. The device should contain two peripherals, and `PeripheralB` should have four
    registers expanded using `dim`, with the correct address offsets and sizes maintained for each register.

    **Processable with svdconv:** yes
    """

    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile(
            "peripheral_inheritance_via_derivedfrom/register_inheritance_same_address_dim.svd"
        )

    assert len(device.peripherals) == 2
    assert device.peripherals[1].name == "PeripheralB"
    assert len(device.peripherals[1].registers_clusters) == 4

    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA0"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[1].registers_clusters[1], Register)
    assert device.peripherals[1].registers_clusters[1].name == "RegisterB0"
    assert device.peripherals[1].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[1].size == 32

    assert isinstance(device.peripherals[1].registers_clusters[2], Register)
    assert device.peripherals[1].registers_clusters[2].name == "RegisterA1"
    assert device.peripherals[1].registers_clusters[2].address_offset == 0x4
    assert device.peripherals[1].registers_clusters[2].size == 32

    assert isinstance(device.peripherals[1].registers_clusters[3], Register)
    assert device.peripherals[1].registers_clusters[3].name == "RegisterB1"
    assert device.peripherals[1].registers_clusters[3].address_offset == 0x4
    assert device.peripherals[1].registers_clusters[3].size == 32


def test_register_inheritance_overlap_address(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test ensures that the parser correctly handles cases where a register is derived from another peripheral,
    resulting in two registers within the same peripheral having overlapping address spaces. For backward
    compatibility with older `svdconv` versions, a warning is issued when registers overlap in address space. A
    parser designed to work with both new and old SVD files should allow registers with overlapping addresses but
    issue a warning to inform the user of the conflict.

    **Expected Outcome:** The parser should detect the address overlap between `RegisterA` and `RegisterB` within
    `PeripheralB`. `RegisterA` starts at address `0x0` with a size of 32 bits, and `RegisterB` starts at address
    `0x2` with a size of 16 bits, creating the overlap. Instead of failing, the parser should successfully process
    the SVD file and issue a warning to inform the user of the overlap.

    **Processable with svdconv:** yes
    """

    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile(
            "peripheral_inheritance_via_derivedfrom/register_inheritance_overlap_address.svd"
        )

    assert len(device.peripherals) == 2
    assert device.peripherals[1].name == "PeripheralB"
    assert len(device.peripherals[1].registers_clusters) == 2
    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[0].size == 32
    assert isinstance(device.peripherals[1].registers_clusters[1], Register)
    assert device.peripherals[1].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[1].registers_clusters[1].address_offset == 0x2
    assert device.peripherals[1].registers_clusters[1].size == 16


def test_register_inheritance_oversized_field(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    PeripheralB inherits from PeripheralA. PeripheralA contains `RegisterA`, which has a default size of 32 bits.
    `RegisterA` includes a field, `FieldA`, with a bit width of 32 bits. When inherited by PeripheralB, the size
    of `RegisterA` is reduced to 16 bits because PeripheralB has its size set to 16. However, `FieldA` is
    inherited with its original 32-bit width, which exceeds the space available in `RegisterA` within PeripheralB.
    Despite this mismatch, `svdconv` neither raises a warning nor an error. A parser should be aware of this
    condition and warn the user when a field exceeds the size of its containing register.

    **Expected Outcome:** The parser should process the file successfully and may issue a warning (`ProcessWarning`)
    to inform the user that `FieldA` exceeds the 16-bit size of `RegisterA` in PeripheralB. The device contains
    two peripherals: PeripheralA has `RegisterA` with a size of 32 bits and a field, `FieldA`, that spans from bit
    0 to bit 31. PeripheralB inherits `RegisterA`, but with a reduced size of 16 bits, while `FieldA` retains its
    original 32-bit width. This creates a mismatch, as `RegisterA` in PeripheralB lacks sufficient space to
    accommodate the full width of `FieldA`. The parser should correctly handle the inheritance, but it should warn
    the user about the oversized field relative to the reduced register size.

    **Processable with svdconv:** yes
    """

    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile(
            "peripheral_inheritance_via_derivedfrom/register_inheritance_oversized_field.svd"
        )

    assert len(device.peripherals) == 2

    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].size == 32
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
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
    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[0].size == 16
    assert len(device.peripherals[1].registers_clusters[0].fields) == 1
    assert device.peripherals[1].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[1].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[1].registers_clusters[0].fields[0].msb == 31


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_register_properties_inheritance_size_adjustment(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test evaluates how the size property is handled during inheritance. The test file contains four
    peripherals: PeripheralA, PeripheralB, PeripheralC, and PeripheralD. PeripheralB inherits from PeripheralA,
    while PeripheralD inherits from PeripheralC. PeripheralA and PeripheralC each contain a register named
    RegisterA. In PeripheralA, the size of RegisterA is implicitly set to 32 bits (inherited from the peripheral
    level), while in PeripheralC, the size is explicitly defined as 32 bits at the register level. In `svdconv`,
    sizes are handled differently depending on whether they are set implicitly (inherited from the peripheral
    level) or explicitly at the register level. This distinction must be considered when developing a parser.

    **Expected Outcome:** The parser should process the file correctly, reflecting how sizes are inherited or
    explicitly defined. PeripheralA has a size of 32 bits, which is implicitly applied to RegisterA. PeripheralB
    inherits from PeripheralA but adjusts its size to 16 bits, and this change is reflected in RegisterA, which
    now has a size of 16 bits. In contrast, PeripheralC explicitly defines the size of RegisterA as 32 bits at the
    register level, and this size remains unchanged in PeripheralD, which inherits from PeripheralC. The parser
    should correctly handle both the implicit and explicit size settings, ensuring that the sizes are applied as
    expected for each peripheral and register.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile(
        "peripheral_inheritance_via_derivedfrom/register_properties_inheritance_size_adjustment.svd"
    )

    assert len(device.peripherals) == 4

    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].size == 32
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].size == 32

    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].size == 16
    assert len(device.peripherals[1].registers_clusters) == 1
    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].size == 16

    assert device.peripherals[2].name == "PeripheralC"
    assert device.peripherals[2].size == 32
    assert len(device.peripherals[2].registers_clusters) == 1
    assert isinstance(device.peripherals[2].registers_clusters[0], Register)
    assert device.peripherals[2].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[2].registers_clusters[0].size == 32

    assert device.peripherals[3].name == "PeripheralD"
    assert device.peripherals[3].size == 32
    assert len(device.peripherals[3].registers_clusters) == 1
    assert isinstance(device.peripherals[3].registers_clusters[0], Register)
    assert device.peripherals[3].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[3].registers_clusters[0].size == 32


def test_same_address(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case examines the scenario where two peripherals, `PeripheralA` and `PeripheralB`, are set to use
    the same base address (`0x40001000`). In the SVD file, `PeripheralB` is derived from `PeripheralA`, but it
    explicitly specifies the same base address. Typically, `svdconv` would issue an error for such conflicts
    because peripherals should not share the same base address unless there is an alternate relationship defined.
    However, overlapping addresses are only treated with a warning by `svdconv` due to compatibility reasons with
    older versions. Therefore, it may be advisable to allow such configurations while issuing a warning instead of
    an outright error.

    **Expected Outcome:** The parser should process the file successfully but issue a warning (e.g. `ProcessWarning`)
    to inform the user that the address blocks of `PeripheralA` and `PeripheralB` share the same address.

    **Processable with svdconv:** no
    """

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
    """
    This test checks whether the parser handles cases where the address blocks of a base peripheral and a derived
    peripheral overlap. This test ensures that when the address ranges of two peripherals partially overlap, the
    parser processes the file correctly but issues a warning to the user. The behavior mirrors that of `svdconv`,
    where overlapping address blocks do not trigger an error but generate a warning to inform the user about the
    potential conflict.

    **Expected Outcome:** The parser should process the file successfully but issue a warning (e.g. `ProcessWarning`)
    to inform the user that the address blocks of `PeripheralA` and `PeripheralB` overlap. `PeripheralA` should
    have a base address of `0x40001000`, while `PeripheralB` should start at `0x40001004`, leading to an overlap
    in their address spaces. Both peripherals should be parsed correctly, and the parser should handle the overlap
    as expected, warning the user without halting the process.

    **Processable with svdconv:** yes - with warnings
    """

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
    """
    This test checks whether a derived peripheral with the same name as its base peripheral triggers an error. The
    expected behavior mirrors that of svdconv, which also raises an error in this scenario. When two peripherals
    have the same name, it should result in a conflict, and the parser must prevent this from occurring by raising
    an appropriate error.

    **Expected Outcome:** The parser should raise an error when it encounters two peripherals, a base peripheral and
    its derived peripheral, sharing the same name. This behavior aligns with `svdconv`, where the same condition
    also triggers an error. The parser should halt processing and notify the user of the conflict, ensuring that
    no two peripherals share the same name within the SVD file.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/same_name.svd")


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_alternate_peripheral(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    By default, each address block in the memory space of a device is assigned to a unique peripheral. If multiple
    peripherals share the same address block, this must be explicitly defined. A peripheral that redefines an
    address block must specify the name of the peripheral originally associated with that block in
    `alternatePeripheral`. This test checks whether a derived peripheral with the same address as the base
    peripheral is accepted by the parser without triggering an error.

    **Expected Outcome:** The parser should process the file without raising an error, recognizing that `PeripheralB`
    shares the same base address as `PeripheralA` and correctly defines `PeripheralA` as its alternate peripheral.
    Both peripherals should be parsed correctly, with `PeripheralA` listed first and having a base address of
    `0x40001000`. `PeripheralB` should also have the same base address of `0x40001000`, with the alternate
    peripheral attribute correctly set to `PeripheralA`. The parser should handle this situation as expected,
    accepting the shared address as valid due to the explicit alternate peripheral specification.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/alternate_peripheral.svd")

    assert len(device.peripherals) == 2
    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].base_address == 0x40001000
    assert len(device.peripherals[0].registers_clusters) == 1
    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].base_address == 0x40001000
    assert device.peripherals[1].alternate_peripheral == "PeripheralA"
    assert len(device.peripherals[1].registers_clusters) == 1


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_alternate_peripheral_overlap(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    By default, each address block in the memory space of a device is assigned to a unique peripheral. If multiple
    peripherals share the same address block, this must be explicitly defined. A peripheral that redefines an
    address block must specify the name of the peripheral originally associated with that block in
    `alternatePeripheral`. This test checks whether a derived peripheral with an overlapping address block to the
    base peripheral is accepted by the parser without triggering an error.

    **Expected Outcome:** The parser should process the file without raising an error, recognizing that `PeripheralB`
    shares an overlapping address block with `PeripheralA` and correctly defines `PeripheralA` as its alternate
    peripheral. Both peripherals should be parsed correctly, with `PeripheralA` listed first and having a base
    address of `0x40001000`. `PeripheralB` should have the base address of `0x40001004`, with the alternate
    peripheral attribute correctly set to `PeripheralA`. The parser should handle this situation as expected,
    accepting the shared space as valid due to the explicit alternate peripheral specification.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_register_inheritance_alternate_group(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks how the parser handles peripheral inheritance when an alternate group is involved in a
    register. The test file includes two peripherals, `PeripheralA` and `PeripheralB`. `PeripheralA` contains a
    register, `RegisterA`, without an alternate group defined. `PeripheralB` inherits `RegisterA` but defines an
    alternate group for another register, which is also named `RegisterA`. Both registers have the same offset
    address. The test ensures that the parser can process this scenario correctly.

    **Expected Outcome:** The parser should successfully process the SVD file, correctly handling the peripheral
    inheritance and alternate group settings. `PeripheralB` contains two instances of `RegisterA`, both with the
    same address offset of `0x0` and a size of 32 bits. The first instance of `RegisterA` has no alternate group
    defined, while the second instance correctly specifies an alternate group named `RegisterX` and is named
    `RegisterA_RegisterX`. The parser should correctly handle this difference between the two instances of the
    inherited register without raising errors.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile(
        "peripheral_inheritance_via_derivedfrom/register_inheritance_alternate_group.svd"
    )

    assert len(device.peripherals) == 2
    assert device.peripherals[1].name == "PeripheralB"
    assert len(device.peripherals[1].registers_clusters) == 2
    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[0].size == 32
    assert device.peripherals[1].registers_clusters[0].alternate_group is None
    assert isinstance(device.peripherals[1].registers_clusters[1], Register)
    assert device.peripherals[1].registers_clusters[1].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[1].size == 32
    assert device.peripherals[1].registers_clusters[1].alternate_group == "RegisterX"


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_register_inheritance_alternate_register(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test evaluates the parser's ability to handle peripheral inheritance when the `alternateRegister` element
    is defined. The test file contains two peripherals, `PeripheralA` and `PeripheralB`. `PeripheralA` defines
    `RegisterA`, and `PeripheralB` inherits from `PeripheralA` while adding a new register, `RegisterB`.
    `RegisterB` shares the same address offset as `RegisterA` and defines `RegisterA` as its alternate register.
    This setup is used to ensure the parser correctly processes alternate register relationships between inherited
    registers.

    **Expected Outcome:** The parser should successfully process the SVD file, properly handling the alternate
    register relationships during inheritance. `PeripheralB` contains two registers: `RegisterA`, which has an
    address offset of `0x0` and a size of 32 bits, with no alternate register defined, and `RegisterB`, which also
    has an address offset of `0x0` and a size of 32 bits, but specifies `RegisterA` as its alternate register. The
    parser should accurately reflect this alternate register linkage without raising any errors.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile(
        "peripheral_inheritance_via_derivedfrom/register_inheritance_alternate_register.svd"
    )

    assert len(device.peripherals) == 2
    assert device.peripherals[1].name == "PeripheralB"
    assert len(device.peripherals[1].registers_clusters) == 2
    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[0].size == 32
    assert device.peripherals[1].registers_clusters[0].alternate_register is None
    assert isinstance(device.peripherals[1].registers_clusters[1], Register)
    assert device.peripherals[1].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[1].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[1].size == 32
    assert device.peripherals[1].registers_clusters[1].alternate_register == "RegisterA"


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="Can't derive from self")
def test_derive_from_self(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case evaluates a scenario where a peripheral attempts to derive from itself, creating an invalid
    configuration. In the SVD file, `PeripheralA` is defined with a `derivedFrom` attribute pointing to its own
    name. Such configurations should be detected as erroneous because a peripheral cannot logically inherit
    properties from itself. This kind of self-reference should lead to a parsing error.

    **Expected Outcome:** The parser should detect the invalid self-referential inheritance and raise an error,
    indicating that a peripheral cannot derive from itself. This ensures that the system handles such
    configurations correctly by stopping further processing and informing the user of the issue.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/derive_from_self.svd")
