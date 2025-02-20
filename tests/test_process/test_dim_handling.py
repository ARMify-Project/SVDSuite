"""
The `dim` element in the CMSIS SVD standard is a powerful feature used to define arrays or lists of repeated elements
such as peripherals, registers, clusters, or fields. It enables the efficient creation of multiple instances of an
object by using a few key attributes rather than duplicating entries.

When working with arrays or lists, the `dim` element specifies the number of instances, while `dimIncrement` defines the
memory address offset between consecutive elements. The `dimIndex` placeholder is used to provide custom names for each
instance, making it possible to generate meaningful and distinct names for each list element. Additionally, the
`dimName` can be defined to specify custom C-type structures if needed.

This chapter tests the parser’s ability to handle `dim` lists and arrays across various hierarchical levels, ensuring
correct expansion and interpretation of arrays and lists at the peripheral, register, cluster, and field levels. The
test cases ensure that all elements are properly expanded, their addresses are correctly calculated, and the parser
processes arrays and lists as specified by the `dim` attributes, while adhering to the memory layout requirements.
"""

from typing import Callable
import pytest

from svdsuite.process import ProcessException
from svdsuite.model.process import Device, Register, Cluster


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_array_peripheral_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test validates whether the parser correctly handles arrays at the peripheral level using `dim` and
    `dimIncrement`. The SVD file defines an array of peripherals, each containing registers with identical
    configurations. The test ensures that the array is expanded correctly, with the proper base addresses for each
    peripheral and the corresponding registers.

    **Expected Outcome:** The parser should process the array defined at the peripheral level, resulting in two
    peripherals, `Peripheral0` and `Peripheral1`, each having a base address and identical register
    configurations. `Peripheral0` should have a base address of `0x40001000`, while `Peripheral1` should have a
    base address of `0x40002000`. Both peripherals should contain two registers, `RegisterA` at address offset
    `0x0` and `RegisterB` at address offset `0x4`. The parser must expand the peripheral array as expected and
    assign the correct addresses to each register without any errors.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_array_cluster_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case checks the parser's ability to correctly handle arrays defined at the cluster level. The `dim`
    element is used to generate multiple instances of clusters, with each cluster containing a set of registers.
    The parser must correctly expand the array, calculate the memory offsets, and ensure that all registers within
    each cluster are properly processed.

    **Expected Outcome:** The parser should successfully generate two instances of the cluster, each containing two
    registers. The first cluster should be named `Cluster0` with a base address offset of `0x0`, and the second
    cluster should be named `Cluster1` with a base address offset of `0x8`. Each cluster should contain two
    registers: `RegisterA` and `RegisterB`, with correct memory offsets.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_array_register_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks the parser's ability to handle arrays defined at the register level. The `dim` element is
    used to create an array of registers within a peripheral, where each register is automatically assigned a
    unique name and address offset based on the `dimIncrement` value. The parser should expand this array
    correctly, ensuring that the registers are sequentially named and have appropriate memory offsets.

    **Expected Outcome:** The parser should successfully process the array of registers, creating two distinct
    registers named `Register0` and `Register1`. `Register0` should have a base address offset of `0x0` and a size
    of 32 bits, while `Register1` should have a base address offset of `0x4` and also a size of 32 bits. The
    `dimIncrement` should be applied correctly to ensure proper address spacing between the registers.

    **Processable with svdconv:** yes
    """

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
def test_simple_array_field_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test examines whether the parser correctly handles arrays defined at the field level within a register.
    In the SVD file, the `dim` element is used to define an array of fields inside a register. However, in
    `svdconv`, fields cannot be arrays, which results in an error. The parser should likewise detect and handle
    this case, raising an appropriate exception or error.

    **Expected Outcome:** The parser should fail to process the file, raising an exception due to the invalid use of a
    `dim` array at the field level. The error message should indicate that fields cannot be defined as arrays,
    mirroring the behavior of `svdconv`.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("dim_handling/simple_array_field_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Peripheral cannot be a list",
)
def test_simple_list_peripheral_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test examines whether the parser correctly handles the use of `dim` lists at the peripheral level. In the
    SVD file, a `dim` list is used to define multiple instances of a peripheral. However, `svdconv` does not allow
    the use of `dim` lists at the peripheral level, resulting in an error. The parser should recognize this
    invalid usage and raise an appropriate exception.

    **Expected Outcome:** The parser should fail to process the file and raise an error, as `dim` lists are not
    allowed at the peripheral level. The error should clearly indicate that peripherals cannot be defined as
    lists, mirroring the behavior of `svdconv`.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("dim_handling/simple_list_peripheral_level.svd")


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_list_cluster_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test verifies how the parser handles `dim` lists at the cluster level. The SVD file defines multiple
    clusters using a `dim` list, creating several instances of clusters within a peripheral. The parser should be
    able to correctly process the SVD file, generating individual clusters with proper naming, offsets, and sizes
    for each list item.

    **Expected Outcome:** The parser should successfully process the file, creating two clusters: `ClusterA` and
    `ClusterB`. Each cluster should contain two registers, `RegisterA` and `RegisterB`, with correct offsets and
    sizes. The parser should correctly handle the `dim` list at the cluster level, following the SVD structure to
    replicate multiple clusters, as allowed by the standard and `svdconv`.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_list_register_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test verifies the parser's ability to handle `dim` lists at the register level, covering various ways of
    specifying the `dimIndex` values. The SVD file contains multiple registers created using different types of
    `dimIndex` definitions, including numeric, alphabetic, and custom sequences. The parser needs to process and
    correctly instantiate each register based on the provided list values, ensuring proper address offsets and
    names.

    **Expected Outcome:** The parser should process the SVD file successfully, generating 13 registers with the
    correct names, address offsets, and sizes. The registers should follow the naming conventions specified by
    their respective `dimIndex` values, covering all possible variations, such as numeric indices (e.g.,
    Register0, Register1), alphabetic indices (e.g., RegisterA, RegisterB), and custom sequences (e.g., RegisterC,
    RegisterD). The address offsets should increment correctly for each register based on the `dimIncrement`
    value.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_list_field_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test ensures that the parser correctly handles `dim` lists at the field level within a register. The SVD
    file defines multiple fields inside a register using the `dim` element to generate a list of fields. Each
    field is created with specific bit positions, and the parser must correctly instantiate each field based on
    the provided list values.

    **Expected Outcome:** The parser should successfully process the SVD file, generating a register with two fields.
    The first field, `FieldA`, should occupy bits 0 to 1, while the second field, `FieldB`, should occupy bits 2
    to 3. The fields should be correctly named and positioned within the register according to their respective
    bit positions, and the parser should handle the `dim` list without issues.

    **Processable with svdconv:** yes
    """

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
def test_dim_array_without_dim_peripheral_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test verifies how the parser handles a situation where an array-like naming convention is used at the
    peripheral level without defining the `dim` element. In this SVD file, a `dim`-style array name is present,
    but the corresponding `dim` element is missing. The parser must detect this inconsistency and raise an error,
    as arrays require the `dim` element to define the number of instances.

    **Expected Outcome:** The parser should fail to process the SVD file and raise an error. The reason for this error
    is the presence of an array-like name at the peripheral level without a corresponding `dim` element, which is
    necessary to define the array's structure. This behavior is consistent with the expected outcome in `svdconv`.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("dim_handling/dim_array_without_dim_peripheral_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Found dim-array in name without dim",
)
def test_dim_array_without_dim_cluster_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks how the parser handles a cluster with an array-like naming convention but without the
    corresponding `dim` element. The array naming style is present, but the `dim` element is missing. The parser
    should detect this and raise an error, as arrays require the `dim` element to define the instances. `svdconv`
    does not print an error or warning for this test case, but ignores the cluster. This seems to be a bug in
    `svdconv`.

    **Expected Outcome:** The parser should fail to process the SVD file, raising an error because a cluster name
    indicates an array, but the `dim` element is missing. This behavior is **not** consistent with the outcome in
    `svdconv`.

    **Processable with svdconv:** yes
    """

    get_processed_device_from_testfile("dim_handling/dim_array_without_dim_cluster_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Found dim-array in name without dim",
)
def test_dim_array_without_dim_register_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test evaluates how the parser handles registers named as arrays without the corresponding `dim` element.
    The array-like naming convention is used without defining the `dim` element, and the parser should raise an
    error.

    **Expected Outcome:** The parser should raise an error when processing the file, as a register name implies an
    array but lacks the `dim` element. The behavior should match `svdconv` expectations.
    """

    get_processed_device_from_testfile("dim_handling/dim_array_without_dim_register_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Found dim-list in name without dim",
)
def test_dim_list_without_dim_cluster_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks how the parser handles clusters that are named as lists without defining the `dim` element.
    The list-like naming convention without `dim` should result in an error. `svdconv` does not print an error or
    warning for this test case, but ignores the cluster. This seems to be a bug in `svdconv`.

    **Expected Outcome:** The parser should raise an error due to the missing `dim` element for a list-style cluster
    name. This **does not** align with `svdconv` behavior.

    **Processable with svdconv:** yes
    """

    get_processed_device_from_testfile("dim_handling/dim_list_without_dim_cluster_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Found dim-list in name without dim",
)
def test_dim_list_without_dim_register_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test verifies how the parser handles registers named as lists without a `dim` element. The list-style
    naming convention without `dim` should result in an error.

    **Expected Outcome:** The parser should raise an error due to the absence of a `dim` element for a list-style
    register name, consistent with `svdconv`.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("dim_handling/dim_list_without_dim_register_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Found dim-list in name without dim",
)
def test_dim_list_without_dim_field_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks how the parser handles fields named as lists without the `dim` element. The parser should
    raise an error for list-style fields lacking the `dim` element. `svdconv` does not print an error or warning
    for this test case, but ignores the field. This seems to be a bug in `svdconv`.

    **Expected Outcome:** The parser should raise an error due to the absence of a `dim` element for a list-style
    field name. This behavior is **not** consistent with `svdconv`.

    **Processable with svdconv:** yes
    """

    get_processed_device_from_testfile("dim_handling/dim_list_without_dim_field_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Number of <dimIndex> Elements is different to number of <dim> instances",
)
def test_dim_list_wrong_dimindex_cluster_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test checks how the parser handles a situation where the `dim` and `dimIndex` elements at the cluster
    level are inconsistent. In this case, the number of elements defined in `dimIndex` does not match the number
    of `dim` instances. This mismatch should result in an error, as the parser expects the number of `dimIndex`
    elements to exactly match the `dim` count.

    **Expected Outcome:** The parser should fail to process the SVD file and raise an error. The error should clearly
    state that the number of `dimIndex` elements is different from the number of `dim` instances, which is
    consistent with how `svdconv` handles this type of error.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("dim_handling/dim_list_wrong_dimindex_cluster_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Number of <dimIndex> Elements is different to number of <dim> instances",
)
def test_dim_list_wrong_dimindex_register_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test examines the behavior of the parser when the `dim` and `dimIndex` elements at the register level are
    inconsistent. Specifically, the number of elements in the `dimIndex` list does not match the number of
    instances defined by the `dim` element. This mismatch should cause an error, as the parser requires the number
    of `dimIndex` elements to correspond exactly to the `dim` count.

    **Expected Outcome:** The parser should fail to process the SVD file and raise an error, indicating that the
    number of `dimIndex` elements is different from the number of `dim` instances. This error is expected to align
    with the behavior of `svdconv`, which also raises an error for this type of discrepancy.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("dim_handling/dim_list_wrong_dimindex_register_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Number of <dimIndex> Elements is different to number of <dim> instances",
)
def test_dim_list_wrong_dimindex_field_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test evaluates how the parser handles a situation where the number of `dimIndex` elements does not match
    the number of `dim` instances at the field level. Such a mismatch between the `dim` and `dimIndex` lists
    should cause an error, as the parser requires the number of entries in both lists to be consistent.

    **Expected Outcome:** The parser should raise an error, signaling that the number of `dimIndex` elements is
    different from the number of `dim` instances. This outcome matches the behavior expected from `svdconv`, which
    also raises an error when encountering such a discrepancy in the `dim` and `dimIndex` configuration at the
    field level.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("dim_handling/dim_list_wrong_dimindex_field_level.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Number of <dimIndex> Elements is different to number of <dim> instances",
)
def test_wrong_dimindex_svdconv_bug(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case explores a scenario where the `dimIndex` format uses ranges like `A-C` or `1-3`, which
    `svdconv` does not correctly handle. Despite no error being raised by `svdconv`, the affected peripheral is
    not created. This appears to be a bug in `svdconv`. In contrast, a proper parser implementation must identify
    and report an error when the number of `dimIndex` elements does not match the number of `dim` instances,
    regardless of how the `dimIndex` is formatted.

    **Expected Outcome:** The parser should raise an error due to the mismatch between the number of `dimIndex`
    elements and the number of `dim` instances. Although `svdconv` fails to generate an error in this case, a
    correctly implemented parser must detect this issue and prevent further processing to ensure that the file
    structure follows the proper SVD conventions.

    **Processable with svdconv:** yes
    """

    get_processed_device_from_testfile("dim_handling/wrong_dimindex_svdconv_bug.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="dimIndex from first dim and dimIndex from second dim contain same value, leading to same register name",
)
def test_two_dim_resulting_in_same_name(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test evaluates how the parser handles cases where two `dim` lists result in conflicting register names
    due to overlapping `dimIndex` values. In this SVD file, two registers use separate `dim` lists, but both lists
    share common `dimIndex` values. The first register uses `dimIndex` values `A` and `B`, while the second
    register uses `B` and `C`. This leads to a naming conflict for `RegisterB`, as it is generated by both `dim`
    lists. The parser needs to detect this name collision.

    **Expected Outcome:** The parser should raise an error due to the naming conflict caused by overlapping `dimIndex`
    values. Both registers attempt to create a register with the name `RegisterB`, which violates the uniqueness
    requirement for register names within a peripheral. This error should be flagged and prevent further
    processing, ensuring that such conflicts are handled appropriately.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("dim_handling/two_dim_resulting_in_same_name.svd")


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_array_displayname_with_dim(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case checks how the parser handles an array of registers where each register is assigned a distinct
    `displayName` that follows the `dim` definition. The `dim` element is used to create an array of registers,
    and the `displayName` field should update accordingly for each register instance. `svdconv` processes this
    case without issues, and the parser is expected to follow similar behavior, correctly assigning the
    appropriate `displayName` to each register in the array.

    **Expected Outcome:** The parser should successfully process the file, creating an array of registers. For each
    register, the `displayName` should match the respective register name. In this case, `Register0` and
    `Register1` should be created, with corresponding `displayName` values of "Register0" and "Register1". The
    `addressOffset` and `size` values for both registers should also be correctly set to `0x0` and `0x4`
    respectively, with a size of 32 bits.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_list_displayname_with_dim(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case examines how the parser handles a list of registers using the `dim` element, where each
    register has a unique `displayName`. The `dim` and `dimIndex` elements are used to generate multiple instances
    of registers, and the parser must ensure that the correct `displayName` is applied to each instance based on
    its corresponding entry in the `dimIndex`. `svdconv` processes this case correctly, and the parser is expected
    to do the same, creating the appropriate registers with distinct `displayName` fields.

    **Expected Outcome:** The parser should successfully process the file and create two registers with the names
    `RegisterA` and `RegisterB`, using the `dimIndex` to distinguish between them. Both registers should have
    correct `addressOffset` values of `0x0` and `0x4` respectively, and a size of 32 bits. Additionally, the
    `displayName` for `RegisterA` should be "RegisterA", and for `RegisterB` it should be "RegisterB", matching
    their names and offsets.

    **Processable with svdconv:** yes
    """

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
def test_array_displayname_without_dim(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case verifies that the parser correctly identifies a misconfiguration where a `displayName` contains
    an expression marker (`[%s]`) without the corresponding `dim` element. In such cases, `svdconv` raises an
    error because the `displayName` expects a `dim` array to provide the necessary index substitutions. The parser
    should similarly detect this issue and raise an appropriate error, as the `displayName` cannot be processed
    without the `dim` element.

    **Expected Outcome:** The parser should raise an error indicating that an expression marker (`[%s]`) was found in
    the `displayName`, but no corresponding `dim` element was provided. This behavior mirrors the error raised by
    `svdconv` in such situations. The peripheral should not be created, and the parser should stop processing this
    file due to the configuration error.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("dim_handling/array_displayname_without_dim.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="Expression marker [%s] found in displayName but no <dim> specified",
)
def test_list_displayname_without_dim(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case verifies that the parser correctly identifies a misconfiguration where a `displayName` contains
    an expression marker (`%s`) without the corresponding `dim` element. In such cases, `svdconv` raises an error
    because the `displayName` expects a `dim` list to provide the necessary index substitutions. The parser should
    similarly detect this issue and raise an appropriate error, as the `displayName` cannot be processed without
    the `dim` element.

    **Expected Outcome:** The parser should raise an error indicating that an expression marker (`%s`) was found in
    the `displayName`, but no corresponding `dim` element was provided. This behavior mirrors the error raised by
    `svdconv` in such situations. The peripheral should not be created, and the parser should stop processing this
    file due to the configuration error.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("dim_handling/list_displayname_without_dim.svd")
