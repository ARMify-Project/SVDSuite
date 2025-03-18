"""
For this feature, test cases cover scenarios where a derived field inherits properties from a base field, ensuring
correct behavior when values are inherited.
"""

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_inheritance_backward_reference_same_scope(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case focuses on field inheritance using the `derivedFrom` attribute within the same register. Here,
    `FieldB` inherits properties from `FieldA`, which is defined earlier within the same register. In the SVD
    file, `FieldA` is explicitly set up with bit offset `0` and width `1`, along with enumerated values for `read-
    write` usage. `FieldB` is derived from `FieldA`, meaning it should inherit all attributes, including the
    enumerated values, while being positioned at a different bit offset (`1`).

    **Expected Outcome:** The parser should correctly interpret the inheritance, processing `FieldB` as a field that
    inherits all attributes from `FieldA`, including its enumerated values. The result should show `FieldA` at bit
    offset `0` and `FieldB` at bit offset `1`, both sharing the same enumerated value containers. Parsing should
    complete without issues, consistent with `svdconv`, which handles this scenario correctly.

    **Processable with svdconv:** yes
    """

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
    assert fielda_enum_container.enumerated_values[1].name == "0b1"
    assert fielda_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fielda_enum_container.enumerated_values[1].value == 0b1

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
    assert fieldb_enum_container.enumerated_values[1].name == "0b1"
    assert fieldb_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fieldb_enum_container.enumerated_values[1].value == 0b1


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_inheritance_forward_reference_same_scope(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case examines field inheritance using the `derivedFrom` attribute within the same register, where
    the field being inherited from (`FieldB`) is defined later in the register than the derived field (`FieldA`).
    In the SVD file, `FieldA` uses the `derivedFrom` attribute to reference `FieldB`, which is defined afterward,
    with its enumerated values and other attributes.

    **Expected Outcome:** The parser should correctly resolve the forward reference, allowing `FieldA` to inherit all
    properties from `FieldB`, including enumerated values. Both `FieldA` and `FieldB` should be processed, with
    `FieldA` at bit offset `0` and `FieldB` at bit offset `1`, sharing the same enumerated value containers.
    Parsing should proceed without issues if the parser handles forward references properly. Unlike `svdconv`,
    which raises an error due to its inability to handle such cases, a more robust parser should accommodate this
    scenario seamlessly.

    **Processable with svdconv:** no
    """

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
    assert fielda_enum_container.enumerated_values[1].name == "0b1"
    assert fielda_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fielda_enum_container.enumerated_values[1].value == 0b1

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
    assert fieldb_enum_container.enumerated_values[1].name == "0b1"
    assert fieldb_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fieldb_enum_container.enumerated_values[1].value == 0b1


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_inheritance_backward_reference_different_scope(
    get_processed_device_from_testfile: Callable[[str], Device],
):
    """
    This test case examines field inheritance using the `derivedFrom` attribute, where the field being inherited
    from (`FieldA`) is defined within a different register (`RegisterA`) scope, but in the same peripheral, which
    requires the full qualifying path (`PeripheralA.RegisterA.FieldA`). In the SVD file, `RegisterA` explicitly
    defines `FieldA` with bit properties and enumerated values. `RegisterB` defines a field also named `FieldA`,
    which uses the `derivedFrom` attribute to inherit properties from the previously defined `FieldA` in
    `RegisterA`.

    **Expected Outcome:** The parser should correctly process the SVD file, allowing `RegisterB.FieldA` to inherit all
    properties, including enumerated values, from `RegisterA.FieldA`. This should include identical bit
    positioning, usage, and enumerated values. Parsing should complete without any issues, consistent with the
    expected behavior of `svdconv`, which successfully handles backward references across different registers in
    the same peripheral scope.

    **Processable with svdconv:** yes
    """

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
    assert rega_enum_container.enumerated_values[1].name == "0b1"
    assert rega_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert rega_enum_container.enumerated_values[1].value == 0b1

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
    assert regb_enum_container.enumerated_values[1].name == "0b1"
    assert regb_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert regb_enum_container.enumerated_values[1].value == 0b1


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_inheritance_forward_reference_different_scope(
    get_processed_device_from_testfile: Callable[[str], Device],
):
    """
    This test case evaluates field inheritance using the `derivedFrom` attribute, where the field being inherited
    (`FieldA`) is defined in a different register (`RegisterB`) within the same peripheral. However, the field in
    `RegisterA` uses a forward reference, meaning it tries to derive properties from `RegisterB.FieldA` before
    `RegisterB` is defined. In the provided SVD file, `RegisterB.FieldA` is explicitly defined with bit properties
    and enumerated values. `RegisterA.FieldA` attempts to inherit these properties via a forward reference.

    **Expected Outcome:** The parser should inherit successfully from `RegisterB.FieldA`. `svdconv` does not handle
    forward references and raises an error.

    **Processable with svdconv:** no
    """

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
    assert rega_enum_container.enumerated_values[1].name == "0b1"
    assert rega_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert rega_enum_container.enumerated_values[1].value == 0b1

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
    assert regb_enum_container.enumerated_values[1].name == "0b1"
    assert regb_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert regb_enum_container.enumerated_values[1].value == 0b1


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_value_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case examines field inheritance through the `derivedFrom` attribute, ensuring that all the
    properties from a base field (`FieldA`) are correctly inherited by a derived field (`FieldB`). In the provided
    SVD file, `FieldA` is defined with various attributes, including description, access type, write constraint,
    and enumerated value. `FieldB` is set to inherit all these properties from `FieldA`, while adjusting its
    position within the register.

    **Expected Outcome:** The parser should correctly process the SVD file, allowing `FieldB` to inherit all
    properties from `FieldA`, such as the description, access type, modified write value, write constraint, and
    enumerated value. The only changes should be the `bitOffset` and `bitWidth` adjustments as specified for
    `FieldB`. This behavior is consistent with `svdconv`, which successfully handles such backward inheritance
    cases within the same register scope. The parsing should complete without errors, and the inherited properties
    should be accurately reflected in `FieldB`.

    **Processable with svdconv:** yes
    """

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
    assert fielda_enum_container.enumerated_values[1].name == "0b1"
    assert fielda_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fielda_enum_container.enumerated_values[1].value == 0b1

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
    assert fieldb_enum_container.enumerated_values[1].name == "0b1"
    assert fieldb_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fieldb_enum_container.enumerated_values[1].value == 0b1


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_override_behavior(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case evaluates the behavior of field inheritance where a derived field (`FieldB`) inherits
    properties from a base field (`FieldA`) and overrides certain attributes. The SVD file illustrates how
    `FieldB` utilizes the `derivedFrom` attribute to inherit from `FieldA` while customizing some of its
    properties such as the description, access type, and enumerated values.

    **Expected Outcome:** The parser should correctly handle the inheritance, allowing `FieldB` to override the
    specified attributes without affecting the inherited properties. The test verifies that `FieldB` successfully
    overrides the required fields and adds its own enumerated value set without duplicating or conflicting with
    those of `FieldA`. This behavior is consistent with `svdconv`. The parsing should complete without errors, and
    the attributes should match the expected results based on the SVD definitions.

    **Processable with svdconv:** yes
    """

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
    assert fielda_enum_container.enumerated_values[1].name == "0b1"
    assert fielda_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fielda_enum_container.enumerated_values[1].value == 0b1

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
    assert fieldb_enum_container1.enumerated_values[1].name == "0b1"
    assert fieldb_enum_container1.enumerated_values[1].description == "Description for 0b1"
    assert fieldb_enum_container1.enumerated_values[1].value == 0b1

    fieldb_enum_container2 = device.peripherals[0].registers_clusters[0].fields[1].enumerated_value_containers[1]
    assert fieldb_enum_container2.name == "FieldBEnumeratedValue"
    assert fieldb_enum_container2.usage == EnumUsageType.WRITE
    assert len(fieldb_enum_container2.enumerated_values) == 2
    assert fieldb_enum_container2.enumerated_values[0].name == "0b0"
    assert fieldb_enum_container2.enumerated_values[0].description == "Description for 0b0"
    assert fieldb_enum_container2.enumerated_values[0].value == 0b0
    assert fieldb_enum_container2.enumerated_values[1].name == "0b1"
    assert fieldb_enum_container2.enumerated_values[1].description == "Description for 0b1"
    assert fieldb_enum_container2.enumerated_values[1].value == 0b1


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Field 'FieldB' (<enumeratedValues> 'FieldAEnumeratedValue'): 'read-write' container already defined",
)
def test_enumerated_value_inheritance_error(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case examines a situation where a derived field (`FieldB`) inherits properties from a base field
    (`FieldA`) but also attempts to redefine enumerated values that are incompatible with the inherited ones. The
    SVD file presents `FieldB` using the `derivedFrom` attribute to inherit from `FieldA`, but it adds a new set
    of enumerated values under the same usage type (`read-write`), which causes a conflict.

    **Expected Outcome:** The parser should detect the conflict and raise an error because `FieldB` is attempting to
    redefine enumerated values that already exist under the `read-write` usage inherited from `FieldA`. `svdconv`
    correctly identifies this issue and generates an error, stating that the enumerated value container for `read-
    write` is already defined. A robust parser should replicate this behavior, ensuring that redefinition of
    inherited enumerated values does not occur without explicitly overriding the existing container.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("field_inheritance_via_derivedfrom/enumerated_value_inheritance_error.svd")


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_multiple_inheritance_backward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case focuses on a scenario where multiple fields (`FieldB` and `FieldC`) inherit properties from a
    base field (`FieldA`) within the same register, using the `derivedFrom` attribute. `FieldB` is derived from
    `FieldA`, and `FieldC` is further derived from `FieldB`. The purpose is to verify that the parser correctly
    handles this chain of inheritance, ensuring that inherited attributes, such as enumerated values, are properly
    applied.

    **Expected Outcome:** The parser should correctly process the SVD file, allowing `FieldB` to inherit attributes
    from `FieldA` and `FieldC` to inherit from `FieldB`. Each of the fields (`FieldA`, `FieldB`, and `FieldC`)
    should have the same enumerated value container as defined in `FieldA`. The attributes such as `bitOffset` and
    `bitWidth` should be overridden as defined for each field. The parser should handle this without issues,
    consistent with `svdconv`, which successfully processes this file.

    **Processable with svdconv:** yes
    """

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
    assert fielda_enum_container.enumerated_values[1].name == "0b1"
    assert fielda_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fielda_enum_container.enumerated_values[1].value == 0b1

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
    assert fieldb_enum_container.enumerated_values[1].name == "0b1"
    assert fieldb_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fieldb_enum_container.enumerated_values[1].value == 0b1

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
    assert fieldc_enum_container.enumerated_values[1].name == "0b1"
    assert fieldc_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fieldc_enum_container.enumerated_values[1].value == 0b1


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_multiple_inheritance_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case involves multiple fields (`FieldA`, `FieldB`, `FieldC`) where `FieldA` is derived from
    `FieldB`, and `FieldB` is derived from `FieldC`, using forward references within the same register. Despite
    `svdconv`'s inability to handle forward references, a robust parser should correctly resolve these references
    and apply the inherited properties as expected. The goal is to ensure that the parser can accurately manage
    such chains of inheritance and still process the register and its fields without errors.

    **Expected Outcome:** The parser should successfully handle the forward references, allowing `FieldA` to inherit
    attributes from `FieldB`, and `FieldB` to inherit from `FieldC`. All three fields should ultimately share the
    same enumerated value container, defined in `FieldC`. Each field should also correctly override attributes
    like `bitOffset` as specified in the SVD file. This ensures compatibility and robustness beyond `svdconv`'s
    current limitations.

    **Processable with svdconv:** no
    """

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
    assert fielda_enum_container.enumerated_values[1].name == "0b1"
    assert fielda_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fielda_enum_container.enumerated_values[1].value == 0b1

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
    assert fieldb_enum_container.enumerated_values[1].name == "0b1"
    assert fieldb_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fieldb_enum_container.enumerated_values[1].value == 0b1

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
    assert fieldc_enum_container.enumerated_values[1].name == "0b1"
    assert fieldc_enum_container.enumerated_values[1].description == "Description for 0b1"
    assert fieldc_enum_container.enumerated_values[1].value == 0b1


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="Circular inheritance is not supported")
def test_circular_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case examines a scenario where circular inheritance occurs between two fields within the same
    register (`FieldA` and `FieldB`). In the SVD file, `FieldA` is defined to derive from `FieldB`, and `FieldB`
    is set to derive from `FieldA`. This creates a circular dependency, which a robust parser should detect and
    prevent from causing infinite loops or incorrect behavior. Circular inheritance should be considered invalid
    and should raise an appropriate error during processing.

    **Expected Outcome:** The parser should identify the circular dependency between `FieldA` and `FieldB` and raise
    an error, indicating that circular inheritance is not supported. This ensures that the system correctly
    handles such invalid configurations by stopping further processing and notifying the user of the issue.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("field_inheritance_via_derivedfrom/circular_inheritance.svd")


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="FieldA overlaps with FieldB")
def test_same_bit_range(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case addresses a scenario where two fields in a register are defined to occupy the same bit range.
    In the provided SVD file, `FieldA` is explicitly defined with a bit offset of `0` and a width of `1`, and
    `FieldB` is derived from `FieldA`, also attempting to use the same bit offset and width. This creates an
    overlap, which is not allowed as it leads to conflicting field definitions within the same register.

    **Expected Outcome:** The parser should detect the overlap between `FieldA` and `FieldB` and raise an error,
    indicating that both fields are trying to occupy the same bit range. This behavior aligns with `svdconv`,
    which also detects and reports such conflicts as error.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("field_inheritance_via_derivedfrom/same_bit_range.svd")


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="FieldA overlaps with FieldB")
def test_overlap_bit_range(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case examines a scenario where two fields within a register are defined to have overlapping bit
    ranges. In the SVD file provided, `FieldA` is explicitly defined with a bit offset of `0` and a width of `2`,
    while `FieldB` is derived from `FieldA` but is redefined with a bit offset of `1` and a width of `1`. This
    configuration causes `FieldB` to overlap with the range occupied by `FieldA`, leading to an invalid layout.

    **Expected Outcome:** The parser should detect the overlapping bit ranges between `FieldA` and `FieldB` and raise
    an error. This behavior ensures that fields are uniquely positioned within a register, preventing any
    conflicts in field interpretation or usage. Notably, `svdconv` exhibits the same behavior, issuing an error
    when it encounters this type of overlap.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("field_inheritance_via_derivedfrom/overlap_bit_range.svd")


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="Can't derive from self")
def test_derive_from_self(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case evaluates a scenario where a field attempts to derive from itself, creating an invalid
    configuration. In the SVD file, `FieldA` is defined with a `derivedFrom` attribute pointing to its own name.
    Such configurations should be detected as erroneous because a field cannot logically inherit properties from
    itself. This kind of self-reference should lead to a parsing error.

    **Expected Outcome:** The parser should detect the invalid self-referential inheritance and raise an error,
    indicating that a field cannot derive from itself. This ensures that the system handles such configurations
    correctly by stopping further processing and informing the user of the issue.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("field_inheritance_via_derivedfrom/derive_from_self.svd")
