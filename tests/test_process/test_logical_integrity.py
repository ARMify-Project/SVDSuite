"""
This feature ensures the logical integrity of various elements within SVD processing. The test cases focus on
identifying potential conflicts, ambiguities, and ordering issues that may arise during the parsing and interpretation
of SVD files, ensuring that the structure and relationships between elements are processed correctly and consistently.
"""

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
    """
    This test checks whether the parser can correctly identify and handle naming conflicts when two peripherals
    within the same device have identical names. The test file contains two peripherals, both named `PeripheralA`.
    In order to maintain logical integrity and ensure that each peripheral is uniquely identifiable, the parser
    must detect such conflicts and prevent ambiguous definitions. Similar to `svdconv`, the parser is expected to
    raise an error when it encounters peripherals with the same name, as this represents a violation of the naming
    rules.

    **Expected Outcome:** The parser should raise an error indicating that there is a peripheral naming conflict
    because both peripherals are named `PeripheralA`. This conflict results in ambiguity, which prevents the
    unique identification of peripherals within the device. As a result, the parser must stop processing the SVD
    file and provide an appropriate error message to inform the user of the issue. This behavior is consistent
    with `svdconv`, which also raises an error for such cases to maintain consistency and avoid incorrect memory
    mappings or register configurations.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("logical_integrity/peripherals_same_names.svd")


def test_peripherals_same_address(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test evaluates whether the parser can handle the case where two peripherals are defined with the same
    base address without being marked as alternate peripherals. In this test file, `PeripheralA` and `PeripheralB`
    both have a base address of `0x40001000`, but unlike valid alternate peripheral setups, there is no indication
    that one peripheral is an alternate of the other. This scenario causes `svdconv` to raise an error, as
    peripherals sharing the same base address without an alternate relationship are not allowed. However, a more
    robust parser implementation should issue a warning and continue processing.

    **Expected Outcome:** The parser should process the file successfully while issuing a warning to notify the user
    that `PeripheralA` and `PeripheralB` share the same base address of `0x40001000` without being designated as
    alternate peripherals. The device should contain two peripherals: `PeripheralA` and `PeripheralB`, both with
    the same base address, and each should have one register. The parser should allow the file to be processed
    while alerting the user about the address conflict, handling the situation gracefully while still providing
    feedback on the potential issue, unlike `svdconv`, which raises an error in this case.

    **Processable with svdconv:** no
    """

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
    """
    This test evaluates how the parser handles cases where two peripherals have overlapping address ranges, but
    neither is designated as an alternate peripheral. In this test file, `PeripheralA` starts at `0x40001000`, and
    `PeripheralB` starts at `0x40001500`, causing their memory address blocks to overlap. While `svdconv`
    processes such files, it generates a warning due to the overlap. A parser should mimic this behavior by
    allowing the file to be processed while issuing a warning to the user about the overlapping address spaces.

    **Expected Outcome:** The parser should process the file successfully but issue a warning to inform the user that
    `PeripheralA` and `PeripheralB` have overlapping address ranges. Specifically, `PeripheralA` occupies an
    address range starting at `0x40001000`, and `PeripheralB` starts at `0x40001500`, leading to an overlap. The
    device should contain two peripherals: `PeripheralA`, which starts at `0x40001000` and has one register, and
    `PeripheralB`, which starts at `0x40001500` and also has one register. The parser should handle the overlap by
    warning the user, ensuring that the file is processed correctly while making them aware of the potential
    conflict, similar to `svdconv` behavior.

    **Processable with svdconv:** yes
    """

    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("logical_integrity/peripherals_overlap_address.svd")

    assert len(device.peripherals) == 2
    assert device.peripherals[0].name == "PeripheralA"
    assert device.peripherals[0].base_address == 0x40001000
    assert len(device.peripherals[0].registers_clusters) == 1
    assert device.peripherals[1].name == "PeripheralB"
    assert device.peripherals[1].base_address == 0x40001500
    assert len(device.peripherals[1].registers_clusters) == 1


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_different_register_names_in_peripheral(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test ensures that the parser correctly processes a peripheral containing multiple registers, each with a
    unique name, but no address overlap. The test file includes a single peripheral that contains two distinct
    registers, `RegisterA` and `RegisterB`, each with different address offsets and properties. The purpose of the
    test is to verify that the parser can accurately differentiate between registers with different names within
    the same peripheral and correctly handle their respective properties.

    **Expected Outcome:** The parser should successfully process the SVD file, identifying that the peripheral
    contains two registers, `RegisterA` and `RegisterB`. `RegisterA` should have an address offset of `0x0` and a
    size of 32 bits, while `RegisterB` should have an address offset of `0x4` and a size of 32 bits. The parser
    should correctly handle both registers, ensuring that they are uniquely identified within the same peripheral
    without any naming conflicts or errors.

    **Processable with svdconv:** yes
    """

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
    """
    This test checks whether the parser correctly identifies and handles naming conflicts when multiple registers
    within the same peripheral share the same name. The test file contains a single peripheral with two registers,
    both named `RegisterA`. This scenario is expected to create a conflict, as registers within the same
    peripheral should have unique names to avoid ambiguity. The behavior of the parser should align with
    `svdconv`, which raises an error in the case of identical register names.

    **Expected Outcome:** The parser should raise an error indicating a register naming conflict when it encounters
    two registers within the same peripheral sharing the name `RegisterA`. This error ensures that each register
    is uniquely identifiable, preventing ambiguity in the peripheral's register definition. The parser should halt
    processing for this file and notify the user about the conflict, mirroring `svdconv` behavior, which also does
    not allow registers with the same name in the same peripheral.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("logical_integrity/same_register_names_in_peripheral.svd")


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_register_and_cluster_register_same_names_in_peripheral(
    get_processed_device_from_testfile: Callable[[str], Device],
):
    """
    This test verifies whether the parser correctly handles situations where a register and a cluster within the
    same peripheral share the same register name. The test file contains a peripheral with a standalone register
    named `RegisterA` and a cluster named `ClusterA`. The cluster `ClusterA` itself contains a register also named
    `RegisterA`. This scenario tests whether the parser can distinguish between registers in different
    contexts—i.e., one as a standalone register and the other as part of a cluster—without causing naming
    conflicts.

    **Expected Outcome:** The parser should successfully process the SVD file without errors, correctly identifying
    the register and cluster, even though both contexts contain a register with the same name, `RegisterA`. The
    peripheral should contain two top-level entities: the first is a standalone register named `RegisterA` with an
    address offset of `0x0` and a size of 32 bits. The second is a cluster named `ClusterA` with an address offset
    of `0x4` and a size of 32 bits. The cluster `ClusterA` contains one register named `RegisterA` with an address
    offset of `0x0` and a size of 32 bits. The parser should properly handle the context in which each register is
    defined—differentiating the standalone register from the register within the cluster—and process the file
    without raising any naming conflict errors.

    **Processable with svdconv:** yes
    """

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
    """
    This test checks if the parser can correctly identify and handle naming conflicts when a register and a
    cluster within the same peripheral share the same name. The test file defines a peripheral that contains both
    a standalone register and a cluster, both named `RegisterA`. Since identifiers on the same hierarchical level
    must have unique identifiers within the same peripheral to avoid ambiguity, the expected behavior is for the
    parser to detect this naming conflict and raise an appropriate error, similar to the behavior of `svdconv`.

    **Expected Outcome:** The parser should raise an error indicating a naming conflict between the register and the
    cluster, both named `RegisterA` within the same peripheral. This conflict makes it impossible to uniquely
    identify the register and cluster entities. The parser should fail processing the file and notify the user of
    the conflict, ensuring that each element within a peripheral has a distinct and unique name, consistent with
    the requirements for logical integrity.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("logical_integrity/register_and_cluster_same_names_in_peripheral.svd")


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_register_and_nested_cluster_same_names_in_peripheral(
    get_processed_device_from_testfile: Callable[[str], Device],
):
    """
    This test evaluates whether the parser can correctly handle situations where a standalone register and a
    nested cluster within the same peripheral share the same name. The test file defines a peripheral that
    contains a standalone register named `RegisterA` and a cluster named `ClusterA`. Within `ClusterA`, there is a
    nested cluster also named `RegisterA`, which itself contains a register with the same name, `RegisterA`. This
    test is intended to verify that the parser can differentiate between entities in different hierarchical levels
    despite having the same name.

    **Expected Outcome:** The parser should successfully process the SVD file, correctly identifying the relationships
    and hierarchies of the elements within the peripheral, even when a register and a nested cluster share the
    same name. The peripheral should contain two top-level entities: the first is a standalone register named
    `RegisterA` with an address offset of `0x0` and a size of 32 bits, and the second is a cluster named
    `ClusterA` with an address offset of `0x4` and a size of 32 bits. Inside `ClusterA`, there is a nested cluster
    also named `RegisterA`, which has an address offset of `0x0` and a size of 32 bits. This nested cluster
    contains a register, also named `RegisterA`, with an address offset of `0x0` and a size of 32 bits. The parser
    should accurately distinguish between the standalone register and the registers and clusters within the nested
    structure, processing the file without any naming conflicts or errors.

    **Processable with svdconv:** yes
    """

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
    """
    This test checks whether the parser can correctly handle the situation where two registers within the same
    peripheral are assigned the same address offset. The test file defines a peripheral containing two registers,
    `RegisterA` and `RegisterB`, both with an address offset of `0x0`. Typically, each register within a
    peripheral should have a unique address to ensure proper memory mapping, and `svdconv` raises an error when
    two registers share the same address. However, for compatibility with older versions of `svdconv`, a warning
    may be issued instead of an error in [certain situations](https://github.com/Open-CMSIS-
    Pack/devtools/blob/44643999691347946562c526fc0474194f865c74/tools/svdconv/SVDModel/src/SvdPeripheral.cpp#L721)
    (e.g., when using `dim`). For a parser designed to work with both new and old SVD files, it is recommended to
    allow registers with the same addresses but issue a warning to the user.

    **Expected Outcome:** The parser should process the file successfully but should issue a warning
    (`ProcessWarning`) indicating that `RegisterA` and `RegisterB` have the same address offset of `0x0`. The
    peripheral should contain two registers, both of which are correctly parsed despite the address overlap. The
    first register, `RegisterA`, should have an address offset of `0x0` and a size of 32 bits, while the second
    register, `RegisterB`, should also have an address offset of `0x0` and a size of 32 bits. The parser should
    handle this scenario by allowing the registers with the same addresses but warning the user about the conflict
    to maintain compatibility and awareness of potential issues.

    **Processable with svdconv:** no
    """

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
    """
    This test ensures that the parser correctly handles scenarios where registers within the same peripheral have
    overlapping address ranges. The test file defines a peripheral that contains two registers, `RegisterA` and
    `RegisterB`. `RegisterA` starts at address offset `0x0` with a size of 32 bits, while `RegisterB` starts at
    address offset `0x2` with a size of 16 bits, resulting in an overlap between their address spaces. While
    overlapping registers usually signal a potential conflict in memory mapping, `svdconv` processes such cases
    with warnings rather than errors to ensure backward compatibility.

    **Expected Outcome:** The parser should successfully process the file while issuing a warning indicating that
    `RegisterA` and `RegisterB` have overlapping address spaces. The peripheral should contain two registers:
    `RegisterA` with an address offset of `0x0` and a size of 32 bits, and `RegisterB` with an address offset of
    `0x2` and a size of 16 bits. Despite the overlap in address ranges, the parser should allow the SVD file to be
    processed, maintaining compatibility with `svdconv` behavior, and should alert the user to the potential issue
    through a warning, ensuring awareness of the address overlap without halting the process.

    **Processable with svdconv:** yes - with warnings
    """

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
    """
    This test evaluates how the parser handles cases where a standalone register and a cluster within the same
    peripheral share the same address offset, and further, whether the addresses within the cluster itself overlap
    with the standalone register. The test file defines a peripheral with a standalone register `RegisterA` at
    address offset `0x0` and a cluster named `ClusterA`, also starting at offset `0x0`. Within `ClusterA`, there
    is a register named `RegisterB` with an address offset of `0x0`. The tool `svdconv` processes this without
    issuing a warning or error and does not recognize that `RegisterA` and `ClusterA` effectively overlap, leading
    to `RegisterA` and `RegisterB` having the same absolute address. For clarity and consistency, a parser
    implementation should warn the user about this address conflict.

    **Expected Outcome:** The parser should process the file successfully but issue a warning to inform the user that
    `RegisterA` and `ClusterA` overlap at address offset `0x0`, and as a result, `RegisterB` within `ClusterA`
    ends up sharing the same absolute address as `RegisterA`. The peripheral should contain two top-level
    entities: `RegisterA` with an address offset of `0x0` and a size of 32 bits, and `ClusterA` also with an
    address offset of `0x0` and a size of 32 bits. Inside `ClusterA`, `RegisterB` should be located at an address
    offset of `0x0`, effectively overlapping with `RegisterA` at the peripheral level. The parser should warn the
    user about these overlapping absolute addresses to ensure that such potential conflicts are clearly
    communicated, despite being allowed during processing for compatibility reasons.

    **Processable with svdconv:** yes
    """

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
    """
    This test ensures that the parser can handle scenarios where the address ranges of a standalone register and a
    cluster within the same peripheral overlap. The test file defines a peripheral containing `RegisterA`, which
    starts at address offset `0x0` with a size of 32 bits, and a cluster named `ClusterA`, starting at address
    offset `0x2`. Inside `ClusterA`, there is a register named `RegisterB` that starts at address offset `0x2` and
    has a size of 16 bits (`ClusterA` has therefore also a size of 16 bits). Although `svdconv` does not recognize
    this overlap and processes the file without a warning or an error, a parser implementation should detect this
    condition and issue a warning to the user, as overlapping address ranges can lead to ambiguity in register
    mapping and potential issues during integration.

    **Expected Outcome:** The parser should successfully process the SVD file while issuing a warning to inform the
    user that `RegisterA` and `ClusterA` have overlapping address ranges. Specifically, `RegisterA` starts at
    `0x0` with a size of 32 bits, and `ClusterA` starts at `0x2` with a size of 16 bits, which causes part of
    `ClusterA` (including `RegisterB` at offset `0x2`) to overlap with the address range covered by `RegisterA`.
    The peripheral should contain two top-level entities: `RegisterA`, with an address offset of `0x0` and a size
    of 32 bits, and `ClusterA`, with an address offset of `0x2` and a size of 16 bits. Within `ClusterA`,
    `RegisterB` should also have an address offset of `0x2` and a size of 16 bits, which contributes to the
    address overlap. The parser should handle this situation by issuing a warning, allowing the file to be
    processed while ensuring that users are informed of the potential conflict.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_peripheral_sorting(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test verifies whether the parser correctly sorts the peripherals based on their base addresses, and if
    the base addresses match, then by their names. Unlike `svdconv`, which retains the peripherals in the exact
    order as they appear in the SVD file, a parser implementation should sort peripherals by their base address to
    provide a more predictable structure for users and tools consuming the output. When peripherals have the same
    base address, they should be sorted by their names alphabetically. This sorting approach aims to improve
    consistency and ease of navigation while acknowledging the differences from `svdconv`'s default behavior.

    **Expected Outcome:** The parser should process the SVD file and sort the peripherals by their base addresses in
    ascending order. If any peripherals share the same base address, they should be sorted further by their names.
    For this particular test file, the device should contain four peripherals, sorted as follows: `PeripheralA`
    with a base address of `0x40001000`, followed by `PeripheralB` with a base address of `0x40002000`, then
    `PeripheralC` with a base address of `0x40003000`, and finally `PeripheralD` with a base address of
    `0x40004000`. Each peripheral should retain its respective properties, and the sorted order should improve
    predictability compared to the original file order while maintaining consistency in naming conventions.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_register_cluster_sorting_in_peripheral(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks whether the parser correctly sorts registers and clusters within a peripheral based on their
    address offsets, with registers and clusters sorted first by their offsets and then by their names if they
    share the same address. In `svdconv`, the registers and clusters are processed and retained in the order in
    which they are defined in the SVD file. However, a parser should sort registers and clusters by address offset
    for better organization and consistency. If registers or clusters have the same address, they should further
    be sorted by their names alphabetically to ensure predictable behavior and avoid ambiguity.

    **Expected Outcome:** The parser should process the SVD file and sort the registers and clusters within the
    peripheral by their address offsets. The peripheral should contain two entities in the sorted order:
    `ClusterA` should appear first with an address offset of `0x0`, followed by `RegisterA` with an address offset
    of `0x8`. Inside `ClusterA`, the contained registers should also be sorted by address offset, starting with
    `RegisterA` at offset `0x0` and then `RegisterB` at offset `0x4`. The parser should reflect this sorting order
    accurately, maintaining each register and cluster's respective properties while ensuring a consistent and
    predictable output.

    **Processable with svdconv:** yes
    """

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
    """
    This test checks whether the parser can correctly handle peripherals that are not aligned to a 4-byte
    boundary. The test file defines `PeripheralA`, which has a base address of `0x40001007`, an address that is
    not aligned to a typical 4-byte boundary. In `svdconv`, such unaligned addresses generate a warning to alert
    the user about the misalignment while still allowing the file to be processed. A parser implementation should
    replicate this behavior—processing the SVD file but issuing a warning to inform the user about the unaligned
    address.

    **Expected Outcome:** The parser should successfully process the SVD file, allowing the unaligned base address of
    `PeripheralA`, but it should issue a warning to inform the user that the peripheral base address is not 4-byte
    aligned. The device should contain one peripheral named `PeripheralA` with a base address of `0x40001007` and
    a size of 8 bits. The peripheral should include one register, `RegisterA`, which has an address offset of
    `0x0` and a size of 8 bits. The parser should maintain the integrity of the data while warning the user about
    the address misalignment, ensuring the user is aware of the potential impact of unaligned memory addresses.

    **Processable with svdconv:** yes - with warning
    """

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


def test_register_unaligned_address(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks whether the parser can detect and correctly handle registers that are defined with an
    unaligned address offset. The test file defines `RegisterA`, with a size of 16 bit and an address offset of
    `0x00000003`, making it unaligned in memory. If the register's size would be 8 bit, the register would be
    aligned.

    **Expected Outcome:** The parser should raise a warning indicating that `RegisterA` is unaligned.

    **Processable with svdconv:** yes
    """

    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("logical_integrity/register_unaligned_address.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x3
    assert device.peripherals[0].registers_clusters[0].size == 16


def test_register_size_bit_width(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks whether the parser can correctly handle registers with an unsupported bit width. The test
    file defines `RegisterA` with a size of 23 bits, which is not a standard register size (valid sizes are
    typically 8, 16, 32, or 64 bits). In `svdconv`, this scenario generates a warning, indicating that the
    register size is non-standard but the file is still processable. A parser implementation should mimic this
    behavior, allowing the file to be processed while issuing a warning to alert the user of the non-standard
    register size.

    **Expected Outcome:** The parser should successfully process the SVD file, but it should issue a warning to notify
    the user that the size of `RegisterA` is non-standard and must be 8, 16, 32, or 64 bits. The device should
    contain one peripheral, `PeripheralA`, with a base address of `0x40001000`, and it should include a register,
    `RegisterA`, with an address offset of `0x0` and a size of 23 bits. The parser should allow the file to be
    processed while warning the user about the unusual bit width of the register, maintaining consistency with how
    `svdconv` handles this situation.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_alternate_peripheral(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test ensures that the parser correctly handles the scenario where two peripherals share the same base
    address, with one peripheral explicitly designated as an alternate of the other. In the test file,
    `PeripheralA` and `PeripheralB` are defined with the same base address of `0x40001000`, but `PeripheralB`
    specifies `PeripheralA` as its alternate peripheral. This setup allows the peripherals to share the same
    memory space, which must be explicitly defined to avoid conflicts. `svdconv` processes this file without
    errors, and a parser implementation should do the same while respecting the alternate peripheral relationship.

    **Expected Outcome:** The parser should process the SVD file without errors, correctly identifying `PeripheralA`
    and `PeripheralB` as sharing the same base address of `0x40001000`. The device should contain two peripherals.
    `PeripheralA` should have no alternate peripheral specified, while `PeripheralB` should correctly list
    `PeripheralA` as its alternate peripheral. Both peripherals should retain their respective properties, with
    `PeripheralA` and `PeripheralB` each containing one register. The parser should handle this configuration
    without any issues, ensuring that the alternate peripheral relationship is respected and processed in line
    with the behavior of `svdconv`.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_alternate_peripheral_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks how the parser handles cases where an alternate peripheral is referenced before its
    declaration in the SVD file. In this scenario, `PeripheralA` is defined first and lists `PeripheralB` as its
    alternate peripheral, even though `PeripheralB` is declared later in the file. Both peripherals share the same
    base address of `0x40001000`. While `svdconv` raises an error because it cannot handle forward references in
    alternate peripheral definitions, a more robust parser implementation should be able to process the file
    without any errors or warnings by correctly resolving the forward reference.

    **Expected Outcome:** The parser should successfully process the SVD file without raising any errors or warnings,
    correctly resolving the forward reference between `PeripheralA` and `PeripheralB`. `PeripheralA` should be
    identified with a base address of `0x40001000` and should correctly refer to `PeripheralB` as its alternate
    peripheral. `PeripheralB`, which is defined later in the file, should also have a base address of `0x40001000`
    and should not have an alternate peripheral. Both peripherals should be processed with their respective
    properties intact, and the parser should handle the forward reference seamlessly, ensuring a superior parsing
    experience compared to `svdconv`.

    **Processable with svdconv:** no - error (Peripheral 'PeripheralB' (@0x40001000) has same address as 'PeripheralA'
    (Line 18))
    """

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
    """
    This test evaluates whether the parser can correctly detect and handle the situation where a peripheral is
    marked as an alternate peripheral of another peripheral with the same name. In this test file, two peripherals
    share the same name, and one is designated as an alternate peripheral of the other. This scenario introduces
    ambiguity and conflicts in memory mapping and identification, as each peripheral must have a unique name.
    `svdconv` raises an error in this case due to the naming conflict, and a parser should similarly reject this
    file to prevent confusion in the device definition.

    **Expected Outcome:** The parser should raise an error indicating that a peripheral cannot be marked as an
    alternate peripheral of another peripheral with the same name. Both peripherals are named identically, which
    creates ambiguity and violates the requirement for unique peripheral names. The parser should halt processing
    and notify the user of the conflict, ensuring that each peripheral is uniquely identified. This behavior
    aligns with `svdconv`, which also raises an error in such cases, preventing the SVD file from being processed
    due to the naming conflict.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("logical_integrity/alternate_peripheral_same_name.svd")


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_alternate_peripheral_overlap(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks whether the parser can correctly handle the scenario where two peripherals overlap in their
    memory address space, but one is designated as an alternate peripheral of the other. In this test file,
    `PeripheralA` starts at base address `0x40001000`, and `PeripheralB` starts at `0x40001500`, partially
    overlapping with `PeripheralA`. Since `PeripheralB` is explicitly marked as an alternate peripheral of
    `PeripheralA`, this overlap is allowed without raising an error or warning. `svdconv` processes this without
    issue, and a parser implementation should behave similarly, handling the overlap correctly when alternate
    peripherals are defined.

    **Expected Outcome:** The parser should process the SVD file successfully without raising any errors or warnings.
    The device should contain two peripherals: `PeripheralA` with a base address of `0x40001000` and no alternate
    peripheral, and `PeripheralB` with a base address of `0x40001500`, which overlaps with `PeripheralA` but is
    correctly marked as an alternate peripheral of `PeripheralA`. Both peripherals should contain their respective
    registers, and the parser should ensure that the overlap is handled correctly due to the alternate peripheral
    relationship, consistent with how `svdconv` handles such scenarios.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_alternate_peripheral_multiple(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks whether the parser can correctly handle a scenario where multiple peripherals share the same
    base address and are designated as alternate peripherals of the same primary peripheral. In this test file,
    `PeripheralA` is the primary peripheral with a base address of `0x40001000`, and both `PeripheralB` and
    `PeripheralC` share the same base address but are marked as alternate peripherals of `PeripheralA`. This setup
    is valid, and `svdconv` processes the file without any issues. A parser implementation should also handle this
    configuration smoothly, allowing multiple alternate peripherals without raising errors or warnings.

    **Expected Outcome:** The parser should successfully process the SVD file, correctly identifying that
    `PeripheralB` and `PeripheralC` share the same base address as `PeripheralA` and are marked as alternate
    peripherals. The device should contain three peripherals: `PeripheralA` with a base address of `0x40001000`
    and no alternate peripheral, `PeripheralB` with the same base address and marked as an alternate peripheral of
    `PeripheralA`, and `PeripheralC`, also with the same base address, similarly marked as an alternate peripheral
    of `PeripheralA`. Each peripheral should have its respective registers, and the parser should handle the
    alternate peripheral relationships without any errors or warnings, consistent with how `svdconv` processes
    such files.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_alternate_peripheral_multiple_svdconv_warning(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test evaluates how the parser handles a scenario where multiple peripherals share the same base address
    and are designated as alternates of other peripherals. In this test file, `PeripheralA`, `PeripheralB`,
    `PeripheralC`, and `PeripheralD` all share the same base address of `0x40001000`. `PeripheralB` and
    `PeripheralC` are alternates of `PeripheralA`, and `PeripheralD` is an alternate of `PeripheralC`. Although
    `svdconv` processes this file, it incorrectly generates a warning stating that `PeripheralD` overlaps with
    `PeripheralA`, without respecting the alternate peripheral relationships. A more robust parser should process
    this configuration without generating such an incorrect warning.

    **Expected Outcome:** The parser should process the file without any errors or incorrect warnings, correctly
    recognizing the alternate relationships. The device should contain four peripherals: `PeripheralA` with a base
    address of `0x40001000` and no alternate, `PeripheralB` and `PeripheralC`, both with the same base address and
    marked as alternates of `PeripheralA`, and `PeripheralD`, which also shares the same base address but is an
    alternate of `PeripheralC`. Each peripheral should have its own registers, and the parser should handle this
    setup seamlessly, ensuring that the alternate relationships are processed correctly without the erroneous
    warnings generated by `svdconv`.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_alternate_register(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks whether the parser correctly handles registers that are marked as alternate registers. In
    this test file, `RegisterB` is defined as an alternate register of `RegisterA`, meaning that both registers
    share the same address but have different functionalities or configurations. The test ensures that the parser
    can handle the alternate register relationship without issues. `svdconv` processes this file without errors,
    and a parser implementation should also be able to handle this scenario correctly.

    **Expected Outcome:** The parser should successfully process the SVD file, correctly identifying that `RegisterB`
    is an alternate register of `RegisterA`. The device should contain one peripheral with two registers:
    `RegisterA`, which has an address offset of `0x0` and a size of 32 bits, and `RegisterB`, which also has an
    address offset of `0x0` and a size of 32 bits but is marked as an alternate register of `RegisterA`. The
    parser should accurately reflect this relationship without any warnings or errors, ensuring that the alternate
    register configuration is handled properly, consistent with the behavior of `svdconv`.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_alternate_register_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks how the parser handles cases where a register is marked as an alternate register of another
    register before the latter is defined. In this test file, `RegisterA` refers to `RegisterB` as its alternate
    register, even though `RegisterB` is declared later in the file. While `svdconv` cannot handle forward
    references in alternate register definitions and raises an error, a robust parser implementation should
    resolve this forward reference and process the file without any issues.

    **Expected Outcome:** The parser should successfully process the SVD file without raising any errors or warnings,
    correctly resolving the forward reference between `RegisterA` and `RegisterB`. The device should contain one
    peripheral with two registers: `RegisterA`, which has an address offset of `0x0` and a size of 32 bits, and
    lists `RegisterB` as its alternate register. `RegisterB`, declared later, should also have an address offset
    of `0x0` and a size of 32 bits but does not have an alternate register. The parser should handle this forward
    reference seamlessly, ensuring that both registers are processed correctly, without any of the limitations
    present in `svdconv`.

    **Processable with svdconv:** no
    """

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
    """
    This test checks how the parser handles a situation where a register is marked as an alternate register of
    another register with the same name within the same peripheral. In this test file, `RegisterA` is defined as a
    regular register, and another `RegisterA` is defined as its alternate, causing a naming conflict. `svdconv`
    raises an error in this case, as registers within the same peripheral must have unique names, even if one is
    marked as an alternate. A parser implementation should also detect this naming conflict and raise an
    appropriate error.

    **Expected Outcome:** The parser should raise an error indicating that `RegisterA` cannot be defined as both a
    regular register and an alternate register with the same name within the same peripheral. The file should fail
    to process due to the naming conflict, as each register in a peripheral must have a unique identifier to avoid
    ambiguity. The parser should halt processing and notify the user of the conflict, ensuring that register names
    remain distinct, which aligns with the behavior of `svdconv`, which also raises an error in this case.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("logical_integrity/alternate_register_same_name.svd")


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_alternate_register_overlap(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks whether the parser can correctly handle registers that overlap in memory but are defined as
    alternate registers. In this test file, `RegisterA` is defined at address offset `0x0`, and `RegisterB` is
    defined at address offset `0x2` with overlapping memory space. `RegisterB` is marked as an alternate register
    of `RegisterA`, allowing for the overlap. `svdconv` processes this file without any issues or warnings, and a
    parser implementation should also handle this scenario smoothly without raising any warnings or errors.

    **Expected Outcome:** The parser should successfully process the SVD file, correctly identifying that `RegisterB`
    overlaps with `RegisterA` and is marked as an alternate register. The device should contain one peripheral
    with two registers: `RegisterA` at address offset `0x0` with a size of 32 bits and `RegisterB` at address
    offset `0x2` with a size of 16 bits, which overlaps with `RegisterA` but is marked as its alternate register.
    The parser should handle this configuration without any warnings or errors, similar to `svdconv`, ensuring
    that the alternate register relationship is processed correctly despite the overlapping memory addresses.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_alternate_register_multiple(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test ensures that the parser can handle multiple registers that share the same address and are designated
    as alternates of one another. In this test file, `RegisterA` is defined at address offset `0x0` and serves as
    the primary register. `RegisterB`, `RegisterC`, and `RegisterD` are also defined at the same address, with
    each marked as an alternate register. `RegisterB` and `RegisterC` are alternates of `RegisterA`, and
    `RegisterD` is an alternate of `RegisterC`. While `svdconv` processes this file without issue, the parser
    should also handle the configuration without raising any errors.

    **Expected Outcome:** The parser should process the file successfully, correctly identifying the relationships
    between the registers. `RegisterA` should be recognized as the primary register, with `RegisterB` and
    `RegisterC` being alternates of `RegisterA`. `RegisterD` should be recognized as an alternate of `RegisterC`.
    All registers share the same address offset of `0x0` and have a size of 32 bits. The parser should handle this
    setup without issuing any warnings or errors, ensuring it processes the multiple alternate register
    relationships as expected, similar to `svdconv`.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_alternate_cluster(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks whether the parser can correctly handle clusters that share the same address and are
    designated as alternates of each other. In this test file, `ClusterA` is defined at address offset `0x0`, and
    `ClusterB` is defined at the same address, but is marked as an alternate of `ClusterA`. `svdconv` processes
    this file without any errors or warnings, and a parser implementation should do the same, ensuring that the
    alternate cluster relationship is properly handled.

    **Expected Outcome:** The parser should successfully process the SVD file, identifying the alternate cluster
    relationship without any errors or warnings. The device should contain one peripheral with two clusters:
    `ClusterA`, which is defined at address offset `0x0` and has no alternate cluster, and `ClusterB`, which
    shares the same address offset of `0x0` and is marked as an alternate of `ClusterA`. Both clusters should have
    the correct size of 32 bits, and the parser should ensure that the alternate cluster relationship is respected
    and processed as intended, consistent with `svdconv`.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_alternate_cluster_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks whether the parser can correctly handle forward references in alternate cluster definitions.
    In this test file, `ClusterA` is defined first and references `ClusterB` as its alternate cluster, even though
    `ClusterB` is declared later in the file. While `svdconv` processes the file, it incorrectly issues a warning
    that `ClusterB` has the same address as `ClusterA`, without properly recognizing the alternate cluster
    relationship. A robust parser should correctly resolve the forward reference and process the file without
    generating any incorrect warnings.

    **Expected Outcome:** The parser should successfully process the SVD file without issuing any incorrect warnings.
    It should correctly identify `ClusterA` as being located at address offset `0x0` with a size of 32 bits and
    recognize `ClusterB` as its alternate cluster. Similarly, `ClusterB`, which is defined later in the file at
    the same address offset and with the same size, should be processed correctly as an alternate cluster of
    `ClusterA`. The parser should handle this forward reference without errors or misleading warnings, ensuring
    that the alternate cluster relationship is respected and processed accurately, unlike `svdconv`, which
    incorrectly generates a warning about the overlapping addresses.

    **Processable with svdconv:** yes
    """

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
    """
    This test evaluates whether the parser can handle the scenario where two clusters within the same peripheral
    are given the same name, with one marked as an alternate of the other. In this test file, `ClusterA` is
    defined, and another cluster also named `ClusterA` is marked as its alternate. This creates a naming conflict,
    as clusters within the same peripheral must have unique names. `svdconv` raises an error in this case, and the
    parser should behave similarly, rejecting the file due to the name conflict.

    **Expected Outcome:** The parser should raise an error indicating that two clusters with the same name cannot
    exist within the same peripheral, even if one is designated as an alternate cluster. The file should fail to
    process because both clusters are named `ClusterA`, creating a naming conflict. The parser should halt further
    processing and notify the user about the issue, ensuring that cluster names are unique within a peripheral.
    This behavior is consistent with `svdconv`, which also raises an error for this kind of conflict.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("logical_integrity/alternate_cluster_same_name.svd")


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_alternate_cluster_overlap(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks how the parser handles clusters that overlap in memory but are designated as alternates of
    each other. In this test file, `ClusterA` is defined at address offset `0x0`, and `ClusterB` is defined at
    address offset `0x2`, causing a partial overlap in their memory space. `ClusterB` is marked as an alternate of
    `ClusterA`, which allows for this overlap. `svdconv` processes this file without issues, and a parser
    implementation should handle the overlapping memory regions correctly, considering the alternate relationship
    between the clusters.

    **Expected Outcome:** The parser should process the file successfully, identifying that `ClusterB` overlaps with
    `ClusterA` but is marked as an alternate cluster, which makes the overlap valid. The device should contain one
    peripheral with two clusters: `ClusterA` at address offset `0x0` with a size of 32 bits and no alternate
    cluster, and `ClusterB` at address offset `0x2` with a size of 16 bits, marked as an alternate of `ClusterA`.
    The parser should handle this alternate cluster relationship without any errors or warnings, ensuring that the
    overlap is processed correctly, similar to `svdconv`.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_alternate_cluster_multiple(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test evaluates how the parser handles multiple clusters that share the same address and are designated as
    alternates of one another. In this test file, `ClusterA` is defined at address offset `0x0`, and `ClusterB`,
    `ClusterC`, and `ClusterD` are all also defined at the same address, but each is marked as an alternate of a
    different cluster. `ClusterB` and `ClusterC` are alternates of `ClusterA`, while `ClusterD` is an alternate of
    `ClusterC`. `svdconv` processes this file without any issues, and a parser implementation should also handle
    these relationships correctly.

    **Expected Outcome:** The parser should process the SVD file successfully, recognizing the alternate relationships
    between the clusters. The device should contain one peripheral with four clusters. `ClusterA` should be
    defined at address offset `0x0` with a size of 32 bits and no alternate cluster. `ClusterB` and `ClusterC`
    should also be defined at address offset `0x0`, both with a size of 32 bits, marked as alternates of
    `ClusterA`. `ClusterD`, also at address offset `0x0` with the same size, should be marked as an alternate of
    `ClusterC`. The parser should process this configuration without any warnings or errors, handling multiple
    alternate cluster relationships as intended, consistent with the behavior of `svdconv`.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_register_alternate_group(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test evaluates whether the parser can correctly process registers that share the same address but belong
    to different alternate groups. In this test file, `RegisterA` is defined at address offset `0x0` without any
    alternate group, while a second `RegisterA` and `RegisterB`, both at the same address, are part of the
    alternate group `RegisterX`. `svdconv` processes this file without any issues, and the parser should be able
    to handle the alternate group associations properly.

    **Expected Outcome:** The parser should process the file correctly, identifying the alternate group relationships
    for the registers. `RegisterA` should be defined at address offset `0x0` with a size of 32 bits and no
    alternate group. The second `RegisterA`, also at the same address, should be part of the alternate group
    `RegisterX` and should be named `RegisterA_RegisterX`. Similarly, `RegisterB` should be at the same address
    with the name `RegisterB_RegisterX` and should also belong to the alternate group `RegisterX`. The parser
    should handle this configuration smoothly, without any errors or warnings, consistent with how `svdconv`
    processes this case.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile("logical_integrity/register_alternate_group.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 3

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert device.peripherals[0].registers_clusters[0].alternate_group is None

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert device.peripherals[0].registers_clusters[1].alternate_group == "RegisterX"

    assert isinstance(device.peripherals[0].registers_clusters[2], Register)
    assert device.peripherals[0].registers_clusters[2].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[2].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[2].size == 32
    assert device.peripherals[0].registers_clusters[2].alternate_group == "RegisterX"


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_register_alternate_group_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test ensures that the parser can correctly handle forward references when defining alternate register
    groups. In this test file, `RegisterA` is defined later in the SVD file, but other registers like
    `RegisterA_RegisterX` and `RegisterB_RegisterX` are part of the alternate group `RegisterX`, referencing
    `RegisterA`. A parser should be able to resolve these forward references without any issues.

    **Expected Outcome:** The parser should process the file correctly, resolving the forward reference for the
    alternate register group. It should recognize that `RegisterA_RegisterX` and `RegisterB_RegisterX` both belong
    to the alternate group `RegisterX`, while `RegisterA`, defined later in the file, is the base register with no
    alternate group. All registers should have the same address offset of `0x0` and a size of 32 bits. The parser
    should process this setup without errors, ensuring that the alternate group relationships and forward
    references are handled as expected.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile("logical_integrity/register_alternate_group_forward_reference.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 3

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert device.peripherals[0].registers_clusters[0].alternate_group is None

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert device.peripherals[0].registers_clusters[1].alternate_group == "RegisterX"

    assert isinstance(device.peripherals[0].registers_clusters[2], Register)
    assert device.peripherals[0].registers_clusters[2].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[2].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[2].size == 32
    assert device.peripherals[0].registers_clusters[2].alternate_group == "RegisterX"


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Register in alternate group has same name as other register in same alternate group",
)
def test_register_alternate_group_same_name(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test verifies how the parser handles a situation where two registers in the same alternate group are
    given the same name. In this test file, `RegisterA_RegisterX` is defined twice within the alternate group
    `RegisterX`, which causes a naming conflict. While `svdconv` processes this file, it issues a warning
    indicating that `RegisterA_RegisterX` is already defined. The parser should similarly detect this conflict and
    raise an error due to the duplicate register name within the alternate group.

    **Expected Outcome:** The parser should raise an error, indicating that two registers in the same alternate group
    cannot have the same name. The file should fail to process because `RegisterA_RegisterX` is defined twice,
    leading to a naming conflict within `RegisterX`. The parser should halt further processing and notify the user
    about the issue, ensuring that register names within the same alternate group are unique, consistent with the
    warning behavior seen in `svdconv`.

    **Processable with svdconv:** no - warning (RegisterA_RegisterX already defined)
    """

    get_processed_device_from_testfile("logical_integrity/register_alternate_group_same_name.svd")


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_register_alternate_group_overlap(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks whether the parser correctly handles registers that belong to the same alternate group but
    have overlapping addresses. In this test file, `RegisterA` is defined at address offset `0x0` with no
    alternate group. `RegisterA_RegisterX` and `RegisterB_RegisterX` are both part of the alternate group
    `RegisterX`, but they overlap in memory. `svdconv` processes this file without issues, and the parser should
    also handle these overlapping alternate group registers correctly.

    **Expected Outcome:** The parser should process the SVD file without errors, recognizing that
    `RegisterA_RegisterX` and `RegisterB_RegisterX` belong to the same alternate group despite overlapping
    addresses. The device should contain one peripheral with three registers: `RegisterA` at address offset `0x0`
    with a size of 32 bits and no alternate group, `RegisterA_RegisterX` at the same address with a size of 16
    bits, and `RegisterB_RegisterX` at the same address with a size of 32 bits, both belonging to `RegisterX`. The
    parser should handle this alternate group overlap without errors or warnings, consistent with `svdconv`.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile("logical_integrity/register_alternate_group_overlap.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 3

    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[0].size == 32
    assert device.peripherals[0].registers_clusters[0].alternate_group is None

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert device.peripherals[0].registers_clusters[1].alternate_group == "RegisterX"

    assert isinstance(device.peripherals[0].registers_clusters[2], Register)
    assert device.peripherals[0].registers_clusters[2].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[2].address_offset == 0x2
    assert device.peripherals[0].registers_clusters[2].size == 16
    assert device.peripherals[0].registers_clusters[2].alternate_group == "RegisterX"


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Field has same name as other field",
)
def test_fields_same_names(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test ensures that the parser correctly identifies and handles cases where two fields within the same
    register are given the same name. In the CMSIS-SVD standard, field names within a register must be unique. If
    two fields share the same name, it creates ambiguity, which could lead to incorrect behavior in the device
    description. `svdconv` correctly identifies this issue as error, whereas the parser should explicitly raise an
    error, preventing the creation of registers with duplicated field names.

    **Expected Outcome:** The parser should raise an error indicating that two fields within the same register share
    the same name. The device should not be processed further, and the parser must halt execution due to the field
    naming conflict, ensuring the integrity of the SVD description.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("logical_integrity/fields_same_names.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Field overlaps other field",
)
def test_fields_same_bit_offset(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test ensures that the parser correctly identifies fields with the same range within a register. In the
    CMSIS-SVD standard, fields within a register must occupy unique, non-overlapping bit ranges. If two fields
    share the same range, it creates a conflict that can lead to incorrect behavior in the device description. The
    parser must detect such overlaps and raise an error.

    **Expected Outcome:** The parser should raise an error indicating that two fields within the same register have
    the same range. The device description should not be processed further due to this conflict, ensuring that the
    integrity of the SVD file is maintained.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("logical_integrity/fields_same_bit_offset.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Field overlaps other field",
)
def test_fields_overlap_bit_offset(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test ensures that the parser correctly identifies overlapping fields within the same register, where
    multiple fields are assigned the same bit offset or range. In the CMSIS-SVD standard, fields within a register
    must occupy unique, non-overlapping bit ranges. If two fields share the same bit offset, it creates a conflict
    that can lead to incorrect behavior in the device description. The parser must detect such overlaps and raise
    an error.

    **Expected Outcome:** The parser should raise an error indicating that two fields within the same register overlap
    in their bit offsets. The device description should not be processed further due to this conflict, ensuring
    that the integrity of the SVD file is maintained.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("logical_integrity/fields_overlap_bit_offset.svd")


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_field_bit_range_processing(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test validates the parser's ability to process and interpret bit ranges in a field using three mutually
    exclusive methods defined by the CMSIS-SVD standard: bitRangeOffsetWidthStyle, bitRangeLsbMsbStyle, and
    bitRangePattern. Each method offers a different way to describe the position and width of a field within a
    register. The parser must correctly process fields defined by any of these methods and convert them into a
    consistent internal representation of the least significant bit (LSB) and the most significant bit (MSB) of
    the field.

    **Expected Outcome:** The parser should correctly process the SVD file and handle all three bit range formats
    without errors. It should translate the fields defined by bitOffset/bitWidth, lsb/msb, and bitRange into
    consistent LSB and MSB values. Specifically, `FieldA`, `FieldB`, and `FieldC` should have correctly processed
    bit positions, ensuring that the register is fully described with non-overlapping bit fields from LSB 0 to MSB
    11.

    **Processable with svdconv:** yes
    """

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
    """
    The `bitRangePattern` must conform to the format `\\[([0-6])?[0-9]:([0-6])?[0-9]\\]`, as defined by the CMSIS-
    SVD standard. If the string in `bitRangePattern` does not match this pattern, an error should be raised. This
    test ensures that the parser validates the bit range format correctly, in line with how `svdconv` behaves when
    encountering invalid bit range strings.

    **Expected Outcome:** The parser should raise an error indicating that the string in the `bitRangePattern` is
    incorrect, as it does not match the required format. The test will fail if the parser does not handle this
    invalid format appropriately, which corresponds with the behavior seen in `svdconv`.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("logical_integrity/field_wrong_string_in_bitrangepattern.svd")


def test_field_illogical_values_in_bitrangepattern(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks if the parser correctly handles a `bitRangePattern` where the least significant bit (LSB) is
    greater than the most significant bit (MSB).

    **Expected Outcome:** The parser should raise a warning indicating that the bit range is illogical because the LSB
    is greater than the MSB and should switch the values of LSB and MSB.

    **Processable with svdconv:** no
    """

    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("logical_integrity/field_illogical_values_in_bitrangepattern.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert len(device.peripherals[0].registers_clusters[0].fields) == 1
    assert device.peripherals[0].registers_clusters[0].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[0].fields[0].lsb == 8
    assert device.peripherals[0].registers_clusters[0].fields[0].msb == 11


def test_ignore_empty_peripheral(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test verifies that the parser correctly ignores peripheral definitions that do not contain any registers
    or clusters. In the provided SVD file, one or more empty peripheral sections are present. These empty definitions
    should be skipped, and only peripherals containing valid elements should be processed.

    **Expected Outcome:** The parser should process the file while issuing a warning, and the resulting device should
    contain only two peripherals (e.g. "PeripheralA" and "PeripheralC") that include valid register definitions.
    Empty peripheral definitions are ignored.

    **Processable with svdconv:** yes
    """

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


def test_ignore_empty_cluster(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks that empty clusters, that do not define any registers or nested elements, are ignored
    during parsing. The SVD file under test contains an empty cluster that should not produce any
    registers in the final device representation.

    **Expected Outcome:** The parser should process the file without errors while issuing a warning, and only valid
    registers (with non-empty clusters) should be present. In this case, the peripheral "PeripheralA" should contain a
    register starting at offset 0x4.

    **Processable with svdconv:** yes
    """

    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("logical_integrity/ignore_empty_cluster.svd")

    assert device.peripherals[0].name == "PeripheralA"
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x4


def test_ignore_empty_cluster_two_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test validates that the parser can handle an empty cluster at a nested (two-level) hierarchy.
    If a cluster within a peripheral is empty (i.e. it does not contain any registers or sub-clusters), then
    that empty inner cluster should be ignored during the processing so that only valid register definitions
    are maintained.

    **Expected Outcome:** The parser should process the file with a warning and return a device where the peripheral
    "PeripheralA" contains one valid register with an address offset of 0x4, ignoring any empty inner clusters.

    **Processable with svdconv:** yes
    """

    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("logical_integrity/ignore_empty_cluster_two_level.svd")

    assert device.peripherals[0].name == "PeripheralA"
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x4


def test_ignore_empty_inner_cluster(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test ensures that the parser properly ignores empty inner clusters within a non-empty cluster.
    In the tested SVD file, the peripheral "PeripheralA" contains a valid cluster ("ClusterA") that in turn includes an
    inner cluster without registers. The parser should discard the empty inner cluster and process only the
    valid elements.

    **Expected Outcome:** The device should contain two top-level entities under "PeripheralA": one cluster ("ClusterA")
    that contains a valid register "RegisterA" at offset 0x0, and a standalone register "RegisterA" at offset 0x4.
    A warning is issued regarding the ignored empty inner cluster.

    **Processable with svdconv:** yes
    """

    with pytest.warns(ProcessWarning):
        device = get_processed_device_from_testfile("logical_integrity/ignore_empty_inner_cluster.svd")

    assert device.peripherals[0].name == "PeripheralA"
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
    assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
    assert device.peripherals[0].registers_clusters[0].address_offset == 0x0
    assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].address_offset == 0x0

    assert isinstance(device.peripherals[0].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="alternateGroup and alternateRegister are mutually exclusive",
)
def test_alternate_register_and_alternate_group_exception(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test verifies that the parser rejects SVD files where a register is defined with both an alternateRegister
    and an alternateGroup attribute simultaneously. According to the SVD standard, these two attributes are mutually
    exclusive, and their simultaneous presence indicates an invalid file configuration.

    **Expected Outcome:** The parser should raise a ProcessException indicating that a register cannot have both an
    alternateRegister and an alternateGroup defined. This behavior enforces the SVD standard's constraint on mutually
    exclusive alternate definitions.

    **Processable with svdconv:** yes - but it shouldn't since it is contrary to the SVD standard
    """

    get_processed_device_from_testfile("logical_integrity/alternate_register_and_alternate_group_exception.svd")
