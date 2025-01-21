from typing import Callable
import pytest

from svdsuite.process import ProcessException
from svdsuite.model.process import Device, IRegister, ICluster


def test_simple_array_peripheral_level(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("dim_handling/simple_array_peripheral_level.svd")

    assert len(device.peripherals) == 2

    assert device.peripherals[0].name == "Peripheral0"
    assert device.peripherals[0].base_address == 0x40001000
    assert device.peripherals[0].size == 32
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1], IRegister)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32

    assert device.peripherals[1].name == "Peripheral1"
    assert device.peripherals[1].base_address == 0x40002000
    assert device.peripherals[1].size == 32
    assert len(device.peripherals[1].registers_clusters) == 2

    assert isinstance(device.peripherals[1].registers_clusters[0], IRegister)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[1].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[1].registers_clusters[1], IRegister)
    assert device.peripherals[1].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[1].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[1].registers_clusters[1].size == 32


def test_simple_array_cluster_level(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("dim_handling/simple_array_cluster_level.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], ICluster)
    assert device.peripherals[0].registers_clusters[0].name == "Cluster0"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], IRegister)
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[1], IRegister)
    assert device.peripherals[0].registers_clusters[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[0].registers_clusters[1].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1], ICluster)
    assert device.peripherals[0].registers_clusters[1].name == "Cluster1"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x8
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], IRegister)
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[1], IRegister)
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].size == 32


def test_simple_array_register_level(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("dim_handling/simple_array_register_level.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
    assert device.peripherals[0].registers_clusters[0].name == "Register0"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1], IRegister)
    assert device.peripherals[0].registers_clusters[1].name == "Register1"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Field cannot be an array",
)
def test_simple_array_field_level(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("dim_handling/simple_array_field_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Peripheral cannot be a list",
)
def test_simple_list_peripheral_level(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("dim_handling/simple_list_peripheral_level.svd")


def test_simple_list_cluster_level(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("dim_handling/simple_list_cluster_level.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], ICluster)
    assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], IRegister)
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[1], IRegister)
    assert device.peripherals[0].registers_clusters[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[0].registers_clusters[1].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1], ICluster)
    assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x8
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], IRegister)
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[1], IRegister)
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].size == 32


def test_simple_list_register_level(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("dim_handling/simple_list_register_level.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 13

    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
    assert device.peripherals[0].registers_clusters[0].name == "Register0"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1], IRegister)
    assert device.peripherals[0].registers_clusters[1].name == "Register1"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[2], IRegister)
    assert device.peripherals[0].registers_clusters[2].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[2].address_offset == 0x8
    assert device.peripherals[0].registers_clusters[2].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[3], IRegister)
    assert device.peripherals[0].registers_clusters[3].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[3].address_offset == 0xC
    assert device.peripherals[0].registers_clusters[3].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[4], IRegister)
    assert device.peripherals[0].registers_clusters[4].name == "Register2"
    assert device.peripherals[0].registers_clusters[4].address_offset == 0x10
    assert device.peripherals[0].registers_clusters[4].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[5], IRegister)
    assert device.peripherals[0].registers_clusters[5].name == "Register3"
    assert device.peripherals[0].registers_clusters[5].address_offset == 0x14
    assert device.peripherals[0].registers_clusters[5].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[6], IRegister)
    assert device.peripherals[0].registers_clusters[6].name == "Register4"
    assert device.peripherals[0].registers_clusters[6].address_offset == 0x18
    assert device.peripherals[0].registers_clusters[6].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[7], IRegister)
    assert device.peripherals[0].registers_clusters[7].name == "RegisterC"
    assert device.peripherals[0].registers_clusters[7].address_offset == 0x1C
    assert device.peripherals[0].registers_clusters[7].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[8], IRegister)
    assert device.peripherals[0].registers_clusters[8].name == "RegisterD"
    assert device.peripherals[0].registers_clusters[8].address_offset == 0x20
    assert device.peripherals[0].registers_clusters[8].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[9], IRegister)
    assert device.peripherals[0].registers_clusters[9].name == "RegisterE"
    assert device.peripherals[0].registers_clusters[9].address_offset == 0x24
    assert device.peripherals[0].registers_clusters[9].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[10], IRegister)
    assert device.peripherals[0].registers_clusters[10].name == "RegisterF"
    assert device.peripherals[0].registers_clusters[10].address_offset == 0x28
    assert device.peripherals[0].registers_clusters[10].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[11], IRegister)
    assert device.peripherals[0].registers_clusters[11].name == "RegisterG"
    assert device.peripherals[0].registers_clusters[11].address_offset == 0x2C
    assert device.peripherals[0].registers_clusters[11].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[12], IRegister)
    assert device.peripherals[0].registers_clusters[12].name == "RegisterH"
    assert device.peripherals[0].registers_clusters[12].address_offset == 0x30
    assert device.peripherals[0].registers_clusters[12].size == 32


def test_simple_list_field_level(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("dim_handling/simple_list_field_level.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1

    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 2

    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 1

    assert device.peripherals[0].registers_clusters[0].fields[1].name == "FieldB"
    assert device.peripherals[0].registers_clusters[0].fields[1].lsb == 2
    assert device.peripherals[0].registers_clusters[0].fields[1].msb == 3


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Found dim-array in name without dim",
)
def test_dim_array_without_dim_peripheral_level(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("dim_handling/dim_array_without_dim_peripheral_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Found dim-array in name without dim",
)
def test_dim_array_without_dim_cluster_level(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("dim_handling/dim_array_without_dim_cluster_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Found dim-array in name without dim",
)
def test_dim_array_without_dim_register_level(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("dim_handling/dim_array_without_dim_register_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Found dim-list in name without dim",
)
def test_dim_list_without_dim_cluster_level(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("dim_handling/dim_list_without_dim_cluster_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Found dim-list in name without dim",
)
def test_dim_list_without_dim_register_level(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("dim_handling/dim_list_without_dim_register_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Found dim-list in name without dim",
)
def test_dim_list_without_dim_field_level(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("dim_handling/dim_list_without_dim_field_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Number of <dimIndex> Elements is different to number of <dim> instances",
)
def test_dim_list_wrong_dimindex_cluster_level(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("dim_handling/dim_list_wrong_dimindex_cluster_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Number of <dimIndex> Elements is different to number of <dim> instances",
)
def test_dim_list_wrong_dimindex_register_level(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("dim_handling/dim_list_wrong_dimindex_register_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Number of <dimIndex> Elements is different to number of <dim> instances",
)
def test_dim_list_wrong_dimindex_field_level(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("dim_handling/dim_list_wrong_dimindex_field_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Number of <dimIndex> Elements is different to number of <dim> instances",
)
def test_wrong_dimindex_svdconv_bug(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("dim_handling/wrong_dimindex_svdconv_bug.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="dimIndex from first dim and dimIndex from second dim contain same value, leading to same register name",
)
def test_two_dim_resulting_in_same_name(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("dim_handling/two_dim_resulting_in_same_name.svd")


def test_array_displayname_with_dim(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("dim_handling/array_displayname_with_dim.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
    assert device.peripherals[0].registers_clusters[0].name == "Register0"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert device.peripherals[0].registers_clusters[0].display_name == "Register0"

    assert isinstance(device.peripherals[0].registers_clusters[1], IRegister)
    assert device.peripherals[0].registers_clusters[1].name == "Register1"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert device.peripherals[0].registers_clusters[1].display_name == "Register1"


def test_list_displayname_with_dim(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("dim_handling/list_displayname_with_dim.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], IRegister)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert device.peripherals[0].registers_clusters[0].display_name == "RegisterA"

    assert isinstance(device.peripherals[0].registers_clusters[1], IRegister)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert device.peripherals[0].registers_clusters[1].display_name == "RegisterB"


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Expression marker [%s] found in displayName but no <dim> specified",
)
def test_array_displayname_without_dim(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("dim_handling/array_displayname_without_dim.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Expression marker [%s] found in displayName but no <dim> specified",
)
def test_list_displayname_without_dim(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("dim_handling/list_displayname_without_dim.svd")
