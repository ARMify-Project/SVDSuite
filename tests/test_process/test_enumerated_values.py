"""
Enumerated values are used to provide human-readable names and descriptions for specific bitfields that have a limited
set of possible values. These enumerations make it easier to understand and work with specific configurations of
peripheral registers, since the enumerated names give meaningful descriptions instead of just raw numerical values.

This feature contains test cases that validate how enumerated values are defined, processed, and applied in various
scenarios. The test cases ensure that the parser correctly handles the definition and usage of enumerated values.
"""

from typing import Callable
import pytest

from svdsuite.process import Process, ProcessException, ProcessWarning
from svdsuite.model.process import Device, Register
from svdsuite.model.types import EnumUsageType


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_read_write(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test verifies how the parser handles enumerated values associated with a field that has both read and
    write access. The SVD file defines a single field with an enumerated value container specifying four possible
    values, each with a unique description. The enumerated values allow for a human-readable interpretation of the
    bitfield content. The parser must accurately interpret and process these enumerations, ensuring the values are
    correctly mapped to their corresponding descriptions.

    **Expected Outcome:** The parser should successfully process the enumerated values for the field within the
    register. It should recognize the container name as "FieldAEnumeratedValue" and categorize it for both read
    and write access. The container should contain four enumerated values, each associated with the binary values
    `0b00`, `0b01`, `0b10`, and `0b11`, with their respective descriptions. The parser should not mark any of
    these values as default. The entire structure should be parsed without any errors, matching the expected
    behavior of `svdconv`.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile("enumerated_values/simple_read_write.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1

    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]
    assert container.name == "FieldAEnumeratedValue"
    assert container.usage == EnumUsageType.READ_WRITE
    assert len(container.enumerated_values) == 4

    assert container.enumerated_values[0].name == "0b00"
    assert container.enumerated_values[0].description == "Description for 0b00"
    assert container.enumerated_values[0].value == 0b00

    assert container.enumerated_values[1].name == "0b01"
    assert container.enumerated_values[1].description == "Description for 0b01"
    assert container.enumerated_values[1].value == 0b01

    assert container.enumerated_values[2].name == "0b10"
    assert container.enumerated_values[2].description == "Description for 0b10"
    assert container.enumerated_values[2].value == 0b10

    assert container.enumerated_values[3].name == "0b11"
    assert container.enumerated_values[3].description == "Description for 0b11"
    assert container.enumerated_values[3].value == 0b11


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Too many <enumeratedValues> container specified",
)
def test_three_containers(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test examines the parser's handling of multiple `<enumeratedValues>` containers within a field. According
    to the CMSIS-SVD specification, a field can have one `<enumeratedValues>` container to define enumerated
    values for both read and write access, or two separate containers, one for read and one for write operations.
    The SVD file used in this test case deliberately includes three `<enumeratedValues>` containers, which exceeds
    the allowable configuration. This setup aims to verify that the parser correctly identifies and rejects the
    improper use of multiple enumerated value containers.

    **Expected Outcome:** The parser should raise an error due to the presence of three `<enumeratedValues>`
    containers in the SVD file. It must recognize that more than two containers are not permitted, regardless of
    the usage attributes specified. This behavior aligns with the CMSIS-SVD standard, which allows a maximum of
    two separate containers (one for read and one for write) or a single combined container for both. Since
    `svdconv` does not support more than two containers, a compliant parser implementation should similarly
    enforce this restriction, triggering an error in this scenario.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("enumerated_values/three_containers.svd")


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_default_usage(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test verifies the parser's handling of `<enumeratedValues>` containers when the `<usage>` attribute is
    not explicitly set. According to the CMSIS-SVD standard, if the `<usage>` attribute is omitted, the enumerated
    values should default to `read-write`. This behavior simplifies the definition of common cases where
    enumerated values apply equally to both read and write operations. The SVD file for this test omits the
    `<usage>` attribute to confirm that the parser correctly defaults to `read-write`.

    **Expected Outcome:** The parser should process the SVD file without errors, correctly interpreting the
    `<enumeratedValues>` container as having a `read-write` usage. It must ensure that, even when the `<usage>`
    attribute is missing, the enumerated values are accessible for both reading and writing. This behavior aligns
    with `svdconv`, which also treats the absence of a `<usage>` attribute as equivalent to `read-write`.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile("enumerated_values/default_usage.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1

    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]
    assert container.name == "FieldAEnumeratedValue"
    assert container.usage == EnumUsageType.READ_WRITE


@pytest.mark.parametrize(
    "first_input,second_input,expected1,expected2",
    [
        pytest.param(
            "read",
            "write",
            EnumUsageType.READ,
            EnumUsageType.WRITE,
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "write",
            "read",
            EnumUsageType.WRITE,
            EnumUsageType.READ,
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param("read", "read", None, None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)),
        pytest.param("write", "write", None, None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)),
        pytest.param("read", "read-write", None, None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)),
        pytest.param("write", "read-write", None, None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)),
        pytest.param("read-write", "read", None, None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)),
        pytest.param("read-write", "write", None, None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)),
        pytest.param(
            "read-write", "read-write", None, None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)
        ),
    ],
)
def test_usage_combinations(
    first_input: str,
    second_input: str,
    expected1: None | EnumUsageType,
    expected2: None | EnumUsageType,
    get_test_svd_file_content: Callable[[str], bytes],
):
    """
    This test examines how the parser handles different combinations of `<usage>` attributes within
    `<enumeratedValues>` containers. The CMSIS-SVD standard allows certain combinations of `<usage>` values (such
    as `read` and `write`) but restricts others. The test file is set up to dynamically replace the placeholders
    "FIRST_INPUT" and "SECOND_INPUT" with combinations of `read`, `write`, and `read-write`, allowing multiple
    test cases to be evaluated. The goal is to verify if the parser correctly accepts valid combinations, like
    `read` and `write`, and raises errors for invalid ones, such as `read-write` paired with any other value.

    **Expected Outcome:** The parser should process the file successfully when the `<usage>` combination is `read` and
    `write`, creating two valid `<enumeratedValues>` containers with the expected `read` and `write` usage types.
    However, it must raise errors for all other combinations, including `write` and `write`, `read` and `read`, or
    any instance where `read-write` is used in conjunction with another `<usage>`. This behavior is consistent
    with `svdconv`, which also restricts most of these combinations, except for the `read` and `write` pairing.

    **Processable with svdconv:** the combination of read and write yes, other combinations not
    """

    file_name = "enumerated_values/usage_combinations.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"FIRST_INPUT", first_input.encode())
    file_content = file_content.replace(b"SECOND_INPUT", second_input.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1

    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 2

    container1 = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]
    container2 = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[1]

    if container1.enumerated_values[0].name == "0b00":
        assert container1.usage == expected1
        assert container2.usage == expected2
    elif container1.enumerated_values[0].name == "0b01":
        assert container1.usage == expected2
        assert container2.usage == expected1
    else:
        assert False


def test_value_name_already_defined_same_container(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test verifies the parser's ability to handle situations where duplicate enumerated value names are
    defined within the same `<enumeratedValues>` container. According to best practices, each enumerated value
    within a container should have a unique name to avoid confusion and ensure clarity in register configurations.
    While `svdconv` allows this scenario, issuing only a warning and subsequently ignoring the duplicated
    enumerated value, a robust parser implementation should enforce stricter validation by treating it as an
    error. This approach prevents potential misconfigurations or ambiguity in interpreting register values.

    **Expected Outcome:** The parser should detect the duplicate enumerated value names within the same container and
    raise an error, signaling a violation of the expected naming conventions. Unlike `svdconv`, which issues a
    warning and ignores the conflicting value, the parser should ensure strict enforcement of unique enumerated
    value names within each container, thereby promoting consistency and clear register definitions.

    **Processable with svdconv:** yes
    """

    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("enumerated_values/value_name_already_defined_same_container.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1
    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    enum_container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]
    assert len(enum_container.enumerated_values) == 2
    assert enum_container.enumerated_values[0].name == "0b00"
    assert enum_container.enumerated_values[0].description == "Description for 0b00"
    assert enum_container.enumerated_values[0].value == 0
    assert enum_container.enumerated_values[1].name == "0b01"
    assert enum_container.enumerated_values[1].description == "Description for 0b01"
    assert enum_container.enumerated_values[1].value == 1


def test_value_already_defined(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test assesses the parser's ability to handle scenarios where the same value is defined multiple times
    within an `<enumeratedValues>` container. In an SVD file, each enumerated value should represent a unique
    mapping between a numerical value and its descriptive name to avoid ambiguity. `svdconv` does allow such
    duplicate definitions but issues a warning, and ignores the value. A parser implementation should
    enforce the same behavior.

    **Expected Outcome:** The parser should identify the duplicate values within the `<enumeratedValues>` container
    and raise an error, indicating that multiple enumerations cannot share the same underlying value. Unlike
    `svdconv`, which warns and ignores the value, the parser must enforce uniqueness for each value definition
    within the container to ensure clarity and prevent conflicting interpretations of register settings.

    **Processable with svdconv:** yes
    """

    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("enumerated_values/value_already_defined.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1
    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    enum_container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]
    assert len(enum_container.enumerated_values) == 2
    assert enum_container.enumerated_values[0].name == "0b00"
    assert enum_container.enumerated_values[0].description == "Description for 0b00"
    assert enum_container.enumerated_values[0].value == 0
    assert enum_container.enumerated_values[1].name == "0b01"
    assert enum_container.enumerated_values[1].description == "Description for 0b01"
    assert enum_container.enumerated_values[1].value == 1


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Multiple isDefault",
)
def test_multiple_isdefault(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test examines how the parser handles cases where multiple enumerated values within the same
    `<enumeratedValues>` container are marked as `isDefault`. According to logical interpretation, only one
    enumerated value should be designated as the default, as having multiple defaults would create ambiguity in
    determining which value should be prioritized or used by default. While `svdconv` processes this scenario
    without issuing a warning or error, this behavior appears to be a bug or oversight. A robust parser
    implementation should flag such cases and enforce a rule that only one enumerated value can be marked as
    `isDefault` within a container.

    **Expected Outcome:** The parser should detect when more than one enumerated value is marked as `isDefault` in the
    same container and raise an error to indicate this improper configuration. Unlike `svdconv`, which processes
    the file without complaints, the parser must ensure clarity and consistency by strictly enforcing that only
    one enumerated value can be assigned as the default, preventing potential conflicts or misinterpretations
    during peripheral configuration.

    **Processable with svdconv:** yes
    """

    get_processed_device_from_testfile("enumerated_values/multiple_isdefault.svd")


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_do_not_care_handling(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test verifies how the parser processes enumerated values when specific bits are marked as "do not care."
    In some cases, a bitfield may have multiple possible values where certain bits are irrelevant, meaning they do
    not influence the final behavior of the register. This is commonly represented using wildcards or
    placeholders, and the parser must interpret these "do not care" bits correctly to allow multiple enumerations
    with the same description but different effective values.

    **Expected Outcome:** The parser should accurately interpret and process the "do not care" bits, allowing multiple
    enumerated values that represent different numeric values to share the same logical name and description. This
    results in a list of enumerated values that map distinct values, such as `0x00`, `0x04`, `0x01`, `0x05`, and
    so on, under similar names based on their functional grouping. The parser must handle this scenario without
    confusion or conflicts, ensuring that each enumeration is correctly represented in the output.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile("enumerated_values/do_not_care_handling.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1

    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]

    assert len(container.enumerated_values) == 8

    assert container.enumerated_values[0].name == "0bx00_0"
    assert container.enumerated_values[0].description == "Description for 0bx00"
    assert container.enumerated_values[0].value == 0

    assert container.enumerated_values[1].name == "0bx01_1"
    assert container.enumerated_values[1].description == "Description for 0bx01"
    assert container.enumerated_values[1].value == 1

    assert container.enumerated_values[2].name == "0bx10_2"
    assert container.enumerated_values[2].description == "Description for 0bx10"
    assert container.enumerated_values[2].value == 2

    assert container.enumerated_values[3].name == "0bx11_3"
    assert container.enumerated_values[3].description == "Description for 0bx11"
    assert container.enumerated_values[3].value == 3

    assert container.enumerated_values[4].name == "0bx00_4"
    assert container.enumerated_values[4].description == "Description for 0bx00"
    assert container.enumerated_values[4].value == 4

    assert container.enumerated_values[5].name == "0bx01_5"
    assert container.enumerated_values[5].description == "Description for 0bx01"
    assert container.enumerated_values[5].value == 5

    assert container.enumerated_values[6].name == "0bx10_6"
    assert container.enumerated_values[6].description == "Description for 0bx10"
    assert container.enumerated_values[6].value == 6

    assert container.enumerated_values[7].name == "0bx11_7"
    assert container.enumerated_values[7].description == "Description for 0bx11"
    assert container.enumerated_values[7].value == 7


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_do_not_care_and_distinct_values(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test examines the parser's ability to handle a mix of "do not care" bits and distinct values within a
    single enumerated value container. In certain cases, bitfields may allow specific bits to be ignored or
    treated as irrelevant, while other values must be distinctly recognized. The parser needs to accurately
    interpret these scenarios, grouping together values that share a logical behavior despite differing in
    specific bit positions, while still uniquely identifying distinct values where necessary.

    **Expected Outcome:** The parser should successfully process the test file, correctly handling both "do not care"
    bits and distinct values within the same container. Enumerated values that include wildcard or ignored bits
    should be grouped under the same name and description, such as `0x00` and `0x02`, both treated as `0bx0`.
    Meanwhile, fully distinct values like `0x03` should be uniquely recognized as `0b11`.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile("enumerated_values/do_not_care_and_distinct_values.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1

    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]

    assert len(container.enumerated_values) == 3

    assert container.enumerated_values[0].name == "0bx0_0"
    assert container.enumerated_values[0].description == "Description for 0bx0"
    assert container.enumerated_values[0].value == 0

    assert container.enumerated_values[1].name == "0bx0_2"
    assert container.enumerated_values[1].description == "Description for 0bx0"
    assert container.enumerated_values[1].value == 2

    assert container.enumerated_values[2].name == "0b11"
    assert container.enumerated_values[2].description == "Description for 0b11"
    assert container.enumerated_values[2].value == 3


def test_do_not_care_and_distinct_result_in_same_value(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test focuses on scenarios where a combination of "do not care" bits and distinct enumerated values
    inadvertently leads to the same final value. This can occur when the "do not care" handling allows for
    multiple bit combinations to be interpreted as the same value, but there is also a specific, distinct
    enumerated value defined separately. In such cases, it is essential for the parser to correctly identify and
    handle these overlaps, avoiding unintended duplications.

    **Expected Outcome:** The parser should have the same behavior as `svdconv`, which
    processes the configuration but issues a warning and ignores the second, duplicated value.

    **Processable with svdconv:** yes
    """

    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile(
            "enumerated_values/do_not_care_and_distinct_result_in_same_value.svd"
        )

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1
    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    enum_container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]
    assert len(enum_container.enumerated_values) == 2
    assert enum_container.enumerated_values[0].name == "0bx0_0"
    assert enum_container.enumerated_values[0].description == "Description for 0bx0"
    assert enum_container.enumerated_values[0].value == 0
    assert enum_container.enumerated_values[1].name == "0bx0_2"
    assert enum_container.enumerated_values[1].description == "Description for 0bx0"
    assert enum_container.enumerated_values[1].value == 2


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_default_extension(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test focuses on how parsers should handle `enumeratedValue` elements marked with `isDefault=True`. In
    `svdconv`, such values are parsed without any special processing, essentially ignoring their purpose beyond
    simple recognition. However, according to the CMSIS-SVD standard, `isDefault` should define a name and
    description for all other values that are not explicitly listed. This means a robust parser should extend the
    enumerated values to include all potential values not explicitly defined, using the `isDefault` entry as a
    template.

    **Expected Outcome:** The parser should go beyond `svdconv`'s behavior by automatically identifying all values not
    covered by explicit `enumeratedValue` entries and adding them to the container using the `isDefault`
    description. For example, if the `isDefault` value is defined with a description like "Description for
    default," the parser should generate new entries for every unlisted possible value, appending them to the
    existing list of enumerated values. In this case, the parser should correctly identify that `0b10` is
    explicitly listed, while the values `0`, `1`, and `3` are not. It should then add these values using the
    `isDefault` template, resulting in a complete and exhaustive set of enumerated values, ensuring that any
    unspecified cases are properly accounted for and described, thus enhancing clarity and usability.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile("enumerated_values/default_extension.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1

    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]

    assert len(container.enumerated_values) == 4

    assert container.enumerated_values[0].name == "default_0"
    assert container.enumerated_values[0].description == "Description for default"
    assert container.enumerated_values[0].value == 0

    assert container.enumerated_values[1].name == "default_1"
    assert container.enumerated_values[1].description == "Description for default"
    assert container.enumerated_values[1].value == 1

    assert container.enumerated_values[2].name == "0b10"
    assert container.enumerated_values[2].description == "Description for 0b10"
    assert container.enumerated_values[2].value == 2

    assert container.enumerated_values[3].name == "default_3"
    assert container.enumerated_values[3].description == "Description for default"
    assert container.enumerated_values[3].value == 3


def test_isdefault_with_value(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    The CMSIS-SVD standard specifies that `enumeratedValue` should contain either `isDefault` or `value`, but not
    both simultaneously. However, `svdconv` does not enforce this rule and will not flag cases where both elements
    are present.

    **Expected Outcome:** A robust parser should detect when an `enumeratedValue` entry incorrectly includes both
    `isDefault` and `value`, should ignore the value and raise a warning.

    **Processable with svdconv:** yes
    """

    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("enumerated_values/isdefault_with_value.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1

    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]

    assert len(container.enumerated_values) == 4

    assert container.enumerated_values[0].name == "default_0"
    assert container.enumerated_values[0].description == "Description for default"
    assert container.enumerated_values[0].value == 0

    assert container.enumerated_values[1].name == "default_1"
    assert container.enumerated_values[1].description == "Description for default"
    assert container.enumerated_values[1].value == 1

    assert container.enumerated_values[2].name == "0b10"
    assert container.enumerated_values[2].description == "Description for 0b10"
    assert container.enumerated_values[2].value == 2

    assert container.enumerated_values[3].name == "default_3"
    assert container.enumerated_values[3].description == "Description for default"
    assert container.enumerated_values[3].value == 3
