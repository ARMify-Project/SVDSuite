from typing import Callable
import pytest

from svdsuite.process import Process, ProcessException, ProcessWarning
from svdsuite.model.process import Device, Register, Cluster
from svdsuite.model.types import (
    AccessType,
    EnumUsageType,
    ProtectionStringType,
    EnumeratedTokenType,
    DataTypeType,
    ModifiedWriteValuesType,
    ReadActionType,
)


@pytest.fixture(name="get_processed_device_from_testfile")
def fixture_get_processed_device_from_testfile(get_test_svd_file_content: Callable[[str], bytes]):
    def _(file_name: str) -> Device:
        file_content = get_test_svd_file_content(file_name)
        return Process.from_xml_content(file_content).get_processed_device()

    return _


class TestApplicationOfDefaultValues:
    def test_default_register_properties_on_device_level(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
        device = get_processed_device_from_testfile(
            "application_of_default_values/default_register_properties_on_device_level.svd"
        )

        assert device.size == 32
        assert device.access == AccessType.READ_WRITE
        assert device.protection == ProtectionStringType.ANY
        assert device.reset_value == 0x0
        assert device.reset_mask == 0xFFFFFFFF

    def test_custom_register_properties_on_device_level(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
        device = get_processed_device_from_testfile(
            "application_of_default_values/custom_register_properties_on_device_level.svd"
        )

        assert device.size == 16
        assert device.access == AccessType.WRITE_ONLY
        assert device.protection == ProtectionStringType.SECURE
        assert device.reset_value == 0xDEADBEEF
        assert device.reset_mask == 0xDEADC0DE


class TestLogicalIntegrity:
    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Peripheral naming conflict",
    )
    def test_peripherals_same_names(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("logical_integrity/peripherals_same_names.svd")

    def test_peripherals_same_address(self, get_processed_device_from_testfile: Callable[[str], Device]):
        with pytest.warns(ProcessWarning):
            device = get_processed_device_from_testfile("logical_integrity/peripherals_same_address.svd")

        assert len(device.peripherals) == 2
        assert device.peripherals[0].name == "PeripheralA"
        assert device.peripherals[0].base_address == 0x40001000
        assert len(device.peripherals[0].registers_clusters) == 1
        assert device.peripherals[1].name == "PeripheralB"
        assert device.peripherals[1].base_address == 0x40001000
        assert len(device.peripherals[1].registers_clusters) == 1

    def test_peripherals_overlap_address(self, get_processed_device_from_testfile: Callable[[str], Device]):
        with pytest.warns(ProcessWarning):
            device = get_processed_device_from_testfile("logical_integrity/peripherals_overlap_address.svd")

        assert len(device.peripherals) == 2
        assert device.peripherals[0].name == "PeripheralA"
        assert device.peripherals[0].base_address == 0x40001000
        assert len(device.peripherals[0].registers_clusters) == 1
        assert device.peripherals[1].name == "PeripheralB"
        assert device.peripherals[1].base_address == 0x40001500
        assert len(device.peripherals[1].registers_clusters) == 1

    def test_different_register_names_in_peripheral(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
    def test_same_register_names_in_peripheral(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("logical_integrity/same_register_names_in_peripheral.svd")

    def test_register_and_cluster_register_same_names_in_peripheral(
        self, get_processed_device_from_testfile: Callable[[str], Device]
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
    def test_register_and_cluster_same_names_in_peripheral(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
        get_processed_device_from_testfile("logical_integrity/register_and_cluster_same_names_in_peripheral.svd")

    def test_register_and_nested_cluster_same_names_in_peripheral(
        self, get_processed_device_from_testfile: Callable[[str], Device]
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

    def test_same_register_addresses_in_peripheral(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_overlap_register_addresses_in_peripheral(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
        with pytest.warns(ProcessWarning):
            device = get_processed_device_from_testfile(
                "logical_integrity/overlap_register_addresses_in_peripheral.svd"
            )

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

    def test_same_register_cluster_addresses_in_peripheral(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
        with pytest.warns(ProcessWarning):
            device = get_processed_device_from_testfile(
                "logical_integrity/same_register_cluster_addresses_in_peripheral.svd"
            )

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
        assert device.peripherals[0].registers_clusters[1].name == "ClusterA"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].size == 32

        assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterB"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 32

    def test_overlap_register_cluster_addresses_in_peripheral(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
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

    def test_peripheral_sorting(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_register_cluster_sorting_in_peripheral(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_peripheral_unaligned_address(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
    def test_register_unaligned_address(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("logical_integrity/register_unaligned_address.svd")

    def test_register_size_bit_width(self, get_processed_device_from_testfile: Callable[[str], Device]):
        with pytest.warns(ProcessWarning):
            device = get_processed_device_from_testfile("logical_integrity/register_size_bit_width.svd")

        assert len(device.peripherals) == 1
        assert device.peripherals[0].name == "PeripheralA"
        assert device.peripherals[0].base_address == 0x40001000
        assert len(device.peripherals[0].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 23

    def test_alternate_peripheral(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_alternate_peripheral_forward_reference(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
    def test_alternate_peripheral_same_name(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("logical_integrity/alternate_peripheral_same_name.svd")

    def test_alternate_peripheral_overlap(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_alternate_peripheral_multiple(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_alternate_peripheral_multiple_svdconv_warning(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
        device = get_processed_device_from_testfile(
            "logical_integrity/alternate_peripheral_multiple_svdconv_warning.svd"
        )

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

    def test_alternate_register(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_alternate_register_forward_reference(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
    def test_alternate_register_same_name(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("logical_integrity/alternate_register_same_name.svd")

    def test_alternate_register_overlap(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_alternate_register_multiple(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_alternate_cluster(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_alternate_cluster_forward_reference(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
    def test_alternate_cluster_same_name(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("logical_integrity/alternate_cluster_same_name.svd")

    def test_alternate_cluster_overlap(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_alternate_cluster_multiple(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_register_alternate_group(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_register_alternate_group_forward_reference(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
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
    def test_register_alternate_group_same_name(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("logical_integrity/register_alternate_group_same_name.svd")

    def test_register_alternate_group_overlap(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
    def test_fields_same_names(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("logical_integrity/fields_same_names.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Field overlaps other field",
    )
    def test_fields_same_bit_offset(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("logical_integrity/fields_same_bit_offset.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Field overlaps other field",
    )
    def test_fields_overlap_bit_offset(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("logical_integrity/fields_overlap_bit_offset.svd")

    def test_field_bit_range_processing(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
    def test_field_wrong_string_in_bitrangepattern(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("logical_integrity/field_wrong_string_in_bitrangepattern.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="LSB > MSB",
    )
    def test_field_illogical_values_in_bitrangepattern(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
        get_processed_device_from_testfile("logical_integrity/field_illogical_values_in_bitrangepattern.svd")


class TestSizeInheritanceAndAdjustment:
    def test_simple_size_adjustment(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("size_inheritance_and_adjustment/simple_size_adjustment.svd")

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2
        assert device.peripherals[0].size == 64  # explicitly set to 16, adjustment overwrite to 64

        assert isinstance(device.peripherals[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 64  # not set, effective size results in 64

        assert isinstance(device.peripherals[0].registers_clusters[1], Register)
        assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x8
        assert device.peripherals[0].registers_clusters[1].size == 64  # explicitly set to 64

    def test_complex_size_adjustment(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("size_inheritance_and_adjustment/complex_size_adjustment.svd")

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 3

        cluster_a = device.peripherals[0].registers_clusters[0]
        assert isinstance(cluster_a, Cluster)
        assert cluster_a.name == "ClusterA"
        assert cluster_a.address_offset == 0x0
        assert cluster_a.size == 64  # not set, size adjustment results in 64 from ClusterB
        assert len(cluster_a.registers_clusters) == 3

        assert isinstance(cluster_a.registers_clusters[0], Register)
        assert cluster_a.registers_clusters[0].name == "RegisterA"
        assert cluster_a.registers_clusters[0].address_offset == 0x0
        assert cluster_a.registers_clusters[0].size == 64  # not set, effective size results in 64 from ClusterA

        assert isinstance(cluster_a.registers_clusters[1], Register)
        assert cluster_a.registers_clusters[1].name == "RegisterB"
        assert cluster_a.registers_clusters[1].address_offset == 0x8
        assert cluster_a.registers_clusters[1].size == 64  # not set, effective size results in 64 from ClusterA

        cluster_b = cluster_a.registers_clusters[2]
        assert isinstance(cluster_b, Cluster)
        assert cluster_b.name == "ClusterB"
        assert cluster_b.address_offset == 0xC
        assert cluster_b.size == 64  # not set, size adjustment results in 64 from RegisterB
        assert len(cluster_b.registers_clusters) == 2

        assert isinstance(cluster_b.registers_clusters[0], Register)
        assert cluster_b.registers_clusters[0].name == "RegisterA"
        assert cluster_b.registers_clusters[0].address_offset == 0x0
        assert cluster_b.registers_clusters[0].size == 64  # not set, effective size results in 64 from ClusterB

        assert isinstance(cluster_b.registers_clusters[1], Register)
        assert cluster_b.registers_clusters[1].name == "RegisterB"
        assert cluster_b.registers_clusters[1].address_offset == 0x8
        assert cluster_b.registers_clusters[1].size == 64  # explicitly set to 64

        cluster_c = device.peripherals[0].registers_clusters[1]
        assert isinstance(cluster_c, Cluster)
        assert cluster_c.name == "ClusterC"
        assert cluster_c.address_offset == 0x1C
        assert cluster_c.size == 32  # not set, size adjustment results implicit in 32 from RegisterA and RegisterB
        assert len(cluster_c.registers_clusters) == 2

        assert isinstance(cluster_c.registers_clusters[0], Register)
        assert cluster_c.registers_clusters[0].name == "RegisterA"
        assert cluster_c.registers_clusters[0].address_offset == 0x0
        assert cluster_c.registers_clusters[0].size == 32  # not set, effective size results in 32 from ClusterC size

        assert isinstance(cluster_c.registers_clusters[1], Register)
        assert cluster_c.registers_clusters[1].name == "RegisterB"
        assert cluster_c.registers_clusters[1].address_offset == 0x8
        assert cluster_c.registers_clusters[1].size == 32  # not set, effective size results in 32 from ClusterC size

        assert isinstance(device.peripherals[0].registers_clusters[2], Register)
        assert device.peripherals[0].registers_clusters[2].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[2].address_offset == 0x2C
        assert device.peripherals[0].registers_clusters[2].size == 64  # not set, ef. size results in 64 from peripheral

    def test_overlap_due_to_size_adjustment(self, get_processed_device_from_testfile: Callable[[str], Device]):
        with pytest.warns(ProcessWarning):
            device = get_processed_device_from_testfile(
                "size_inheritance_and_adjustment/overlap_due_to_size_adjustment.svd"
            )

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2
        assert device.peripherals[0].size == 64  # explicitly set to 32, adjustment overwrite to 64 from RegisterB

        assert isinstance(device.peripherals[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 64  # not set, ef. size results in 64 (PeripheralA)

        assert isinstance(device.peripherals[0].registers_clusters[1], Register)
        assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].size == 64  # explicitly set to 64


class TestDimHandling:
    def test_simple_array_peripheral_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("dim_handling/simple_array_peripheral_level.svd")

        assert len(device.peripherals) == 2

        assert device.peripherals[0].name == "Peripheral0"
        assert device.peripherals[0].base_address == 0x40001000
        assert device.peripherals[0].size == 32
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[1], Register)
        assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].size == 32

        assert device.peripherals[1].name == "Peripheral1"
        assert device.peripherals[1].base_address == 0x40002000
        assert device.peripherals[1].size == 32
        assert len(device.peripherals[1].registers_clusters) == 2

        assert isinstance(device.peripherals[1].registers_clusters[0], Register)
        assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[1].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[1].registers_clusters[1], Register)
        assert device.peripherals[1].registers_clusters[1].name == "RegisterB"
        assert device.peripherals[1].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[1].registers_clusters[1].size == 32

    def test_simple_array_cluster_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("dim_handling/simple_array_cluster_level.svd")

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "Cluster0"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[1], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[1].name == "RegisterB"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[0].registers_clusters[1].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
        assert device.peripherals[0].registers_clusters[1].name == "Cluster1"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x8
        assert device.peripherals[0].registers_clusters[1].size == 32
        assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[1], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].name == "RegisterB"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].size == 32

    def test_simple_array_register_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("dim_handling/simple_array_register_level.svd")

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].name == "Register0"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[1], Register)
        assert device.peripherals[0].registers_clusters[1].name == "Register1"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].size == 32

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Field cannot be an array",
    )
    def test_simple_array_field_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("dim_handling/simple_array_field_level.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Peripheral cannot be a list",
    )
    def test_simple_list_peripheral_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("dim_handling/simple_list_peripheral_level.svd")

    def test_simple_list_cluster_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("dim_handling/simple_list_cluster_level.svd")

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[1], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[1].name == "RegisterB"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[0].registers_clusters[1].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
        assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x8
        assert device.peripherals[0].registers_clusters[1].size == 32
        assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[1], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].name == "RegisterB"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].size == 32

    def test_simple_list_register_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("dim_handling/simple_list_register_level.svd")

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 13

        assert isinstance(device.peripherals[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].name == "Register0"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[1], Register)
        assert device.peripherals[0].registers_clusters[1].name == "Register1"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[2], Register)
        assert device.peripherals[0].registers_clusters[2].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[2].address_offset == 0x8
        assert device.peripherals[0].registers_clusters[2].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[3], Register)
        assert device.peripherals[0].registers_clusters[3].name == "RegisterB"
        assert device.peripherals[0].registers_clusters[3].address_offset == 0xC
        assert device.peripherals[0].registers_clusters[3].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[4], Register)
        assert device.peripherals[0].registers_clusters[4].name == "Register2"
        assert device.peripherals[0].registers_clusters[4].address_offset == 0x10
        assert device.peripherals[0].registers_clusters[4].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[5], Register)
        assert device.peripherals[0].registers_clusters[5].name == "Register3"
        assert device.peripherals[0].registers_clusters[5].address_offset == 0x14
        assert device.peripherals[0].registers_clusters[5].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[6], Register)
        assert device.peripherals[0].registers_clusters[6].name == "Register4"
        assert device.peripherals[0].registers_clusters[6].address_offset == 0x18
        assert device.peripherals[0].registers_clusters[6].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[7], Register)
        assert device.peripherals[0].registers_clusters[7].name == "RegisterC"
        assert device.peripherals[0].registers_clusters[7].address_offset == 0x1C
        assert device.peripherals[0].registers_clusters[7].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[8], Register)
        assert device.peripherals[0].registers_clusters[8].name == "RegisterD"
        assert device.peripherals[0].registers_clusters[8].address_offset == 0x20
        assert device.peripherals[0].registers_clusters[8].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[9], Register)
        assert device.peripherals[0].registers_clusters[9].name == "RegisterE"
        assert device.peripherals[0].registers_clusters[9].address_offset == 0x24
        assert device.peripherals[0].registers_clusters[9].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[10], Register)
        assert device.peripherals[0].registers_clusters[10].name == "RegisterF"
        assert device.peripherals[0].registers_clusters[10].address_offset == 0x28
        assert device.peripherals[0].registers_clusters[10].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[11], Register)
        assert device.peripherals[0].registers_clusters[11].name == "RegisterG"
        assert device.peripherals[0].registers_clusters[11].address_offset == 0x2C
        assert device.peripherals[0].registers_clusters[11].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[12], Register)
        assert device.peripherals[0].registers_clusters[12].name == "RegisterH"
        assert device.peripherals[0].registers_clusters[12].address_offset == 0x30
        assert device.peripherals[0].registers_clusters[12].size == 32

    def test_simple_list_field_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("dim_handling/simple_list_field_level.svd")

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 1

        assert isinstance(device.peripherals[0].registers_clusters[0], Register)
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
    def test_dim_array_without_dim_peripheral_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("dim_handling/dim_array_without_dim_peripheral_level.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Found dim-array in name without dim",
    )
    def test_dim_array_without_dim_cluster_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("dim_handling/dim_array_without_dim_cluster_level.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Found dim-array in name without dim",
    )
    def test_dim_array_without_dim_register_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("dim_handling/dim_array_without_dim_register_level.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Found dim-list in name without dim",
    )
    def test_dim_list_without_dim_cluster_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("dim_handling/dim_list_without_dim_cluster_level.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Found dim-list in name without dim",
    )
    def test_dim_list_without_dim_register_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("dim_handling/dim_list_without_dim_register_level.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Found dim-list in name without dim",
    )
    def test_dim_list_without_dim_field_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("dim_handling/dim_list_without_dim_field_level.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Number of <dimIndex> Elements is different to number of <dim> instances",
    )
    def test_dim_list_wrong_dimindex_cluster_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("dim_handling/dim_list_wrong_dimindex_cluster_level.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Number of <dimIndex> Elements is different to number of <dim> instances",
    )
    def test_dim_list_wrong_dimindex_register_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("dim_handling/dim_list_wrong_dimindex_register_level.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Number of <dimIndex> Elements is different to number of <dim> instances",
    )
    def test_dim_list_wrong_dimindex_field_level(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("dim_handling/dim_list_wrong_dimindex_field_level.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Number of <dimIndex> Elements is different to number of <dim> instances",
    )
    def test_wrong_dimindex_svdconv_bug(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("dim_handling/wrong_dimindex_svdconv_bug.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="dimIndex from first dim and dimIndex from second dim contain same value, leading to same register name",
    )
    def test_two_dim_resulting_in_same_name(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("dim_handling/two_dim_resulting_in_same_name.svd")

    def test_array_displayname_with_dim(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("dim_handling/array_displayname_with_dim.svd")

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].name == "Register0"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32
        assert device.peripherals[0].registers_clusters[0].display_name == "Register0"

        assert isinstance(device.peripherals[0].registers_clusters[1], Register)
        assert device.peripherals[0].registers_clusters[1].name == "Register1"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].size == 32
        assert device.peripherals[0].registers_clusters[1].display_name == "Register1"

    def test_list_displayname_with_dim(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("dim_handling/list_displayname_with_dim.svd")

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32
        assert device.peripherals[0].registers_clusters[0].display_name == "RegisterA"

        assert isinstance(device.peripherals[0].registers_clusters[1], Register)
        assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].size == 32
        assert device.peripherals[0].registers_clusters[1].display_name == "RegisterB"

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Expression marker [%s] found in displayName but no <dim> specified",
    )
    def test_array_displayname_without_dim(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("dim_handling/array_displayname_without_dim.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Expression marker [%s] found in displayName but no <dim> specified",
    )
    def test_list_displayname_without_dim(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("dim_handling/list_displayname_without_dim.svd")


class TestEnumeratedValues:
    def test_simple_read_write(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
    def test_three_containers(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("enumerated_values/three_containers.svd")

    def test_default_usage(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
            pytest.param("read", "write", EnumUsageType.READ, EnumUsageType.WRITE),
            pytest.param("write", "read", EnumUsageType.WRITE, EnumUsageType.READ),
            pytest.param("read", "read", None, None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)),
            pytest.param("write", "write", None, None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)),
            pytest.param(
                "read", "read-write", None, None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)
            ),
            pytest.param(
                "write", "read-write", None, None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)
            ),
            pytest.param(
                "read-write", "read", None, None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)
            ),
            pytest.param(
                "read-write", "write", None, None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)
            ),
        ],
    )
    def test_usage_combinations(
        self,
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
        assert isinstance(device.peripherals[0].registers_clusters[0], Register)
        assert len(device.peripherals[0].registers_clusters[0].fields) == 1

        assert len(device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers) == 2

        container1 = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[0]
        assert container1.usage == expected1

        container2 = device.peripherals[0].registers_clusters[0].fields[0].enumerated_value_containers[1]
        assert container2.usage == expected2

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Value name already defined in other container",
    )
    def test_value_name_already_defined_other_container(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
        get_processed_device_from_testfile("enumerated_values/value_name_already_defined_other_container.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Value name already defined in container",
    )
    def test_value_name_already_defined_same_container(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
        get_processed_device_from_testfile("enumerated_values/value_name_already_defined_same_container.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Value already defined in container",
    )
    def test_value_already_defined(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("enumerated_values/value_already_defined.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Multiple isDefault",
    )
    def test_multiple_isdefault(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("enumerated_values/multiple_isdefault.svd")

    def test_do_not_care_handling(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_do_not_care_and_distinct_values(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
    def test_do_not_care_and_distinct_result_in_same_value(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
        get_processed_device_from_testfile("enumerated_values/do_not_care_and_distinct_result_in_same_value.svd")

    def test_default_extension(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
    def test_isdefault_with_value(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("enumerated_values/isdefault_with_value.svd")


class TestPeripheralInheritanceViaDerivedFrom:
    def test_simple_inheritance_backward_reference(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_simple_inheritance_forward_reference(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_value_inheritance(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

        assert isinstance(device.peripherals[1].registers_clusters[0], Register)
        assert device.peripherals[1].registers_clusters[0].name == "RegisterA"

    def test_override_behavior(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
        assert isinstance(device.peripherals[1].registers_clusters[0], Register)
        assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
        assert isinstance(device.peripherals[1].registers_clusters[1], Register)
        assert device.peripherals[1].registers_clusters[1].name == "RegisterB"
        assert device.peripherals[1].registers_clusters[1].address_offset == 0x8

    def test_multiple_inheritance_backward_reference(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_multiple_inheritance_forward_reference(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_multiple_inheritance_backward_and_forward_reference_with_value_override(
        self, get_processed_device_from_testfile: Callable[[str], Device]
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
    def test_circular_inheritance(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/circular_inheritance.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason=(
            "RegisterA is already defined in PeripheralB and cannot be inherited from PeripheralA "
            "because it has the same name"
        ),
    )
    def test_register_inheritance_same_name(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/register_inheritance_same_name.svd")

    def test_register_inheritance_same_address(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_register_inheritance_same_address_dim(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_register_inheritance_overlap_address(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_register_inheritance_oversized_field(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_register_properties_inheritance_size_adjustment(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
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

    def test_same_address(self, get_processed_device_from_testfile: Callable[[str], Device]):
        with pytest.warns(ProcessWarning):
            device = get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/same_address.svd")

        assert len(device.peripherals) == 2
        assert device.peripherals[0].name == "PeripheralA"
        assert device.peripherals[0].base_address == 0x40001000
        assert len(device.peripherals[0].registers_clusters) == 1
        assert device.peripherals[1].name == "PeripheralB"
        assert device.peripherals[1].base_address == 0x40001000
        assert len(device.peripherals[1].registers_clusters) == 1

    def test_block_overlap(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
    def test_same_name(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/same_name.svd")

    def test_alternate_peripheral(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/alternate_peripheral.svd")

        assert len(device.peripherals) == 2
        assert device.peripherals[0].name == "PeripheralA"
        assert device.peripherals[0].base_address == 0x40001000
        assert len(device.peripherals[0].registers_clusters) == 1
        assert device.peripherals[1].name == "PeripheralB"
        assert device.peripherals[1].base_address == 0x40001000
        assert device.peripherals[1].alternate_peripheral == "PeripheralA"
        assert len(device.peripherals[1].registers_clusters) == 1

    def test_alternate_peripheral_overlap(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_register_inheritance_alternate_group(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
        assert device.peripherals[1].registers_clusters[1].name == "RegisterA_RegisterX"
        assert device.peripherals[1].registers_clusters[1].address_offset == 0x0
        assert device.peripherals[1].registers_clusters[1].size == 32
        assert device.peripherals[1].registers_clusters[1].alternate_group == "RegisterX"

    def test_register_inheritance_alternate_register(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
    def test_derive_from_self(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("peripheral_inheritance_via_derivedfrom/derive_from_self.svd")


class TestClusterInheritanceViaDerivedFrom:
    def test_simple_inheritance_backward_reference_same_scope(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
        device = get_processed_device_from_testfile(
            "cluster_inheritance_via_derivedfrom/simple_inheritance_backward_reference_same_scope.svd"
        )

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
        assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].size == 32
        assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 32

    def test_simple_inheritance_forward_reference_same_scope(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
        device = get_processed_device_from_testfile(
            "cluster_inheritance_via_derivedfrom/simple_inheritance_forward_reference_same_scope.svd"
        )

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
        assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].size == 32
        assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 32

    def test_simple_inheritance_backward_reference_different_scope(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
        device = get_processed_device_from_testfile(
            "cluster_inheritance_via_derivedfrom/simple_inheritance_backward_reference_different_scope.svd"
        )

        assert len(device.peripherals) == 2

        assert len(device.peripherals[0].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 32

        assert len(device.peripherals[1].registers_clusters) == 1
        assert isinstance(device.peripherals[1].registers_clusters[0], Cluster)
        assert device.peripherals[1].registers_clusters[0].name == "ClusterA"
        assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[1].registers_clusters[0].size == 32
        assert len(device.peripherals[1].registers_clusters[0].registers_clusters) == 1
        assert isinstance(device.peripherals[1].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[1].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[1].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[1].registers_clusters[0].registers_clusters[0].size == 32

    def test_simple_inheritance_forward_reference_different_scope(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
        device = get_processed_device_from_testfile(
            "cluster_inheritance_via_derivedfrom/simple_inheritance_forward_reference_different_scope.svd"
        )

        assert len(device.peripherals) == 2

        assert len(device.peripherals[0].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 32

        assert len(device.peripherals[1].registers_clusters) == 1
        assert isinstance(device.peripherals[1].registers_clusters[0], Cluster)
        assert device.peripherals[1].registers_clusters[0].name == "ClusterA"
        assert device.peripherals[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[1].registers_clusters[0].size == 32
        assert len(device.peripherals[1].registers_clusters[0].registers_clusters) == 1
        assert isinstance(device.peripherals[1].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[1].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[1].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[1].registers_clusters[0].registers_clusters[0].size == 32

    def test_value_inheritance(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/value_inheritance.svd")

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
        assert device.peripherals[0].registers_clusters[0].description == "ClusterA description"
        assert device.peripherals[0].registers_clusters[0].alternate_cluster == "ClusterC"
        assert device.peripherals[0].registers_clusters[0].header_struct_name == "HeaderStructName"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 16
        assert device.peripherals[0].registers_clusters[0].access == AccessType.WRITE_ONLY
        assert device.peripherals[0].registers_clusters[0].protection == ProtectionStringType.SECURE
        assert device.peripherals[0].registers_clusters[0].reset_value == 0xDEADBEEF
        assert device.peripherals[0].registers_clusters[0].reset_mask == 0xDEADC0DE
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 16

        assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
        assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
        assert device.peripherals[0].registers_clusters[1].description == "ClusterB description"
        assert device.peripherals[0].registers_clusters[1].alternate_cluster == "ClusterC"
        assert device.peripherals[0].registers_clusters[1].header_struct_name == "HeaderStructName"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].size == 16
        assert device.peripherals[0].registers_clusters[1].access == AccessType.WRITE_ONLY
        assert device.peripherals[0].registers_clusters[1].protection == ProtectionStringType.SECURE
        assert device.peripherals[0].registers_clusters[1].reset_value == 0xDEADBEEF
        assert device.peripherals[0].registers_clusters[1].reset_mask == 0xDEADC0DE
        assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 16

    def test_override_behavior(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/override_behavior.svd")

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2
        assert device.peripherals[0].size == 16
        assert device.peripherals[0].access == AccessType.READ_WRITE
        assert device.peripherals[0].protection == ProtectionStringType.ANY
        assert device.peripherals[0].reset_value == 0x0
        assert device.peripherals[0].reset_mask == 0xFFFFFFFF

        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
        assert device.peripherals[0].registers_clusters[0].description == "ClusterA description"
        assert device.peripherals[0].registers_clusters[0].alternate_cluster == "ClusterC"
        assert device.peripherals[0].registers_clusters[0].header_struct_name == "HeaderStructName"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 8
        assert device.peripherals[0].registers_clusters[0].access == AccessType.WRITE_ONLY
        assert device.peripherals[0].registers_clusters[0].protection == ProtectionStringType.SECURE
        assert device.peripherals[0].registers_clusters[0].reset_value == 0xDEADBEEF
        assert device.peripherals[0].registers_clusters[0].reset_mask == 0xDEADC0DE
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 8
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].access == AccessType.WRITE_ONLY
        assert (
            device.peripherals[0].registers_clusters[0].registers_clusters[0].protection == ProtectionStringType.SECURE
        )
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].reset_value == 0xDEADBEEF
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].reset_mask == 0xDEADC0DE

        assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
        assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
        assert device.peripherals[0].registers_clusters[1].description == "ClusterB description"
        assert device.peripherals[0].registers_clusters[1].alternate_cluster == "ClusterD"
        assert device.peripherals[0].registers_clusters[1].header_struct_name == "HeaderStructName2"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x1
        assert device.peripherals[0].registers_clusters[1].size == 16
        assert device.peripherals[0].registers_clusters[1].access == AccessType.WRITE_ONCE
        assert device.peripherals[0].registers_clusters[1].protection == ProtectionStringType.NON_SECURE
        assert device.peripherals[0].registers_clusters[1].reset_value == 0xF0F0F0F0
        assert device.peripherals[0].registers_clusters[1].reset_mask == 0xABABABAB
        assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 2
        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 16
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].access == AccessType.WRITE_ONCE
        assert (
            device.peripherals[0].registers_clusters[1].registers_clusters[0].protection
            == ProtectionStringType.NON_SECURE
        )
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].reset_value == 0xF0F0F0F0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].reset_mask == 0xABABABAB

        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[1], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].name == "RegisterB"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].address_offset == 0x2
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].size == 16
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].access == AccessType.WRITE_ONCE
        assert (
            device.peripherals[0].registers_clusters[1].registers_clusters[1].protection
            == ProtectionStringType.NON_SECURE
        )
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].reset_value == 0xF0F0F0F0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].reset_mask == 0xABABABAB

    def test_multiple_inheritance_backward_reference(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile(
            "cluster_inheritance_via_derivedfrom/multiple_inheritance_backward_reference.svd"
        )

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 3

        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
        assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].size == 32
        assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[2], Cluster)
        assert device.peripherals[0].registers_clusters[2].name == "ClusterC"
        assert device.peripherals[0].registers_clusters[2].address_offset == 0x8
        assert device.peripherals[0].registers_clusters[2].size == 32
        assert len(device.peripherals[0].registers_clusters[2].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[2].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[2].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[2].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[2].registers_clusters[0].size == 32

    def test_multiple_inheritance_forward_reference(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile(
            "cluster_inheritance_via_derivedfrom/multiple_inheritance_forward_reference.svd"
        )

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 3

        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
        assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].size == 32
        assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[2], Cluster)
        assert device.peripherals[0].registers_clusters[2].name == "ClusterC"
        assert device.peripherals[0].registers_clusters[2].address_offset == 0x8
        assert device.peripherals[0].registers_clusters[2].size == 32
        assert len(device.peripherals[0].registers_clusters[2].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[2].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[2].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[2].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[2].registers_clusters[0].size == 32

    @pytest.mark.xfail(strict=True, raises=ProcessException, reason="Circular inheritance is not supported")
    def test_circular_inheritance(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/circular_inheritance.svd")

    @pytest.mark.xfail(strict=True, raises=ProcessException, reason="Nested inheritance is not supported")
    def test_nested_cluster_inheritance(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/nested_cluster_inheritance.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="RegisterA is already defined in ClusterA and cannot be inherited because it has the same name",
    )
    def test_register_inheritance_same_name(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/register_inheritance_same_name.svd")

    def test_register_inheritance_same_address(self, get_processed_device_from_testfile: Callable[[str], Device]):
        with pytest.warns(ProcessWarning):
            device = get_processed_device_from_testfile(
                "cluster_inheritance_via_derivedfrom/register_inheritance_same_address.svd"
            )

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
        assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].size == 32
        assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 2
        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 32
        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[1], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].name == "RegisterB"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].size == 32

    def test_register_inheritance_overlap_address(self, get_processed_device_from_testfile: Callable[[str], Device]):
        with pytest.warns(ProcessWarning):
            device = get_processed_device_from_testfile(
                "cluster_inheritance_via_derivedfrom/register_inheritance_overlap_address.svd"
            )

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
        assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].size == 32
        assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 2
        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 32
        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[1], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].name == "RegisterB"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].address_offset == 0x2
        assert device.peripherals[0].registers_clusters[1].registers_clusters[1].size == 16

    def test_same_address(self, get_processed_device_from_testfile: Callable[[str], Device]):
        with pytest.warns(ProcessWarning):
            device = get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/same_address.svd")

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
        assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].size == 32
        assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 32

    def test_cluster_overlap(self, get_processed_device_from_testfile: Callable[[str], Device]):
        with pytest.warns(ProcessWarning):
            device = get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/cluster_overlap.svd")

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 16
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 16

        assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
        assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x1
        assert device.peripherals[0].registers_clusters[1].size == 8
        assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 8

    def test_alternate_cluster(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/alternate_cluster.svd")

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
        assert device.peripherals[0].registers_clusters[0].alternate_cluster is None
        assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].size == 32
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].size == 32

        assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
        assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
        assert device.peripherals[0].registers_clusters[1].alternate_cluster == "ClusterA"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].size == 32
        assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 1
        assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
        assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 32

    @pytest.mark.xfail(strict=True, raises=ProcessException, reason="Can't derive from self")
    def test_derive_from_self(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/derive_from_self.svd")


class TestRegisterInheritanceViaDerivedFrom:
    def test_simple_inheritance_backward_reference_same_scope(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
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

    def test_simple_inheritance_forward_reference_same_scope(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
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
        self, get_processed_device_from_testfile: Callable[[str], Device]
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
        self, get_processed_device_from_testfile: Callable[[str], Device]
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

    def test_value_inheritance(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_override_behavior(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_multiple_inheritance_backward_reference(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_multiple_inheritance_forward_reference(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
    def test_circular_inheritance(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("register_inheritance_via_derivedfrom/circular_inheritance.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="FieldA is already defined in RegisterA and cannot be inherited because it has the same name",
    )
    def test_field_inheritance_same_name(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("register_inheritance_via_derivedfrom/field_inheritance_same_name.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="FieldA overlaps with FieldB",
    )
    def test_field_inheritance_same_bit_range(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("register_inheritance_via_derivedfrom/field_inheritance_same_bit_range.svd")

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="FieldA overlaps with FieldB",
    )
    def test_field_inheritance_overlap_bit_range(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile(
            "register_inheritance_via_derivedfrom/field_inheritance_overlap_bit_range.svd"
        )

    def test_same_address(self, get_processed_device_from_testfile: Callable[[str], Device]):
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

    def test_register_overlap(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
    def test_derive_from_self(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("register_inheritance_via_derivedfrom/derive_from_self.svd")


class TestFieldInheritanceViaDerivedFrom:
    def test_simple_inheritance_backward_reference_same_scope(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
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
        assert fielda_enum_container.enumerated_values[0].is_default is False
        assert fielda_enum_container.enumerated_values[1].name == "0b1"
        assert fielda_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fielda_enum_container.enumerated_values[1].value == 0b1
        assert fielda_enum_container.enumerated_values[1].is_default is False

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
        assert fieldb_enum_container.enumerated_values[0].is_default is False
        assert fieldb_enum_container.enumerated_values[1].name == "0b1"
        assert fieldb_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fieldb_enum_container.enumerated_values[1].value == 0b1
        assert fieldb_enum_container.enumerated_values[1].is_default is False

    def test_simple_inheritance_forward_reference_same_scope(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
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
        assert fielda_enum_container.enumerated_values[0].is_default is False
        assert fielda_enum_container.enumerated_values[1].name == "0b1"
        assert fielda_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fielda_enum_container.enumerated_values[1].value == 0b1
        assert fielda_enum_container.enumerated_values[1].is_default is False

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
        assert fieldb_enum_container.enumerated_values[0].is_default is False
        assert fieldb_enum_container.enumerated_values[1].name == "0b1"
        assert fieldb_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fieldb_enum_container.enumerated_values[1].value == 0b1
        assert fieldb_enum_container.enumerated_values[1].is_default is False

    def test_simple_inheritance_backward_reference_different_scope(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
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
        assert rega_enum_container.enumerated_values[0].is_default is False
        assert rega_enum_container.enumerated_values[1].name == "0b1"
        assert rega_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert rega_enum_container.enumerated_values[1].value == 0b1
        assert rega_enum_container.enumerated_values[1].is_default is False

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
        assert regb_enum_container.enumerated_values[0].is_default is False
        assert regb_enum_container.enumerated_values[1].name == "0b1"
        assert regb_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert regb_enum_container.enumerated_values[1].value == 0b1
        assert regb_enum_container.enumerated_values[1].is_default is False

    def test_simple_inheritance_forward_reference_different_scope(
        self, get_processed_device_from_testfile: Callable[[str], Device]
    ):
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
        assert rega_enum_container.enumerated_values[0].is_default is False
        assert rega_enum_container.enumerated_values[1].name == "0b1"
        assert rega_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert rega_enum_container.enumerated_values[1].value == 0b1
        assert rega_enum_container.enumerated_values[1].is_default is False

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
        assert regb_enum_container.enumerated_values[0].is_default is False
        assert regb_enum_container.enumerated_values[1].name == "0b1"
        assert regb_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert regb_enum_container.enumerated_values[1].value == 0b1
        assert regb_enum_container.enumerated_values[1].is_default is False

    def test_value_inheritance(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
        assert fielda_enum_container.enumerated_values[0].is_default is False
        assert fielda_enum_container.enumerated_values[1].name == "0b1"
        assert fielda_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fielda_enum_container.enumerated_values[1].value == 0b1
        assert fielda_enum_container.enumerated_values[1].is_default is False

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
        assert fieldb_enum_container.enumerated_values[0].is_default is False
        assert fieldb_enum_container.enumerated_values[1].name == "0b1"
        assert fieldb_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fieldb_enum_container.enumerated_values[1].value == 0b1
        assert fieldb_enum_container.enumerated_values[1].is_default is False

    def test_override_behavior(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
        assert fielda_enum_container.enumerated_values[0].is_default is False
        assert fielda_enum_container.enumerated_values[1].name == "0b1"
        assert fielda_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fielda_enum_container.enumerated_values[1].value == 0b1
        assert fielda_enum_container.enumerated_values[1].is_default is False

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
        assert fieldb_enum_container1.enumerated_values[0].is_default is False
        assert fieldb_enum_container1.enumerated_values[1].name == "0b1"
        assert fieldb_enum_container1.enumerated_values[1].description == "Description for 0b1"
        assert fieldb_enum_container1.enumerated_values[1].value == 0b1
        assert fieldb_enum_container1.enumerated_values[1].is_default is False

        fieldb_enum_container2 = device.peripherals[0].registers_clusters[0].fields[1].enumerated_value_containers[1]
        assert fieldb_enum_container2.name == "FieldBEnumeratedValue"
        assert fieldb_enum_container2.usage == EnumUsageType.WRITE
        assert len(fieldb_enum_container2.enumerated_values) == 2
        assert fieldb_enum_container2.enumerated_values[0].name == "0b0"
        assert fieldb_enum_container2.enumerated_values[0].description == "Description for 0b0"
        assert fieldb_enum_container2.enumerated_values[0].value == 0b0
        assert fieldb_enum_container2.enumerated_values[0].is_default is False
        assert fieldb_enum_container2.enumerated_values[1].name == "0b1"
        assert fieldb_enum_container2.enumerated_values[1].description == "Description for 0b1"
        assert fieldb_enum_container2.enumerated_values[1].value == 0b1
        assert fieldb_enum_container2.enumerated_values[1].is_default is False

    @pytest.mark.xfail(
        strict=True,
        raises=ProcessException,
        reason="Field 'FieldB' (<enumeratedValues> 'FieldAEnumeratedValue'): 'read-write' container already defined",
    )
    def test_enumerated_value_inheritance_error(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("field_inheritance_via_derivedfrom/enumerated_value_inheritance_error.svd")

    def test_multiple_inheritance_backward_reference(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
        assert fielda_enum_container.enumerated_values[0].is_default is False
        assert fielda_enum_container.enumerated_values[1].name == "0b1"
        assert fielda_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fielda_enum_container.enumerated_values[1].value == 0b1
        assert fielda_enum_container.enumerated_values[1].is_default is False

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
        assert fieldb_enum_container.enumerated_values[0].is_default is False
        assert fieldb_enum_container.enumerated_values[1].name == "0b1"
        assert fieldb_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fieldb_enum_container.enumerated_values[1].value == 0b1
        assert fieldb_enum_container.enumerated_values[1].is_default is False

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
        assert fieldc_enum_container.enumerated_values[0].is_default is False
        assert fieldc_enum_container.enumerated_values[1].name == "0b1"
        assert fieldc_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fieldc_enum_container.enumerated_values[1].value == 0b1
        assert fieldc_enum_container.enumerated_values[1].is_default is False

    def test_multiple_inheritance_forward_reference(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
        assert fielda_enum_container.enumerated_values[0].is_default is False
        assert fielda_enum_container.enumerated_values[1].name == "0b1"
        assert fielda_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fielda_enum_container.enumerated_values[1].value == 0b1
        assert fielda_enum_container.enumerated_values[1].is_default is False

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
        assert fieldb_enum_container.enumerated_values[0].is_default is False
        assert fieldb_enum_container.enumerated_values[1].name == "0b1"
        assert fieldb_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fieldb_enum_container.enumerated_values[1].value == 0b1
        assert fieldb_enum_container.enumerated_values[1].is_default is False

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
        assert fieldc_enum_container.enumerated_values[0].is_default is False
        assert fieldc_enum_container.enumerated_values[1].name == "0b1"
        assert fieldc_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fieldc_enum_container.enumerated_values[1].value == 0b1
        assert fieldc_enum_container.enumerated_values[1].is_default is False

    @pytest.mark.xfail(strict=True, raises=ProcessException, reason="Circular inheritance is not supported")
    def test_circular_inheritance(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("field_inheritance_via_derivedfrom/circular_inheritance.svd")

    @pytest.mark.xfail(strict=True, raises=ProcessException, reason="FieldA overlaps with FieldB")
    def test_same_bit_range(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("field_inheritance_via_derivedfrom/same_bit_range.svd")

    @pytest.mark.xfail(strict=True, raises=ProcessException, reason="FieldA overlaps with FieldB")
    def test_overlap_bit_range(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("field_inheritance_via_derivedfrom/overlap_bit_range.svd")

    @pytest.mark.xfail(strict=True, raises=ProcessException, reason="Can't derive from self")
    def test_derive_from_self(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("field_inheritance_via_derivedfrom/derive_from_self.svd")


class TestEnumeratedValuesInheritanceViaDerivedFrom:
    @pytest.mark.xfail(strict=True, raises=ProcessException, reason="Two containers require usage types read and write")
    def test_backward_reference_same_scope(self, get_processed_device_from_testfile: Callable[[str], Device]):
        get_processed_device_from_testfile("enum_copy_via_derivedfrom/backward_reference_same_scope.svd")

    def test_backward_reference_different_scope(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
        assert fielda_enum_container.enumerated_values[0].is_default is False
        assert fielda_enum_container.enumerated_values[1].name == "0b1"
        assert fielda_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fielda_enum_container.enumerated_values[1].value == 0b1
        assert fielda_enum_container.enumerated_values[1].is_default is False

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
        assert fieldb_enum_container.enumerated_values[0].is_default is False
        assert fieldb_enum_container.enumerated_values[1].name == "0b1"
        assert fieldb_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fieldb_enum_container.enumerated_values[1].value == 0b1
        assert fieldb_enum_container.enumerated_values[1].is_default is False

    def test_forward_reference_different_scope(self, get_processed_device_from_testfile: Callable[[str], Device]):
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
        assert fielda_enum_container.enumerated_values[0].is_default is False
        assert fielda_enum_container.enumerated_values[1].name == "0b1"
        assert fielda_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fielda_enum_container.enumerated_values[1].value == 0b1
        assert fielda_enum_container.enumerated_values[1].is_default is False

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
        assert fieldb_enum_container.enumerated_values[0].is_default is False
        assert fieldb_enum_container.enumerated_values[1].name == "0b1"
        assert fieldb_enum_container.enumerated_values[1].description == "Description for 0b1"
        assert fieldb_enum_container.enumerated_values[1].value == 0b1
        assert fieldb_enum_container.enumerated_values[1].is_default is False


class TestDerivedFromPathResolving:
    @pytest.mark.parametrize(
        "path",
        [
            "PeripheralA.ClusterA.ClusterB.RegisterA",
            "ClusterA.ClusterB.RegisterA",
            pytest.param(
                "PeripheralAA.ClusterA.ClusterB.RegisterA",
                marks=pytest.mark.xfail(strict=True, raises=ProcessException),
            ),
            pytest.param(
                "PeripheralA.ClusterAA.ClusterB.RegisterA",
                marks=pytest.mark.xfail(strict=True, raises=ProcessException),
            ),
            pytest.param(
                "PeripheralA.ClusterA.ClusterBB.RegisterA",
                marks=pytest.mark.xfail(strict=True, raises=ProcessException),
            ),
            pytest.param(
                "PeripheralA.ClusterA.ClusterB.RegisterAA",
                marks=pytest.mark.xfail(strict=True, raises=ProcessException),
            ),
            pytest.param(
                "PeripheralA.ClusterB.RegisterA",
                marks=pytest.mark.xfail(strict=True, raises=ProcessException),
            ),
            pytest.param(
                "PeripheralA.ClusterA.RegisterA",
                marks=pytest.mark.xfail(strict=True, raises=ProcessException),
            ),
            pytest.param(
                "PeripheralA.RegisterA",
                marks=pytest.mark.xfail(strict=True, raises=ProcessException),
            ),
            pytest.param(
                "RegisterA",
                marks=pytest.mark.xfail(strict=True, raises=ProcessException),
            ),
            pytest.param(
                "ClusterB.RegisterA",
                marks=pytest.mark.xfail(strict=True, raises=ProcessException),
            ),
            pytest.param(
                "ClusterA.RegisterA",
                marks=pytest.mark.xfail(strict=True, raises=ProcessException),
            ),
        ],
    )
    def test_register_level_same_peripheral_with_nested_cluster(
        self,
        path: str,
        get_test_svd_file_content: Callable[[str], bytes],
    ):
        file_name = "derivedfrom_path_resolving/register_level_same_peripheral_with_nested_cluster.svd"

        file_content = get_test_svd_file_content(file_name)
        file_content = file_content.replace(b"PATH", path.encode())

        device = Process.from_xml_content(file_content).get_processed_device()

        assert len(device.peripherals) == 1
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1

        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "ClusterB"
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters[0].registers_clusters) == 1

        registera = device.peripherals[0].registers_clusters[0].registers_clusters[0].registers_clusters[0]
        assert isinstance(registera, Register)
        assert registera.name == "RegisterA"
        assert registera.address_offset == 0x0
        assert registera.size == 32
        assert len(registera.fields) == 1

        assert registera.fields[0].name == "FieldA"
        assert registera.fields[0].lsb == 0
        assert registera.fields[0].msb == 0

        assert isinstance(device.peripherals[0].registers_clusters[1], Register)
        assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].size == 32
        assert len(device.peripherals[0].registers_clusters[1].fields) == 1

        assert device.peripherals[0].registers_clusters[1].fields[0].name == "FieldA"
        assert device.peripherals[0].registers_clusters[1].fields[0].lsb == 0
        assert device.peripherals[0].registers_clusters[1].fields[0].msb == 0

    @pytest.mark.parametrize(
        "path",
        [
            "SameA.SameA.SameA.SameA",  # can't be processed with svdconv
            "SameA.SameA.SameA",  # can't be processed with svdconv
            pytest.param(
                "SameA",
                marks=pytest.mark.xfail(strict=True, raises=ProcessException),
            ),
            pytest.param(
                "SameA.SameA",
                marks=pytest.mark.xfail(strict=True, raises=ProcessException),
            ),
            pytest.param(
                "SameA.SameA.SameA.SameA.SameA",
                marks=pytest.mark.xfail(strict=True, raises=ProcessException),
            ),
        ],
    )
    def test_register_level_same_peripheral_elements_same_name(
        self,
        path: str,
        get_test_svd_file_content: Callable[[str], bytes],
    ):
        file_name = "derivedfrom_path_resolving/register_level_same_peripheral_elements_same_name.svd"

        file_content = get_test_svd_file_content(file_name)
        file_content = file_content.replace(b"PATH", path.encode())

        device = Process.from_xml_content(file_content).get_processed_device()

        assert len(device.peripherals) == 1
        assert device.peripherals[0].name == "SameA"
        assert len(device.peripherals[0].registers_clusters) == 2

        assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].name == "SameA"
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1

        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Cluster)
        assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "SameA"
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters[0].registers_clusters) == 1

        registera = device.peripherals[0].registers_clusters[0].registers_clusters[0].registers_clusters[0]
        assert isinstance(registera, Register)
        assert registera.name == "SameA"
        assert registera.address_offset == 0x0
        assert registera.size == 32
        assert len(registera.fields) == 1

        assert registera.fields[0].name == "SameA"
        assert registera.fields[0].lsb == 0
        assert registera.fields[0].msb == 0

        assert isinstance(device.peripherals[0].registers_clusters[1], Register)
        assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
        assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
        assert device.peripherals[0].registers_clusters[1].size == 32
        assert len(device.peripherals[0].registers_clusters[1].fields) == 1

        assert device.peripherals[0].registers_clusters[1].fields[0].name == "SameA"
        assert device.peripherals[0].registers_clusters[1].fields[0].lsb == 0
        assert device.peripherals[0].registers_clusters[1].fields[0].msb == 0
