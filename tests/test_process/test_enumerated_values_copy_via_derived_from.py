"""
For this feature, test cases cover scenarios where a enumerated values container (`enumeratedValues`) is copied from a
base container with `derivedFrom`. An `enumeratedValues` entry is referenced by its name. Although the CMSIS SVD
standard states, that the name is resolved by uniques or further qualifiecation by specifying the associated field,
register, and peripheral, `svdconv` can only resolve references by the same rules as the referencing `derivedFrom` works
on peripheral, cluster, register, and field level. Since the validity of SVD files is primarily verified using
`svdconv`, any parser implementation should ensure that its name resolution mechanism at the `enumeratedValues` level is
consistent with that of `svdconv`. To maintain compatibility, the parser should adopt the same approach to name
resolution, following the same rules and hierarchy used by `svdconv`.
"""

from typing import Callable
import pytest

from svdsuite.process import ProcessException
from svdsuite.model.process import Device, Register
from svdsuite.model.types import EnumUsageType


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="Two containers require usage types read and write")
def test_backward_reference_same_scope(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case examines a scenario where the `derivedFrom` attribute is used within the same scope to refer
    directly by name to another `enumeratedValues` container, without providing a fully qualified path.
    Technically, this is allowed by the SVD standard, but it is not feasible to implement. The only situation
    where two `enumeratedValues` containers can coexist within the same field is if one has a `read` usage and the
    other has a `write` usage. The SVD standard specifies that no modifications are allowed when deriving from an
    `enumeratedValues` container. Therefore, it is not possible to change the `usage` attribute when using
    `derivedFrom`. Consequently, attempting to derive in this way results in an error, as `svdconv` correctly
    detects. A robust parser implementation should behave similarly, rejecting this configuration and raising an
    appropriate error to ensure compliance with the standard's technical limitations.

    **Expected Outcome:** The parser should raise an error, indicating that two `enumeratedValues` containers cannot
    coexist within the same field unless they have distinct `read` and `write` usage types. This behavior matches
    that of `svdconv`.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("enum_copy_via_derivedfrom/backward_reference_same_scope.svd")


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_backward_reference_different_scope(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case verifies that an enumerated values container can be correctly copied from another field. In the
    SVD file, `FieldA` defines an enumerated values container named `FieldAEnumeratedValue`, while `FieldB` copies
    this container using the `derivedFrom` attribute. This allows `FieldB` to reuse the same set of enumerated
    values as `FieldA`, ensuring consistency across fields.

    **Expected Outcome:** The parser should successfully process the SVD file, allowing `FieldB` to copy the
    enumerated values from `FieldA`'s `FieldAEnumeratedValue`. The enumerated values should be identical for both
    `FieldA` and `FieldB`, and no conflicts or errors should arise during parsing.

    **Processable with svdconv:** yes
    """

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
def test_forward_reference_different_scope(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case verifies that an enumerated values container can be correctly copied from another field,
    although the base container is defined lateron in the file. In the SVD file, `FieldB` defines an enumerated
    values container named `FieldAEnumeratedValue`, while `FieldA` copies this container using the `derivedFrom`
    attribute. This allows `FieldA` to reuse the same set of enumerated values as `FieldB`, ensuring consistency
    across fields.

    **Expected Outcome:** The parser should successfully process the SVD file, allowing `FieldA` to copy the
    enumerated values from `FieldB`'s `FieldAEnumeratedValue`. The enumerated values should be identical for both
    `FieldA` and `FieldB`, and no conflicts or errors should arise during parsing. `svdconv` can't parse the file
    since it does not support forward references.

    **Processable with svdconv:** no
    """

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
