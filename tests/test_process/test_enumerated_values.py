from typing import Callable
import pytest

from svdsuite.process import Process, ProcessException
from svdsuite.model.process import Device, IRegister
from svdsuite.model.types import EnumUsageType


def test_simple_read_write(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("enumerated_values/simple_read_write.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1

    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]
    assert container.name == "FieldAEnumeratedValue"
    assert container.usage == EnumUsageType.READ_WRITE
    assert len(container.enumerated_values) == 4

    assert container.enumerated_values[0].name == "0b00"
    assert container.enumerated_values[0].description == "Description for 0b00"
    assert container.enumerated_values[0].value == 0b00
    assert container.enumerated_values[0].is_default is False

    assert container.enumerated_values[1].name == "0b01"
    assert container.enumerated_values[1].description == "Description for 0b01"
    assert container.enumerated_values[1].value == 0b01
    assert container.enumerated_values[1].is_default is False

    assert container.enumerated_values[2].name == "0b10"
    assert container.enumerated_values[2].description == "Description for 0b10"
    assert container.enumerated_values[2].value == 0b10
    assert container.enumerated_values[2].is_default is False

    assert container.enumerated_values[3].name == "0b11"
    assert container.enumerated_values[3].description == "Description for 0b11"
    assert container.enumerated_values[3].value == 0b11
    assert container.enumerated_values[3].is_default is False


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Too many <enumeratedValues> container specified",
)
def test_three_containers(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("enumerated_values/three_containers.svd")


def test_default_usage(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("enumerated_values/default_usage.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1

    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]
    assert container.name == "FieldAEnumeratedValue"
    assert container.usage == EnumUsageType.READ_WRITE


@pytest.mark.parametrize(
    "first_input,second_input,expected1,expected2",
    [
        pytest.param("read", "write", EnumUsageType.READ, EnumUsageType.WRITE),
        pytest.param("write", "read", EnumUsageType.WRITE, EnumUsageType.READ),
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
    file_name = "enumerated_values/usage_combinations.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"FIRST_INPUT", first_input.encode())
    file_content = file_content.replace(b"SECOND_INPUT", second_input.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
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


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Value name already defined in container",
)
def test_value_name_already_defined_same_container(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("enumerated_values/value_name_already_defined_same_container.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Value already defined in container",
)
def test_value_already_defined(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("enumerated_values/value_already_defined.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Multiple isDefault",
)
def test_multiple_isdefault(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("enumerated_values/multiple_isdefault.svd")


def test_do_not_care_handling(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("enumerated_values/do_not_care_handling.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1

    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]

    assert len(container.enumerated_values) == 8

    assert container.enumerated_values[0].name == "0bx00_0"
    assert container.enumerated_values[0].description == "Description for 0bx00"
    assert container.enumerated_values[0].value == 0
    assert container.enumerated_values[0].is_default is False

    assert container.enumerated_values[1].name == "0bx01_1"
    assert container.enumerated_values[1].description == "Description for 0bx01"
    assert container.enumerated_values[1].value == 1
    assert container.enumerated_values[1].is_default is False

    assert container.enumerated_values[2].name == "0bx10_2"
    assert container.enumerated_values[2].description == "Description for 0bx10"
    assert container.enumerated_values[2].value == 2
    assert container.enumerated_values[2].is_default is False

    assert container.enumerated_values[3].name == "0bx11_3"
    assert container.enumerated_values[3].description == "Description for 0bx11"
    assert container.enumerated_values[3].value == 3
    assert container.enumerated_values[3].is_default is False

    assert container.enumerated_values[4].name == "0bx00_4"
    assert container.enumerated_values[4].description == "Description for 0bx00"
    assert container.enumerated_values[4].value == 4
    assert container.enumerated_values[4].is_default is False

    assert container.enumerated_values[5].name == "0bx01_5"
    assert container.enumerated_values[5].description == "Description for 0bx01"
    assert container.enumerated_values[5].value == 5
    assert container.enumerated_values[5].is_default is False

    assert container.enumerated_values[6].name == "0bx10_6"
    assert container.enumerated_values[6].description == "Description for 0bx10"
    assert container.enumerated_values[6].value == 6
    assert container.enumerated_values[6].is_default is False

    assert container.enumerated_values[7].name == "0bx11_7"
    assert container.enumerated_values[7].description == "Description for 0bx11"
    assert container.enumerated_values[7].value == 7
    assert container.enumerated_values[7].is_default is False


def test_do_not_care_and_distinct_values(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("enumerated_values/do_not_care_and_distinct_values.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1

    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]

    assert len(container.enumerated_values) == 3

    assert container.enumerated_values[0].name == "0bx0_0"
    assert container.enumerated_values[0].description == "Description for 0bx0"
    assert container.enumerated_values[0].value == 0
    assert container.enumerated_values[0].is_default is False

    assert container.enumerated_values[1].name == "0bx0_2"
    assert container.enumerated_values[1].description == "Description for 0bx0"
    assert container.enumerated_values[1].value == 2
    assert container.enumerated_values[1].is_default is False

    assert container.enumerated_values[2].name == "0b11"
    assert container.enumerated_values[2].description == "Description for 0b11"
    assert container.enumerated_values[2].value == 3
    assert container.enumerated_values[2].is_default is False


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Value already defined in container",
)
def test_do_not_care_and_distinct_result_in_same_value(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("enumerated_values/do_not_care_and_distinct_result_in_same_value.svd")


def test_default_extension(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("enumerated_values/default_extension.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1

    assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    container = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]

    assert len(container.enumerated_values) == 4

    assert container.enumerated_values[0].name == "default_0"
    assert container.enumerated_values[0].description == "Description for default"
    assert container.enumerated_values[0].value == 0
    assert container.enumerated_values[0].is_default is False

    assert container.enumerated_values[1].name == "default_1"
    assert container.enumerated_values[1].description == "Description for default"
    assert container.enumerated_values[1].value == 1
    assert container.enumerated_values[1].is_default is False

    assert container.enumerated_values[2].name == "0b10"
    assert container.enumerated_values[2].description == "Description for 0b10"
    assert container.enumerated_values[2].value == 2
    assert container.enumerated_values[2].is_default is False

    assert container.enumerated_values[3].name == "default_3"
    assert container.enumerated_values[3].description == "Description for default"
    assert container.enumerated_values[3].value == 3
    assert container.enumerated_values[3].is_default is False


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="isDefault must not have a value",
)
def test_isdefault_with_value(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("enumerated_values/isdefault_with_value.svd")
