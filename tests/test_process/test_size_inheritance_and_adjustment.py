"""
Contrary to what is defined in the CMSIS SVD standard, in `svdconv` the inheritance and adjustment of register sizes
follow a specific algorithm based on implicit and explicit size definitions at different levels. The calculation of the
***effective size*** involves both ***explicit definitions*** and ***inheritance*** from higher levels, following a
recursive approach to determine the ***maximum size*** within each level. Here's how the algorithm works:

For each peripheral, if clusters are present, they are resolved ***from the inside out***, starting with the innermost
clusters (where children are only registers). Each cluster is examined by iterating through all of its children—either
***registers*** or ***subclusters***. The effective size for a register is either ***explicitly defined*** or
***inherited*** from a higher level, such as from the cluster, peripheral, or ultimately the device level. If no
explicit size is defined, it inherits the size from the levels above, taking the first size that is found while
traversing upwards. If this traversal reaches the device level and no size is defined there either, the size is set to
***32 bits*** by default.

For a given cluster, its size is determined by finding the ***maximum size*** among all of its children, including both
registers and subclusters.

This process is repeated ***recursively***, starting with the innermost clusters and moving outward to determine the
size of the parent clusters. Finally, the peripheral's size is calculated by taking the maximum size among all of its
direct children, including clusters and registers. This approach ensures that the effective size of a peripheral is
determined based on the largest size found in its entire hierarchy.

<details> <summary><i>Python code that demonstrates the algorithm (click to expand)</i></summary>

```python from dataclasses import dataclass, field

@dataclass(kw_only=True) class Device: size: None | int = None name: str peripherals: list["Peripheral"] =
field(default_factory=list)

@dataclass(kw_only=True) class Peripheral: size: None | int = None name: str registers_clusters: list["Register |
Cluster"] = field(default_factory=list) parent: Device

@dataclass(kw_only=True) class Cluster: size: None | int = None name: str registers_clusters: list["Register | Cluster"]
= field(default_factory=list) parent: "Cluster | Peripheral"

@dataclass(kw_only=True) class Register: size: None | int = None name: str parent: "Cluster | Peripheral"

def resolve_size_over_levels(peripheral: Peripheral) -> int: # Start resolving the size for the peripheral by examining
all its children inherited_size = resolve_inherited_size(peripheral) effective_size = inherited_size

for element in peripheral.registers_clusters: child_size = resolve_size(element, inherited_size) effective_size =
max(effective_size, child_size)

peripheral.size = effective_size return effective_size

def resolve_size(element: Register | Cluster, inherited_size: int) -> int: # Determine effective size for Register or
Cluster if isinstance(element, Register): return element.size if element.size is not None else inherited_size

if isinstance(element, Cluster): return resolve_cluster_size(element)

raise ValueError("Element must be either Register or Cluster")

def resolve_cluster_size(cluster: Cluster) -> int: # Start resolving the size for the cluster by examining all its
children cluster_inherited_size = resolve_inherited_size(cluster) effective_size = cluster_inherited_size

for child in cluster.registers_clusters: child_size = resolve_size(child, cluster_inherited_size) effective_size =
max(effective_size, child_size)

cluster.size = effective_size return effective_size

def resolve_inherited_size(element: Peripheral | Cluster | Register) -> int: # Traverse upwards to find the first
defined size, or return 32 if no size is defined current = element.parent while current is not None: if current.size is
not None: return current.size current = getattr(current, "parent", None) return 32 # Default to 32 if no size is found
in any parent level

# Example usage: def print_hierarchy(element: Peripheral | Cluster | Register, path: str = ""): if isinstance(element,
Peripheral): path += element.name print(f"{path} (size: {element.size})") for child in element.registers_clusters:
print_hierarchy(child, path + ".") elif isinstance(element, Cluster): path += element.name print(f"{path} (size:
{element.size})") for child in element.registers_clusters: print_hierarchy(child, path + ".") elif isinstance(element,
Register): path += element.name print(f"{path} (size: {element.size})") else: raise ValueError("Element must be either
Peripheral, Cluster or Register")

device = Device(name="DeviceA") peripheral_a = Peripheral(name="PeripheralA", parent=device)

cluster_a = Cluster(name="ClusterA", parent=peripheral_a) register_a = Register(name="RegisterA", parent=cluster_a)
register_b = Register(name="RegisterB", parent=cluster_a) cluster_b = Cluster(name="ClusterB", parent=cluster_a)
register_a_in_cluster_b = Register(name="RegisterA", parent=cluster_b) register_b_in_cluster_b =
Register(name="RegisterB", size=64, parent=cluster_b) cluster_b.registers_clusters.extend([register_a_in_cluster_b,
register_b_in_cluster_b]) cluster_a.registers_clusters.extend([register_a, register_b, cluster_b])

cluster_c = Cluster(name="ClusterC", parent=peripheral_a) register_a_in_cluster_c = Register(name="RegisterA",
parent=cluster_c) register_b_in_cluster_c = Register(name="RegisterB", parent=cluster_c)
cluster_c.registers_clusters.extend([register_a_in_cluster_c, register_b_in_cluster_c])

register_a_in_peripheral = Register(name="RegisterA", parent=peripheral_a)

peripheral_a.registers_clusters.extend([cluster_a, cluster_c, register_a_in_peripheral])
device.peripherals.append(peripheral_a)

# Resolve sizes and print hierarchy resolve_size_over_levels(peripheral_a) print_hierarchy(peripheral_a) ```

</details>
"""

from typing import Callable
import pytest

from svdsuite.process import ProcessWarning
from svdsuite.model.process import Device, Register, Cluster


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_size_adjustment(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test evaluates how the parser handles simple size inheritance and explicit size adjustments within a
    peripheral. In this scenario, the peripheral has both implicit and explicit size definitions, and the parser
    must adjust these sizes based on the rules described. Specifically, `RegisterA` has no explicit size set, so
    it should inherit the size from the peripheral level, while `RegisterB` has an explicit size defined.
    `svdconv` processes this file correctly, applying size adjustments based on the highest level's explicit
    settings.

    **Expected Outcome:** The parser should correctly adjust the sizes, processing the SVD file without errors. The
    peripheral should have two registers, `RegisterA` and `RegisterB`. The overall size of the peripheral should
    be set to 64 bits, which overrides the explicit 16-bit setting due to size adjustments. `RegisterA`, with no
    explicit size set, should inherit the peripheral's size and be 64 bits. `RegisterB`, which explicitly has a
    size of 64 bits, should retain this size. The parser should process the inheritance and size adjustment
    algorithm correctly, reflecting the behavior of `svdconv`.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_complex_size_adjustment(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test examines how the parser handles more intricate scenarios of size inheritance and adjustments across
    clusters and registers within a peripheral. The SVD file contains clusters and registers with varying degrees
    of explicit and implicit size definitions. The parser must determine the correct effective sizes based on size
    inheritance rules and adjustments at different levels. In this case, the sizes within the clusters and
    registers are adjusted, either explicitly or inherited, following a recursive calculation of the maximum
    effective size.

    **Expected Outcome:** The parser should process the file without errors, correctly inheriting and adjusting sizes
    across clusters and registers. ClusterA, which has no explicit size defined, should have its size adjusted to
    64 bits, inherited from ClusterB and its child registers. Both `RegisterA` and `RegisterB` within ClusterA
    should also have effective sizes of 64 bits. Similarly, ClusterB should inherit a size of 64 bits from its
    children, while ClusterC, which also lacks an explicit size, should have a final size of 32 bits, based on its
    child registers, which inherit the size implicitly from device level (default value). Since the size
    adjustment for ClusterC is executed before the final size adjustment for PeripheralA, at this point of time,
    no size is set for PeripheralA. Finally, PeripheralA should adjust its size to 64 bits, reflecting the largest
    size found in its children. The parser should handle all these size adjustments and inheritance steps
    accurately, consistent with the behavior of `svdconv`.

    **Processable with svdconv:** yes
    """

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
    assert cluster_b.address_offset == 0x10
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
    assert cluster_c.address_offset == 0x20
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
    assert device.peripherals[0].registers_clusters[2].address_offset == 0x30
    assert device.peripherals[0].registers_clusters[2].size == 64  # not set, ef. size results in 64 from peripheral


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_overlap_due_to_size_adjustment(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test verifies how the parser handles size adjustments that lead to register overlaps. The SVD file
    contains a peripheral where the size inheritance and adjustment algorithm causes an overlap between two
    registers. Specifically, `PeripheralA` starts with a defined size of 32 bits, but the effective size is
    adjusted to 64 bits due to the size of `RegisterB`. `RegisterA`, which does not have an explicit size,
    inherits its size from the peripheral, leading to an overlap with `RegisterB`, which has an address offset of
    0x4.

    **Expected Outcome:** The parser should process the file and issue a warning about the overlap caused by the size
    adjustment. `PeripheralA` should have a final size of 64 bits, overriding the original size of 32 bits due to
    the size of `RegisterB`. `RegisterA`, which does not have a size defined, should inherit the size from
    `PeripheralA` and have a final size of 64 bits. This leads to an overlap with `RegisterB`, whose size is
    explicitly set to 64 bits, starting at address offset 0x4. The parser should handle this case by adjusting the
    sizes correctly and raising a warning due to the overlap, similar to the behavior in `svdconv`.

    **Processable with svdconv:** yes
    """

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
