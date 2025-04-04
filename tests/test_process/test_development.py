"""
This tests are designed to validate core aspects of the SVD processing and resolution algorithm and were used during
the development of SVDSuite. They are not exhaustive and do not cover all possible edge cases or configurations.
Instead, they focus on the fundamental functionality of the SVD processing and resolution algorithm, ensuring that the
core features work as intended. It focuses on verifying that peripheral-level definitions and nested algorithmic
derivations (including clusters, registers, and inherited enumerated values) are interpreted correctly.

Each test evaluates different facets:
- Peripheral level processing: verifying that each peripheral in the SVD is correctly derived and identified with the
  proper name and base address.
- Algorithm functionality: ensuring that nested clusters and registers are processed with the correct hierarchical
  relationships and default/inherited properties.
"""

from typing import Callable
import pytest

from svdsuite.model.process import Device, Register, Cluster


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_peripheral_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    Test Peripheral Level Processing

    This test validates that the parser correctly processes the peripheral definitions within an SVD file.
    It ensures that:
    - The device object contains the expected number of peripherals.
    - Each peripheral is assigned the correct name and base address as described in the SVD.

    This is critical to confirm that higher-level elements are correctly extracted prior to further processing of
    registers and clusters.

    **Expected Outcome:**
    - The device should include 14 peripherals.
    - Each peripheral must have the expected name and base address as defined.

    **Processable with svdconv:** no - svdconv does not support forward references
    """

    device = get_processed_device_from_testfile("development/peripheral_level.svd")

    assert len(device.peripherals) == 14

    assert device.peripherals[0].name == "PeripheralA0"
    assert device.peripherals[0].base_address == 0x40001000

    assert device.peripherals[1].name == "PeripheralA1"
    assert device.peripherals[1].base_address == 0x40002000

    assert device.peripherals[2].name == "PeripheralB"
    assert device.peripherals[2].base_address == 0x40003000

    assert device.peripherals[3].name == "PeripheralC0"
    assert device.peripherals[3].base_address == 0x40004000

    assert device.peripherals[4].name == "PeripheralC1"
    assert device.peripherals[4].base_address == 0x40005000

    assert device.peripherals[5].name == "PeripheralD"
    assert device.peripherals[5].base_address == 0x40006000

    assert device.peripherals[6].name == "PeripheralE0"
    assert device.peripherals[6].base_address == 0x40007000

    assert device.peripherals[7].name == "PeripheralE1"
    assert device.peripherals[7].base_address == 0x40008000

    assert device.peripherals[8].name == "PeripheralF"
    assert device.peripherals[8].base_address == 0x40009000

    assert device.peripherals[9].name == "PeripheralG0"
    assert device.peripherals[9].base_address == 0x4000A000

    assert device.peripherals[10].name == "PeripheralG1"
    assert device.peripherals[10].base_address == 0x4000B000

    assert device.peripherals[11].name == "PeripheralH"
    assert device.peripherals[11].base_address == 0x4000C000

    assert device.peripherals[12].name == "PeripheralI"
    assert device.peripherals[12].base_address == 0x4000D000

    assert device.peripherals[13].name == "PeripheralJ"
    assert device.peripherals[13].base_address == 0x4000E000


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_algorithm(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    Test Comprehensive SVD Processing Algorithm

    This test evaluates the algorithm's ability to resolve and process nested SVD structures, including clusters,
    registers, and fields with enumerated values. It verifies that the nested hierarchy—involving inherited properties
    and explicit definitions—is correctly handled.

    In this scenario, the SVD file contains peripherals with embedded clusters and registers. The test ensures that:
    - The nested elements are correctly differentiated (clusters vs. registers).
    - Inheritance across the hierarchy is applied appropriately.
    - Default and overridden values are processed as per the SVD standard.

    **Expected Outcome:**
    - The device should consist of 6 peripherals with proper hierarchical nesting.
    - Clusters and registers within these peripherals are resolved correctly, with each element having its
      inherited or explicitly defined properties.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile("development/algorithm.svd")

    assert len(device.peripherals) == 6

    assert device.peripherals[0].name == "ElementA"
    assert device.peripherals[0].base_address == 0x40001000
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
    assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
    assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
    assert len(device.peripherals[0].registers_clusters[0].registers_clusters[0].fields) == 1
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].fields[0].name == "FieldA"
    fielda = device.peripherals[0].registers_clusters[0].registers_clusters[0].fields[0]
    assert len(fielda.enumerated_value_containers) == 1
    assert fielda.enumerated_value_containers[0].name is None

    assert device.peripherals[1].name == "PeripheralA"
    assert device.peripherals[1].base_address == 0x40002000
    assert len(device.peripherals[1].registers_clusters) == 1
    assert isinstance(device.peripherals[1].registers_clusters[0], Cluster)
    assert device.peripherals[1].registers_clusters[0].name == "ElementA"
    assert len(device.peripherals[1].registers_clusters[0].registers_clusters) == 1
    assert isinstance(device.peripherals[1].registers_clusters[0].registers_clusters[0], Cluster)
    assert device.peripherals[1].registers_clusters[0].registers_clusters[0].name == "ClusterA"
    clustera = device.peripherals[1].registers_clusters[0].registers_clusters[0]
    assert len(clustera.registers_clusters) == 1
    assert isinstance(clustera.registers_clusters[0], Register)
    assert clustera.registers_clusters[0].name == "RegisterB"
    assert len(clustera.registers_clusters[0].fields) == 1
    assert clustera.registers_clusters[0].fields[0].name == "FieldA"
    assert len(clustera.registers_clusters[0].fields[0].enumerated_value_containers) == 1
    assert clustera.registers_clusters[0].fields[0].enumerated_value_containers[0].name is None

    assert device.peripherals[2].name == "Peripheral0"
    assert device.peripherals[2].base_address == 0x40003000
    assert len(device.peripherals[2].registers_clusters) == 2
    assert isinstance(device.peripherals[2].registers_clusters[0], Cluster)
    assert device.peripherals[2].registers_clusters[0].name == "ElementA"
    assert len(device.peripherals[2].registers_clusters[0].registers_clusters) == 1
    assert isinstance(device.peripherals[2].registers_clusters[0].registers_clusters[0], Cluster)
    assert device.peripherals[2].registers_clusters[0].registers_clusters[0].name == "ClusterA"
    clustera = device.peripherals[2].registers_clusters[0].registers_clusters[0]
    assert len(clustera.registers_clusters) == 1
    assert isinstance(clustera.registers_clusters[0], Register)
    assert clustera.registers_clusters[0].name == "RegisterB"
    assert len(clustera.registers_clusters[0].fields) == 1
    assert clustera.registers_clusters[0].fields[0].name == "FieldA"
    assert len(clustera.registers_clusters[0].fields[0].enumerated_value_containers) == 1
    assert clustera.registers_clusters[0].fields[0].enumerated_value_containers[0].name is None
    assert isinstance(device.peripherals[2].registers_clusters[1], Cluster)
    assert device.peripherals[2].registers_clusters[1].name == "ClusterA"
    assert len(device.peripherals[2].registers_clusters[1].registers_clusters) == 1
    assert isinstance(device.peripherals[2].registers_clusters[1].registers_clusters[0], Register)
    assert device.peripherals[2].registers_clusters[1].registers_clusters[0].name == "RegisterB"
    assert len(device.peripherals[2].registers_clusters[1].registers_clusters[0].fields) == 1
    assert device.peripherals[2].registers_clusters[1].registers_clusters[0].fields[0].name == "FieldA"
    fielda = device.peripherals[2].registers_clusters[1].registers_clusters[0].fields[0]
    assert len(fielda.enumerated_value_containers) == 1
    assert fielda.enumerated_value_containers[0].name is None

    assert device.peripherals[3].name == "Peripheral1"
    assert device.peripherals[3].base_address == 0x40004000
    assert len(device.peripherals[3].registers_clusters) == 2
    assert isinstance(device.peripherals[3].registers_clusters[0], Cluster)
    assert device.peripherals[3].registers_clusters[0].name == "ElementA"
    assert len(device.peripherals[3].registers_clusters[0].registers_clusters) == 1
    assert isinstance(device.peripherals[3].registers_clusters[0].registers_clusters[0], Cluster)
    assert device.peripherals[3].registers_clusters[0].registers_clusters[0].name == "ClusterA"
    clustera = device.peripherals[3].registers_clusters[0].registers_clusters[0]
    assert len(clustera.registers_clusters) == 1
    assert isinstance(clustera.registers_clusters[0], Register)
    assert clustera.registers_clusters[0].name == "RegisterB"
    assert len(clustera.registers_clusters[0].fields) == 1
    assert clustera.registers_clusters[0].fields[0].name == "FieldA"
    assert len(clustera.registers_clusters[0].fields[0].enumerated_value_containers) == 1
    assert clustera.registers_clusters[0].fields[0].enumerated_value_containers[0].name is None
    assert isinstance(device.peripherals[3].registers_clusters[1], Cluster)
    assert device.peripherals[3].registers_clusters[1].name == "ClusterA"
    assert len(device.peripherals[3].registers_clusters[1].registers_clusters) == 1
    assert isinstance(device.peripherals[3].registers_clusters[1].registers_clusters[0], Register)
    assert device.peripherals[3].registers_clusters[1].registers_clusters[0].name == "RegisterB"
    assert len(device.peripherals[3].registers_clusters[1].registers_clusters[0].fields) == 1
    assert device.peripherals[3].registers_clusters[1].registers_clusters[0].fields[0].name == "FieldA"
    fielda = device.peripherals[3].registers_clusters[1].registers_clusters[0].fields[0]
    assert len(fielda.enumerated_value_containers) == 1
    assert fielda.enumerated_value_containers[0].name is None

    assert device.peripherals[4].name == "PeripheralB"
    assert device.peripherals[4].base_address == 0x40005000
    assert len(device.peripherals[4].registers_clusters) == 1
    assert isinstance(device.peripherals[4].registers_clusters[0], Register)
    assert device.peripherals[4].registers_clusters[0].name == "RegisterA"
    assert len(device.peripherals[4].registers_clusters[0].fields) == 1
    assert device.peripherals[4].registers_clusters[0].fields[0].name == "FieldA"
    assert len(device.peripherals[4].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    assert device.peripherals[4].registers_clusters[0].fields[0].enumerated_value_containers[0].name is None

    assert device.peripherals[5].name == "PeripheralC"
    assert device.peripherals[5].base_address == 0x40006000
    assert len(device.peripherals[5].registers_clusters) == 1
    assert isinstance(device.peripherals[5].registers_clusters[0], Register)
    assert device.peripherals[5].registers_clusters[0].name == "RegisterA"
    assert len(device.peripherals[5].registers_clusters[0].fields) == 1
    assert device.peripherals[5].registers_clusters[0].fields[0].name == "FieldA"
    assert len(device.peripherals[5].registers_clusters[0].fields[0].enumerated_value_containers) == 1
    assert device.peripherals[5].registers_clusters[0].fields[0].enumerated_value_containers[0].name is None
