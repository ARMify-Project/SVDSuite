from typing import Callable
import pytest

from svdsuite.process import ProcessException, ProcessWarning
from svdsuite.model.process import Device, Register, Cluster


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Peripheral naming conflict",
)
def test_peripherals_same_names(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("logical_integrity/peripherals_same_names.svd")


def test_peripherals_same_address(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("logical_integrity/peripherals_same_address.svd")

    assert len(device.peripherals) == 2
    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].base_address == 0x40001000
    assert len(device.peripherals[0].registers_clusters) == 1
    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].base_address == 0x40001000
    assert len(device.peripherals[1].registers_clusters) == 1


def test_peripherals_overlap_address(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("logical_integrity/peripherals_overlap_address.svd")

    assert len(device.peripherals) == 2
    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].base_address == 0x40001000
    assert len(device.peripherals[0].registers_clusters) == 1
    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].base_address == 0x40001500
    assert len(device.peripherals[1].registers_clusters) == 1


def test_different_register_names_in_peripheral(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/different_register_names_in_peripheral.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Register naming conflict",
)
def test_same_register_names_in_peripheral(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("logical_integrity/same_register_names_in_peripheral.svd")


def test_register_and_cluster_register_same_names_in_peripheral(
    get_processed_device_from_testfile: Callable[[str], Device]
):
    device = get_processed_device_from_testfile(
        "logical_integrity/register_and_cluster_register_same_names_in_peripheral.svd"
    )

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
    assert device.peripherals[0].registers_clusters[1].name == "ClusterA"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32

    assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 32


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Register and cluster naming conflict",
)
def test_register_and_cluster_same_names_in_peripheral(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("logical_integrity/register_and_cluster_same_names_in_peripheral.svd")


def test_register_and_nested_cluster_same_names_in_peripheral(
    get_processed_device_from_testfile: Callable[[str], Device]
):
    device = get_processed_device_from_testfile(
        "logical_integrity/register_and_nested_cluster_same_names_in_peripheral.svd"
    )

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
    assert device.peripherals[0].registers_clusters[1].name == "ClusterA"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32

    assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Cluster)
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 32

    assert len(device.peripherals[0].registers_clusters[1].registers_clusters[0].registers_clusters) == 1
    nested_rega = device.peripherals[0].registers_clusters[1].registers_clusters[0].registers_clusters[0]

    assert isinstance(nested_rega, Register)
    assert nested_rega.name == "RegisterA"
    assert nested_rega.address_offset == 0x0
    assert nested_rega.size == 32


def test_same_register_addresses_in_peripheral(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("logical_integrity/same_register_addresses_in_peripheral.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].size == 32


def test_overlap_register_addresses_in_peripheral(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("logical_integrity/overlap_register_addresses_in_peripheral.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x2
    assert device.peripherals[0].registers_clusters[1].size == 16


def test_same_register_cluster_addresses_in_peripheral(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile(
            "logical_integrity/same_register_cluster_addresses_in_peripheral.svd"
        )

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
    assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].size == 32

    assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 32


def test_overlap_register_cluster_addresses_in_peripheral(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile(
            "logical_integrity/overlap_register_cluster_addresses_in_peripheral.svd"
        )

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
    assert device.peripherals[0].registers_clusters[1].name == "ClusterA"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x2
    assert device.peripherals[0].registers_clusters[1].size == 16

    assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x2
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 16


def test_peripheral_sorting(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/peripheral_sorting.svd")

    assert len(device.peripherals) == 4

    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].base_address == 0x40001000

    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].base_address == 0x40002000

    assert device.peripherals[2].name == "PeripheralC"
    assert device.peripherals[2].base_address == 0x40003000

    assert device.peripherals[3].name == "PeripheralD"
    assert device.peripherals[3].base_address == 0x40004000


def test_register_cluster_sorting_in_peripheral(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/register_cluster_sorting_in_peripheral.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
    assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x8
    assert device.peripherals[0].registers_clusters[1].size == 32

    assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[0].registers_clusters[1].size == 32


def test_peripheral_unaligned_address(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("logical_integrity/peripheral_unaligned_address.svd")

    assert len(device.peripherals) == 1
    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].base_address == 0x40001007
    assert device.peripherals[0].size == 8
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 8


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Unaligned registers are not supported",
)
def test_register_unaligned_address(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("logical_integrity/register_unaligned_address.svd")


def test_register_size_bit_width(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("logical_integrity/register_size_bit_width.svd")

    assert len(device.peripherals) == 1
    assert device.peripherals[0].name == "PeripheralB"
    assert device.peripherals[0].base_address == 0x40002000
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32


# TODO add @pytest.mark.filterwarnings("error::ProcessWarning") and for many other tests
def test_alternate_peripheral(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/alternate_peripheral.svd")

    assert len(device.peripherals) == 2
    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].base_address == 0x40001000
    assert device.peripherals[0].alternate_peripheral is None
    assert len(device.peripherals[0].registers_clusters) == 1
    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].base_address == 0x40001000
    assert device.peripherals[1].alternate_peripheral == "PeripheralA"
    assert len(device.peripherals[1].registers_clusters) == 1


def test_alternate_peripheral_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/alternate_peripheral_forward_reference.svd")

    assert len(device.peripherals) == 2
    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].base_address == 0x40001000
    assert device.peripherals[0].alternate_peripheral == "PeripheralB"
    assert len(device.peripherals[0].registers_clusters) == 1
    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].base_address == 0x40001000
    assert device.peripherals[1].alternate_peripheral is None
    assert len(device.peripherals[1].registers_clusters) == 1


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Alternate peripheral has same name as other peripheral",
)
def test_alternate_peripheral_same_name(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("logical_integrity/alternate_peripheral_same_name.svd")


def test_alternate_peripheral_overlap(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/alternate_peripheral_overlap.svd")

    assert len(device.peripherals) == 2
    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].base_address == 0x40001000
    assert device.peripherals[0].alternate_peripheral is None
    assert len(device.peripherals[0].registers_clusters) == 1
    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].base_address == 0x40001500
    assert device.peripherals[1].alternate_peripheral == "PeripheralA"
    assert len(device.peripherals[1].registers_clusters) == 1


def test_alternate_peripheral_multiple(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/alternate_peripheral_multiple.svd")

    assert len(device.peripherals) == 3

    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].base_address == 0x40001000
    assert device.peripherals[0].alternate_peripheral is None
    assert len(device.peripherals[0].registers_clusters) == 1

    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].base_address == 0x40001000
    assert device.peripherals[1].alternate_peripheral == "PeripheralA"
    assert len(device.peripherals[1].registers_clusters) == 1

    assert device.peripherals[2].name == "PeripheralC"
    assert device.peripherals[2].base_address == 0x40001000
    assert device.peripherals[2].alternate_peripheral == "PeripheralA"
    assert len(device.peripherals[2].registers_clusters) == 1


def test_alternate_peripheral_multiple_svdconv_warning(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/alternate_peripheral_multiple_svdconv_warning.svd")

    assert len(device.peripherals) == 4

    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].base_address == 0x40001000
    assert device.peripherals[0].alternate_peripheral is None
    assert len(device.peripherals[0].registers_clusters) == 1

    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].base_address == 0x40001000
    assert device.peripherals[1].alternate_peripheral == "PeripheralA"
    assert len(device.peripherals[1].registers_clusters) == 1

    assert device.peripherals[2].name == "PeripheralC"
    assert device.peripherals[2].base_address == 0x40001000
    assert device.peripherals[2].alternate_peripheral == "PeripheralA"
    assert len(device.peripherals[2].registers_clusters) == 1

    assert device.peripherals[3].name == "PeripheralD"
    assert device.peripherals[3].base_address == 0x40001000
    assert device.peripherals[3].alternate_peripheral == "PeripheralC"
    assert len(device.peripherals[3].registers_clusters) == 1


def test_alternate_register(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/alternate_register.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert device.peripherals[0].registers_clusters[0].alternate_register is None

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert device.peripherals[0].registers_clusters[1].alternate_register == "RegisterA"


def test_alternate_register_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/alternate_register_forward_reference.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert device.peripherals[0].registers_clusters[0].alternate_register == "RegisterB"

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert device.peripherals[0].registers_clusters[1].alternate_register is None


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Alternate register has same name as other register",
)
def test_alternate_register_same_name(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("logical_integrity/alternate_register_same_name.svd")


def test_alternate_register_overlap(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/alternate_register_overlap.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert device.peripherals[0].registers_clusters[0].alternate_register is None

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x2
    assert device.peripherals[0].registers_clusters[1].size == 16
    assert device.peripherals[0].registers_clusters[1].alternate_register == "RegisterA"


def test_alternate_register_multiple(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/alternate_register_multiple.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 4

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert device.peripherals[0].registers_clusters[0].alternate_register is None

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert device.peripherals[0].registers_clusters[1].alternate_register == "RegisterA"

    assert isinstance(device.peripherals[0].registers_clusters[2], Register)
    assert device.peripherals[0].registers_clusters[2].name == "RegisterC"
    assert device.peripherals[0].registers_clusters[2].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[2].size == 32
    assert device.peripherals[0].registers_clusters[2].alternate_register == "RegisterA"

    assert isinstance(device.peripherals[0].registers_clusters[3], Register)
    assert device.peripherals[0].registers_clusters[3].name == "RegisterD"
    assert device.peripherals[0].registers_clusters[3].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[3].size == 32
    assert device.peripherals[0].registers_clusters[3].alternate_register == "RegisterC"


def test_alternate_cluster(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/alternate_cluster.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
    assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert device.peripherals[0].registers_clusters[0].alternate_cluster is None

    assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
    assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert device.peripherals[0].registers_clusters[1].alternate_cluster == "ClusterA"


def test_alternate_cluster_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/alternate_cluster_forward_reference.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
    assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert device.peripherals[0].registers_clusters[0].alternate_cluster == "ClusterB"

    assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
    assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert device.peripherals[0].registers_clusters[1].alternate_cluster is None


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Alternate cluster has same name as other cluster",
)
def test_alternate_cluster_same_name(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("logical_integrity/alternate_cluster_same_name.svd")


def test_alternate_cluster_overlap(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/alternate_cluster_overlap.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
    assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert device.peripherals[0].registers_clusters[0].alternate_cluster is None

    assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
    assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x2
    assert device.peripherals[0].registers_clusters[1].size == 16
    assert device.peripherals[0].registers_clusters[1].alternate_cluster == "ClusterA"


def test_alternate_cluster_multiple(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/alternate_cluster_multiple.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 4

    assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
    assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert device.peripherals[0].registers_clusters[0].alternate_cluster is None

    assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
    assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert device.peripherals[0].registers_clusters[1].alternate_cluster == "ClusterA"

    assert isinstance(device.peripherals[0].registers_clusters[2], Cluster)
    assert device.peripherals[0].registers_clusters[2].name == "ClusterC"
    assert device.peripherals[0].registers_clusters[2].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[2].size == 32
    assert device.peripherals[0].registers_clusters[2].alternate_cluster == "ClusterA"

    assert isinstance(device.peripherals[0].registers_clusters[3], Cluster)
    assert device.peripherals[0].registers_clusters[3].name == "ClusterD"
    assert device.peripherals[0].registers_clusters[3].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[3].size == 32
    assert device.peripherals[0].registers_clusters[3].alternate_cluster == "ClusterC"


def test_register_alternate_group(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/register_alternate_group.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 3

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert device.peripherals[0].registers_clusters[0].alternate_group is None

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterA_RegisterX"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert device.peripherals[0].registers_clusters[1].alternate_group == "RegisterX"

    assert isinstance(device.peripherals[0].registers_clusters[2], Register)
    assert device.peripherals[0].registers_clusters[2].name == "RegisterB_RegisterX"
    assert device.peripherals[0].registers_clusters[2].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[2].size == 32
    assert device.peripherals[0].registers_clusters[2].alternate_group == "RegisterX"


def test_register_alternate_group_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/register_alternate_group_forward_reference.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 3

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA_RegisterX"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert device.peripherals[0].registers_clusters[0].alternate_group == "RegisterX"

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB_RegisterX"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert device.peripherals[0].registers_clusters[1].alternate_group == "RegisterX"

    assert isinstance(device.peripherals[0].registers_clusters[2], Register)
    assert device.peripherals[0].registers_clusters[2].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[2].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[2].size == 32
    assert device.peripherals[0].registers_clusters[2].alternate_group is None


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Register in alternate group has same name as other register in same alternate group",
)
def test_register_alternate_group_same_name(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("logical_integrity/register_alternate_group_same_name.svd")


def test_register_alternate_group_overlap(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/register_alternate_group_overlap.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 3

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert device.peripherals[0].registers_clusters[0].alternate_group is None

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterA_RegisterX"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].size == 16
    assert device.peripherals[0].registers_clusters[1].alternate_group == "RegisterX"

    assert isinstance(device.peripherals[0].registers_clusters[2], Register)
    assert device.peripherals[0].registers_clusters[2].name == "RegisterB_RegisterX"
    assert device.peripherals[0].registers_clusters[2].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[2].size == 32
    assert device.peripherals[0].registers_clusters[2].alternate_group == "RegisterX"


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Field has same name as other field",
)
def test_fields_same_names(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("logical_integrity/fields_same_names.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Field overlaps other field",
)
def test_fields_same_bit_offset(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("logical_integrity/fields_same_bit_offset.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Field overlaps other field",
)
def test_fields_overlap_bit_offset(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("logical_integrity/fields_overlap_bit_offset.svd")


def test_field_bit_range_processing(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("logical_integrity/field_bit_range_processing.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 3

    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 3

    assert device.peripherals[0].registers_clusters[0].fields[1].name == "FieldB"
    assert device.peripherals[0].registers_clusters[0].fields[1].lsb == 4
    assert device.peripherals[0].registers_clusters[0].fields[1].msb == 7

    assert device.peripherals[0].registers_clusters[0].fields[2].name == "FieldC"
    assert device.peripherals[0].registers_clusters[0].fields[2].lsb == 8
    assert device.peripherals[0].registers_clusters[0].fields[2].msb == 11


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Wrong string in bitRangePattern",
)
def test_field_wrong_string_in_bitrangepattern(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("logical_integrity/field_wrong_string_in_bitrangepattern.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="LSB > MSB",
)
def test_field_illogical_values_in_bitrangepattern(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("logical_integrity/field_illogical_values_in_bitrangepattern.svd")


def test_ignore_empty_peripheral(get_processed_device_from_testfile: Callable[[str], Device]):
    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("logical_integrity/ignore_empty_peripheral.svd")

    assert len(device.peripherals) == 2

    assert device.peripherals[0].name == "PeripheralA"
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"

    assert device.peripherals[1].name == "PeripheralC"
    assert len(device.peripherals[1].registers_clusters) == 1
    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
