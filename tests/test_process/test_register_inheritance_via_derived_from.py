"""
For this feature, test cases cover scenarios where a derived register inherits properties from a base register, ensuring
correct behavior when values are inherited.
"""

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_inheritance_backward_reference_same_scope(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case evaluates the behavior of register inheritance using the `derivedFrom` attribute within the
    same peripheral scope. The scenario involves `RegisterB` inheriting properties from `RegisterA`, which has
    been defined earlier in the same scope. In the provided SVD file, `RegisterA` is explicitly defined with an
    address offset of `0x0`, and it contains a field named `FieldA` occupying bits 0 through 2. `RegisterB` is
    defined to inherit from `RegisterA` via the `derivedFrom` attribute, while being located at a different
    address offset (`0x4`).

    **Expected Outcome:** The parser should successfully process the SVD file, recognizing `RegisterB` as inheriting
    all attributes from `RegisterA`. This includes the field `FieldA` with the same bit positioning (bits 0 to 2).
    `RegisterA` should appear at address offset `0x0` and `RegisterB` at `0x4`, both having a size of 32 bits and
    containing an identical field structure. The parsing should complete without any issues, consistent with the
    expected behavior of `svdconv`, which correctly handles backward references within the same scope.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_inheritance_forward_reference_same_scope(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case examines the handling of register inheritance using the `derivedFrom` attribute when the base
    register is defined later in the same peripheral scope. Here, `RegisterA` is defined to inherit from
    `RegisterB`, even though `RegisterB` appears afterward in the SVD file. This setup tests the parser's ability
    to resolve forward references, where the derived register (`RegisterA`) relies on properties that are
    specified only after its own definition. In the provided SVD file, `RegisterA` uses the `derivedFrom`
    attribute to inherit from `RegisterB`, which is defined with an address offset of `0x4` and contains a field
    named `FieldA`. `RegisterA` should inherit all properties of `RegisterB`, while occupying its own distinct
    address offset (`0x0`).

    **Expected Outcome:** The parser should correctly handle the forward reference, resolving `RegisterA`'s
    inheritance from `RegisterB` and applying all relevant properties. `RegisterA` should have the same field
    structure as `RegisterB`, including `FieldA` occupying bits 0 through 2. Both registers should be correctly
    recognized, with `RegisterA` located at address offset `0x0` and `RegisterB` at `0x4`, each with a size of 32
    bits. Unlike `svdconv`, which cannot handle forward references and raises an error, the parser should resolve
    this scenario seamlessly.

    **Processable with svdconv:** no
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_inheritance_backward_reference_different_scope(
    get_processed_device_from_testfile: Callable[[str], Device]
):
    """
    This test case evaluates the behavior of register inheritance using the `derivedFrom` attribute when the base
    register is defined within a different peripheral. In the SVD file, `RegisterA` is defined within
    `PeripheralA`, located at base address `0x40001000`. This register contains a field named `FieldA`, occupying
    bits 0 through 2. In `PeripheralB`, which has a different base address (`0x40002000`), another `RegisterA` is
    defined that uses the `derivedFrom` attribute to inherit all properties from `PeripheralA.RegisterA`.

    **Expected Outcome:** The parser should correctly process the SVD file, recognizing that `PeripheralB.RegisterA`
    inherits all attributes from `PeripheralA.RegisterA`, including the field definition `FieldA`. Both registers
    should have identical structures, with the derived register correctly inheriting the properties from its base,
    even though they are defined in separate peripherals. The parsing should be consistent with `svdconv`, which
    successfully handles this cross-scope backward reference, resulting in `RegisterA` in `PeripheralB` being
    properly inherited and recognized without issues.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_inheritance_forward_reference_different_scope(
    get_processed_device_from_testfile: Callable[[str], Device]
):
    """
    This test case explores the behavior of register inheritance using the `derivedFrom` attribute when a derived
    register attempts to inherit from a base register defined in a different peripheral that appears later in the
    file. Specifically, `PeripheralA.RegisterA` is set to inherit from `PeripheralB.RegisterA`, even though
    `PeripheralB` is defined after `PeripheralA` in the SVD file. The base register `PeripheralB.RegisterA`
    contains a field named `FieldA` located at bits 0 through 2, and it is defined at address offset `0x0` within
    `PeripheralB`.

    **Expected Outcome:** The parser should be able to correctly handle this forward reference, recognizing that
    `PeripheralA.RegisterA` inherits all attributes from `PeripheralB.RegisterA`, including the field `FieldA`.
    Both registers should maintain identical structures, and the derived register should accurately reflect the
    inherited properties, despite the forward reference. Unlike `svdconv`, which cannot process this type of
    forward reference across different scopes and would produce an error, the parser is expected to resolve this
    relationship correctly, ensuring `RegisterA` in `PeripheralA` is properly inherited from
    `PeripheralB.RegisterA` without any issues.

    **Processable with svdconv:** no
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_value_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case examines how the `derivedFrom` attribute is used to inherit register properties, focusing on a
    scenario where `RegisterB` inherits multiple attributes from `RegisterA`. In the provided SVD file,
    `RegisterA` is defined with a wide range of attributes, including display name, description, access type,
    size, protection level, and more. `RegisterB` is set to inherit from `RegisterA` while having a distinct
    address offset of `0x2`. The test ensures that `RegisterB` correctly inherits all properties of `RegisterA`
    except for the explicitly overridden attributes. A special case is the attribute `displayName`. Although it is
    also inherited, it is only allowed to appear once within the scope. Therefore, it must be explicitly
    overridden in `RegisterB`.

    **Expected Outcome:** The parser should successfully process the SVD file and recognize that `RegisterB` inherits
    all applicable properties from `RegisterA`. This includes attributes such as the display name, description,
    size, access type, and protection level, among others. `RegisterA` should be located at address offset `0x0`,
    while `RegisterB` should be at `0x2`, both with the same attributes and configurations. The inherited
    properties should match precisely, reflecting accurate inheritance behavior. This is consistent with
    `svdconv`, which also handles this scenario correctly without any issues.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile("register_inheritance_via_derivedfrom/value_inheritance.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].display_name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].description == "RegisterA description"
    assert device.peripherals[0].registers_clusters[0].alternate_register == "RegisterA"
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
    assert device.peripherals[0].registers_clusters[1].alternate_register == "RegisterA"
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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_override_behavior(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case examines the use of the `derivedFrom` attribute to inherit properties from a base register
    while allowing for selective overrides. In this scenario, `RegisterB` is defined to inherit properties from
    `RegisterA`, but several attributes are explicitly overridden. The SVD file defines `RegisterA` with a
    comprehensive set of attributes, including size, access type, reset values, and field details. `RegisterB`
    inherits these attributes via `derivedFrom`, but overrides certain properties such as size, description,
    access type, and field structure.

    **Expected Outcome:** The parser should correctly process `RegisterB`, inheriting all attributes from `RegisterA`
    except those that are explicitly overridden in `RegisterB`. This means that `RegisterB` should retain
    properties like `alternateRegister`, `resetValue`, and `fields` from `RegisterA` unless a different value is
    specified. For example, `RegisterB` should inherit the field `FieldA` from `RegisterA` but should also
    introduce a new field, `FieldB`. The parser should handle this inheritance and overriding mechanism
    seamlessly, producing a result where `RegisterA` and `RegisterB` are distinct yet connected through shared
    properties. This behavior matches the expected output from `svdconv`, which processes similar cases without
    issues.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile("register_inheritance_via_derivedfrom/override_behavior.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].display_name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].description == "RegisterA description"
    assert device.peripherals[0].registers_clusters[0].alternate_register == "RegisterB"
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
    assert device.peripherals[0].registers_clusters[1].alternate_register == "RegisterA"
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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_multiple_inheritance_backward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case evaluates the functionality of register inheritance when multiple derived registers inherit
    from a base register via backward references. In this scenario, `RegisterA` is defined as the base register
    with a specific set of attributes, including fields. `RegisterB` inherits from `RegisterA`, and `RegisterC`
    subsequently inherits from `RegisterB`. This chain of backward references ensures that `RegisterC` ultimately
    inherits properties from `RegisterA` through `RegisterB`. The SVD file clearly defines the inheritance
    structure, allowing each derived register to have a distinct address offset while maintaining the core
    properties from the base register.

    **Expected Outcome:** The parser should correctly interpret the inheritance chain, ensuring that both `RegisterB`
    and `RegisterC` inherit all attributes from `RegisterA`. This means that `RegisterB` and `RegisterC` should
    have the same field (`FieldA` with bits 0 to 2) as defined in `RegisterA`. Each register should be positioned
    at their respective address offsets (`0x0` for `RegisterA`, `0x4` for `RegisterB`, and `0x8` for `RegisterC`)
    with a size of 32 bits. The parsing should be consistent with the expected behavior of `svdconv`, which
    handles such backward reference chains correctly.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_multiple_inheritance_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case examines the scenario of register inheritance using forward references. Here, `RegisterA` is
    defined to inherit from `RegisterB`, which in turn is defined to inherit from `RegisterC`. The SVD file
    specifies these registers in a sequence where `RegisterC` is defined last, creating a chain of forward
    references. The objective is to verify if the parser can correctly resolve these references and apply the
    inheritance as intended. Each derived register should inherit properties from the subsequent one in the chain,
    even though they are defined in a forward manner.

    **Expected Outcome:** The parser should successfully process the SVD file, correctly handling the forward
    references and applying the inheritance chain. This means that `RegisterA` should ultimately inherit
    properties from `RegisterC` via `RegisterB`, despite being defined earlier in the file. Each register should
    have the same field structure inherited from `RegisterC`, with `FieldA` occupying bits 0 to 2. The registers
    should appear at their respective address offsets: `0x0` for `RegisterA`, `0x4` for `RegisterB`, and `0x8` for
    `RegisterC`, all with a size of 32 bits. While `svdconv` does not handle such forward references, the parser
    should complete this without errors.

    **Processable with svdconv:** no
    """

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
    """
    This test case explores the scenario of circular inheritance, where `RegisterA` is defined to inherit from
    `RegisterB`, and `RegisterB` is, in turn, defined to inherit from `RegisterA`. This creates a circular
    reference loop, which is not a valid configuration. Circular inheritance would prevent the parser from
    resolving the properties of the registers correctly, as there would be no clear point of reference for the
    inherited attributes. The goal is to ensure that the parser detects such circular dependencies and raises an
    appropriate error to avoid an infinite loop or incorrect processing.

    **Expected Outcome:** The parser should detect the circular inheritance between `RegisterA` and `RegisterB` and
    raise an error. This indicates that circular inheritance is not allowed, and the parser correctly identifies
    and prevents it from being processed. `svdconv`, can't process the file, since deriving from `RegisterB` is
    not possible due to forward referencing.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("register_inheritance_via_derivedfrom/circular_inheritance.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="FieldA is already defined in RegisterA and cannot be inherited because it has the same name",
)
def test_field_inheritance_same_name(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case evaluates the behavior of field inheritance when a derived register (`RegisterB`) attempts to
    define a field (`FieldA`) that shares the same name as a field inherited from its base register (`RegisterA`).
    According to SVD specifications, each field within a register should have a unique name, and inheriting a
    field with the same name as an existing field in the derived register leads to a conflict. The goal of this
    test is to ensure that the parser detects this scenario and raises an appropriate error.

    **Expected Outcome:** The parser should raise an error, indicating that `FieldA` cannot be redefined in
    `RegisterB` because it already exists in the inherited properties from `RegisterA`. This behavior prevents
    conflicts in field definitions and maintains the integrity of the register's structure. Like `svdconv`, which
    also throws an error in this situation, the parser's explicit handling of this case ensures that users are
    clearly informed about the issue, guiding them to resolve such naming conflicts in their SVD files.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("register_inheritance_via_derivedfrom/field_inheritance_same_name.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="FieldA overlaps with FieldB",
)
def test_field_inheritance_same_bit_range(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case examines the scenario where a derived register (`RegisterB`) inherits `FieldA` from a base
    register (`RegisterA`) and attempts to define a new field (`FieldB`) that occupies the same bit range as an
    inherited field (`FieldA`). According to the SVD standard, fields within a register must not overlap in their
    bit ranges, and any such conflicts should be detected and flagged as errors. This test ensures that the parser
    correctly identifies the overlap and raises an appropriate error.

    **Expected Outcome:** The parser should raise an error indicating that `FieldA` and `FieldB` cannot coexist
    because they overlap in their bit ranges. This behavior aligns with `svdconv`, which also detects and reports
    such conflicts. The parser's ability to catch this issue helps maintain the integrity of register definitions
    by preventing ambiguous or conflicting field configurations.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("register_inheritance_via_derivedfrom/field_inheritance_same_bit_range.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="FieldA overlaps with FieldB",
)
def test_field_inheritance_overlap_bit_range(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case examines the scenario where a derived register (`RegisterB`) inherits `FieldA` from a base
    register (`RegisterA`) and attempts to define a new field (`FieldB`) that occupies an overlapping bit range as
    an inherited field (`FieldA`). According to the SVD standard, fields within a register must not overlap in
    their bit ranges, and any such conflicts should be detected and flagged as errors. This test ensures that the
    parser correctly identifies the overlap and raises an appropriate error.

    **Expected Outcome:** The parser should raise an error indicating that `FieldA` and `FieldB` cannot coexist
    because they overlap in their bit ranges. This behavior aligns with `svdconv`, which also detects and reports
    such conflicts. The parser's ability to catch this issue helps maintain the integrity of register definitions
    by preventing ambiguous or conflicting field configurations.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("register_inheritance_via_derivedfrom/field_inheritance_overlap_bit_range.svd")


def test_same_address(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case explores a scenario where two registers, `RegisterA` and `RegisterB`, share the same address
    offset within the same peripheral. The `RegisterB` is derived from `RegisterA`, meaning it inherits its
    configuration but is defined at the same address (`0x0`). According to the SVD standard, multiple registers
    should not occupy the same address space unless they have an alternate relationship, and `svdconv` enforces
    this rule by issuing an error. However, for enhanced compatibility, especially with older `svdconv` versions,
    it may be advisable to allow such configurations while issuing a warning instead of an outright error.

    **Expected Outcome:** The parser should issue a warning indicating that `RegisterA` and `RegisterB` share the same
    address offset, but it should still successfully process the SVD file. This approach aligns with the idea of
    maintaining compatibility with various SVD formats, including older versions where multiple registers might
    share the same address. Although `svdconv` would reject this file outright, a more flexible parser should
    permit it while clearly warning users of the potential conflict.

    **Processable with svdconv:** no
    """

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
    """
    This test case addresses a situation where two registers, `RegisterA` and `RegisterB`, have overlapping
    address spaces within the same peripheral. In this example, `RegisterB` is derived from `RegisterA` but is
    defined at an address offset (`0x2`) that causes it to overlap partially with `RegisterA`. While such overlaps
    can lead to conflicts, `svdconv` issues a warning rather than an error to maintain compatibility with older
    `svdconv` versions, which have not detected overlapping addresses. A robust parser implementation should mimic
    this behavior, issuing a warning to inform the user of the overlap but still proceed with processing the file.

    **Expected Outcome:** The parser should successfully process the SVD file but issue a warning indicating the
    address overlap between `RegisterA` and `RegisterB`. This approach maintains compatibility with existing tools
    like `svdconv`, which handle such scenarios by warning the user rather than blocking the processing
    altogether.

    **Processable with svdconv:** yes
    """

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
    """
    This test case evaluates a scenario where a register attempts to derive from itself, creating an invalid
    configuration. In the SVD file, `RegisterA` is defined with a `derivedFrom` attribute pointing to its own
    name. Such configurations should be detected as erroneous because a register cannot logically inherit
    properties from itself. This kind of self-reference should lead to a parsing error.

    **Expected Outcome:** The parser should detect the invalid self-referential inheritance and raise an error,
    indicating that a register cannot derive from itself. This ensures that the system handles such configurations
    correctly by stopping further processing and informing the user of the issue.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("register_inheritance_via_derivedfrom/derive_from_self.svd")
