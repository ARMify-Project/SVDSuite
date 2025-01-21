from typing import Callable
import pytest

from svdsuite.process import ProcessWarning
from svdsuite.model.process import Device, Register, Cluster


def test_simple_size_adjustment(get_processed_device_from_testfile: Callable[[str], Device]):
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


def test_complex_size_adjustment(get_processed_device_from_testfile: Callable[[str], Device]):
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


def test_overlap_due_to_size_adjustment(get_processed_device_from_testfile: Callable[[str], Device]):
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
