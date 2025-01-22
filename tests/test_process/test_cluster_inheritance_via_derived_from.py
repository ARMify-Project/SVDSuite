from typing import Callable
import pytest

from svdsuite.process import ProcessException, ProcessWarning
from svdsuite.model.process import Device, Register, Cluster
from svdsuite.model.types import AccessType, ProtectionStringType


def test_simple_inheritance_backward_reference_same_scope(get_processed_device_from_testfile: Callable[[str], Device]):
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


def test_simple_inheritance_forward_reference_same_scope(get_processed_device_from_testfile: Callable[[str], Device]):
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
    get_processed_device_from_testfile: Callable[[str], Device]
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
    get_processed_device_from_testfile: Callable[[str], Device]
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


def test_value_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
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


def test_override_behavior(get_processed_device_from_testfile: Callable[[str], Device]):
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
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].protection == ProtectionStringType.SECURE
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
    assert device.peripherals[0].registers_clusters[1].reset_value == 0x0F0F0F0F
    assert device.peripherals[0].registers_clusters[1].reset_mask == 0xABABABAB
    assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 2
    assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 16
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].access == AccessType.WRITE_ONCE
    assert (
        device.peripherals[0].registers_clusters[1].registers_clusters[0].protection == ProtectionStringType.NON_SECURE
    )
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].reset_value == 0x0F0F0F0F
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].reset_mask == 0xABABABAB

    assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].address_offset == 0x2
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].size == 16
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].access == AccessType.WRITE_ONCE
    assert (
        device.peripherals[0].registers_clusters[1].registers_clusters[1].protection == ProtectionStringType.NON_SECURE
    )
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].reset_value == 0x0F0F0F0F
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].reset_mask == 0xABABABAB


def test_multiple_inheritance_backward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
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


def test_multiple_inheritance_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
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
def test_circular_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/circular_inheritance.svd")


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="Nested inheritance is not supported")
def test_nested_cluster_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/nested_cluster_inheritance.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="RegisterA is already defined in ClusterA and cannot be inherited because it has the same name",
)
def test_register_inheritance_same_name(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/register_inheritance_same_name.svd")


def test_register_inheritance_same_address(get_processed_device_from_testfile: Callable[[str], Device]):
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


def test_register_inheritance_overlap_address(get_processed_device_from_testfile: Callable[[str], Device]):
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


def test_same_address(get_processed_device_from_testfile: Callable[[str], Device]):
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


def test_cluster_overlap(get_processed_device_from_testfile: Callable[[str], Device]):
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


def test_alternate_cluster(get_processed_device_from_testfile: Callable[[str], Device]):
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
def test_derive_from_self(get_processed_device_from_testfile: Callable[[str], Device]):
    get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/derive_from_self.svd")


def test_size_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/size_inheritance.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2
    assert device.peripherals[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
    assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x1
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 8

    assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].address_offset == 0x1
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].size == 32
