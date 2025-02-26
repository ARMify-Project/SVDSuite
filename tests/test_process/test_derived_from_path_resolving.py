"""
The `derivedFrom` attribute in SVD is a powerful feature that allows reuse of elements (like registers, clusters, and
fields) across different parts of a peripheral definition. It is used to reference existing definitions and inherit
their attributes without having to redefine them. This reduces redundancy and helps maintain consistency within complex
device descriptions.

The `derivedFrom` path resolving mechanism is crucial in determining how references are processed. Paths can vary in
complexity, ranging from simple names to more intricate, nested references within clusters. A robust parser
implementation must correctly interpret these paths, supporting multiple levels of hierarchy while handling any scope
ambiguities. Additionally, the parser should gracefully handle errors when the paths are incorrect, issuing clear
diagnostic messages to aid debugging.

According to [this](https://github.com/Open-CMSIS-Pack/devtools/issues/815#issuecomment-1495681319), the deriving
algorithm works as follows:

1. **Initialization:** - Split the deriving path (the string in the `derivedFrom` attribute) by `.` and store it in
array $P$. For example, if the path is `x.y.z`, then $P_0 = \text{x}$, $P_1 = \text{y}$, and $P_2 = \text{z}$. - Set
index $i = 0$. - Store the deriving element (the element with the `derivedFrom` attribute) in variable $D$. - Store the
deriving element $D$ in variable $C$ (i.e., $C = D$). - Get the parent of the current element $C$ and set it as the
current node (i.e., $C = C.\text{parent()}$).

2. **Search in the current scope:** - For each child of $C$, do the following: - Ignore the child if it is the same as
$D$, to not match the deriving element itself. - Check if the child’s name matches $P_i$. - If a match is found: 1.
Check if $P_{i+1}$ exists (i.e., there is a next element in the path). - **If $P_{i+1}$ does not exist:** - Verify if
the child has the same type as $D$ (e.g., both are registers): - **If it does,** the base element is found. Stop the
search. - **If it does not,** continue the algorithm (go to step 3). - **If $P_{i+1}$ exists:** - Increment $i$ (i.e.,
move to the next part of the path). - Set $C$ to the child element that matched $P_i$ and proceed to step 2 to continue
searching down the hierarchy.

3. **Fallback search at the top level (peripherals):** - If no match was found within the current scope, start searching
from the top-level container (referred to as `peripherals`): - Set $C$ to the `peripherals` container, which is the
container that holds all peripherals. - Set $i = 0$ (start over from the beginning of the path). - Repeat step 2 from
the `peripherals` container: - Check if there is a child of $C$ that matches $P_i$. - Proceed with the same logic as in
step 2, following the path $P$.

4. **Termination:** - If the algorithm finds a match at any point, stop the search and return the base element. - If no
match is found after searching through both the local scope and the top-level container, conclude that the base element
could not be found.

In this chapter, we focus on test cases that validate the path resolving mechanism of `derivedFrom`. Each test case
involves substituting the `derivedFrom` path with multiple variations, and then testing whether the parser can correctly
process or reject each of these paths. Importantly, each test file is not a single test case; instead, each test file
contains exactly one `derivedFrom` attribute, and multiple paths are tested against it. This approach allows us to
thoroughly validate path resolving in different scenarios using the same base SVD setup.

In the provided implementation examples, the `pytest` parameterization feature is utilized to test these paths. Paths
that are expected to be valid and processable are not marked with `pytest`'s xmark, while paths that are expected to
raise errors are marked with `pytest.mark.xfail`. Furthermore, test cases which are marked with `pytest.mark.xfail` are
not processable with `svdconv`, whereas the others can be processed with `svdconv` if not statet otherwise.
"""

from typing import Callable
import pytest

from svdsuite.process import Process, ProcessException
from svdsuite.model.process import Register, Cluster


@pytest.mark.parametrize(
    "path",
    [
        pytest.param(
            "PeripheralA.ClusterA.ClusterB.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "ClusterA.ClusterB.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
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
def test_test_setup_1(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    """
    This test setup explores `derivedFrom` path resolution within a single peripheral that contains nested
    clusters. The setup verifies whether the parser can correctly resolve paths to registers located within
    different levels of nested clusters. Additionally, it ensures that invalid paths are properly flagged as
    errors.

    **Expected Outcome:** Paths that correctly reference the target should be processed successfully. Invalid paths
    should raise an error, and the parser should provide clear diagnostics indicating the issue. This mimics
    `svdconv`'s behavior.

    **Processable with svdconv:** partly
    """

    file_name = "derivedfrom_path_resolving/test_setup_1.svd"

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
        pytest.param(  # can't be processed with svdconv
            "SameA.SameA.SameA.SameA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(  # can't be processed with svdconv
            "SameA.SameA.SameA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
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
def test_test_setup_2(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    """
    This test setup explores `derivedFrom` path resolution within a single peripheral that contains nested
    clusters and each element is named with the same name. Without the derivation, `svdconv` would be able to
    parse the file without any warnings or erros. However, `svdconv` contains a [known
    bug](https://github.com/Open-CMSIS-Pack/devtools/issues/815#issuecomment-1495681319), which prevents name
    resolving, if a parent has the same name as the child. The setup verifies whether the parser can correctly
    resolve paths to registers located within different levels of nested clusters, if they have the same names.
    Additionally, it ensures that invalid paths are properly flagged as errors.

    **Expected Outcome:** Paths that correctly reference the target should be processed successfully. Invalid paths
    should raise an error, and the parser should provide clear diagnostics indicating the issue.

    **Processable with svdconv:** no
    """

    file_name = "derivedfrom_path_resolving/test_setup_2.svd"

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


@pytest.mark.parametrize(
    "path",
    [
        pytest.param(
            "ElementA.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "ElementA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
    ],
)
def test_test_setup_3(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    """
    In this test setup, the path `ElementA.RegisterA` can be resolved in multiple valid ways. Depending on how the
    algorithm is implemented, it could return `RegisterA` located within the `ElementA` peripheral or the
    `RegisterA` within `PeripheralA`. Since the parser should implement the same algorithm as `svdconv`, the
    expected behavior is that `RegisterA` within `PeripheralA` is found. This is because the search process first
    looks within the same scope, and if no match is found, it expands to all peripherals. Ultimately, `RegisterB`
    should inherit from `RegisterA` located in `PeripheralA`, meaning it must include `FieldB` instead of
    `FieldA`.

    **Expected Outcome:** Paths that correctly reference the target should be processed successfully. Invalid paths
    should raise an error, and the parser should provide clear diagnostics indicating the issue.

    **Processable with svdconv:** partly
    """

    file_name = "derivedfrom_path_resolving/test_setup_3.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"PATH", path.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 2

    assert device.peripherals[1].name == "PeripheralA"
    assert len(device.peripherals[1].registers_clusters) == 2

    assert isinstance(device.peripherals[1].registers_clusters[1], Register)
    assert device.peripherals[1].registers_clusters[1].name == "RegisterB"
    assert len(device.peripherals[1].registers_clusters[1].fields) == 1
    assert device.peripherals[1].registers_clusters[1].fields[0].name == "FieldB"


@pytest.mark.parametrize(
    "path",
    [
        pytest.param(
            "ElementA.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "ElementB.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "ElementA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
    ],
)
def test_test_setup_4(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    """
    In this test setup, the path `ElementA.RegisterA` can be resolved in multiple valid ways, similar to the
    previous setup. However, this time there is an additional `dim` configuration, which creates two clusters
    `ElementA` and `ElementB` within `PeripheralA`. Depending on how the algorithm is implemented, it could return
    `RegisterA` from either the `ElementA` peripheral or of the `ElementA` cluster within `PeripheralA`. Since the
    parser should follow the same resolution rules as `svdconv`, the expected behavior is that `RegisterA` within
    `PeripheralA` is found. The search should prioritize finding matches within the same scope first, and only
    expand to all peripherals if no match is found. Ultimately, `RegisterB` should inherit from `RegisterA` within
    `PeripheralA`, and it must therefore include `FieldB` instead of `FieldA`.

    **Expected Outcome:** Paths that correctly reference the target should be processed successfully. Invalid paths
    should raise an error, and the parser should provide clear diagnostics indicating the issue.

    **Processable with svdconv:** partly
    """

    file_name = "derivedfrom_path_resolving/test_setup_4.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"PATH", path.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 2

    assert device.peripherals[1].name == "PeripheralA"
    assert len(device.peripherals[1].registers_clusters) == 3

    assert isinstance(device.peripherals[1].registers_clusters[2], Register)
    assert device.peripherals[1].registers_clusters[2].name == "RegisterB"
    assert len(device.peripherals[1].registers_clusters[2].fields) == 1
    assert device.peripherals[1].registers_clusters[2].fields[0].name == "FieldB"


@pytest.mark.parametrize(
    "path",
    [
        pytest.param(
            "PeripheralA.Cluster%s.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "PeripheralA.ClusterA.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "PeripheralA.ClusterB.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
    ],
)
def test_test_setup_5(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    """
    Elements that use `dim` can be referenced in two ways: either by their name before the `dim` expansion (with
    `%s` within the name or `[%s]` at the end) or by their resolved name after the `dim` expansion. This test
    setup examines both methods of referencing `dim`-based elements. The test verifies whether the parser
    correctly identifies paths using both the pre-expansion placeholder (`Cluster%s`) and the fully expanded names
    (`ClusterA`, `ClusterB`). Paths that correctly reference the target elements should be processed without
    errors, while incorrect paths should trigger clear diagnostic messages. This setup ensures that the parser
    handles `dim`-expanded elements flexibly, similar to how `svdconv` resolves these references.

    **Expected Outcome:** Paths that correctly reference the target should be processed successfully. Invalid paths
    should raise an error, and the parser should provide clear diagnostics indicating the issue.

    **Processable with svdconv:** partly
    """

    file_name = "derivedfrom_path_resolving/test_setup_5.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"PATH", path.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 2

    assert device.peripherals[1].name == "PeripheralB"
    assert len(device.peripherals[1].registers_clusters) == 1
    assert isinstance(device.peripherals[1].registers_clusters[0], Register)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert len(device.peripherals[1].registers_clusters[0].fields) == 1
    assert device.peripherals[1].registers_clusters[0].fields[0].name == "FieldA"


@pytest.mark.parametrize(
    "path",
    [
        pytest.param(
            "PeripheralA.ClusterA.ClusterB.RegisterA.FieldA.FieldAEnumeratedValue",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "ClusterA.ClusterB.RegisterA.FieldA.FieldAEnumeratedValue",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "ClusterB.RegisterA.FieldA.FieldAEnumeratedValue",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "RegisterA.FieldA.FieldAEnumeratedValue",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "FieldA.FieldAEnumeratedValue",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "FieldAEnumeratedValue",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
    ],
)
def test_test_setup_6(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    """
    This test setup examines how the parser handles resolving paths for enumerated values within nested clusters.

    **Expected Outcome:** Paths that correctly reference the target should be processed successfully. Invalid paths
    should raise an error, and the parser should provide clear diagnostics indicating the issue.

    **Processable with svdconv:** partly
    """

    file_name = "derivedfrom_path_resolving/test_setup_6.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"PATH", path.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
    assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
    assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], Cluster)
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "ClusterB"
    assert len(device.peripherals[0].registers_clusters[0].registers_clusters[0].registers_clusters) == 1
    registera = device.peripherals[0].registers_clusters[0].registers_clusters[0].registers_clusters[0]
    assert isinstance(registera, Register)
    assert registera.name == "RegisterA"
    assert len(registera.fields) == 2

    assert registera.fields[0].name == "FieldA"
    assert len(registera.fields[0].enumerated_value_containers) == 1
    assert registera.fields[0].enumerated_value_containers[0].name == "FieldAEnumeratedValue"
    assert len(registera.fields[0].enumerated_value_containers[0].enumerated_values) == 2

    assert registera.fields[1].name == "FieldB"
    assert len(registera.fields[1].enumerated_value_containers) == 1
    assert registera.fields[1].enumerated_value_containers[0].name == "FieldAEnumeratedValue"
    assert len(registera.fields[1].enumerated_value_containers[0].enumerated_values) == 2


@pytest.mark.parametrize(
    "path",
    [
        pytest.param(
            "PeripheralA.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "PeripheralB.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "PeripheralC.RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "PeripheralA.RegisterB",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "PeripheralB.RegisterB",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
    ],
)
def test_test_setup_7(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    """
    This test setup focuses on how the parser resolves `derivedFrom` paths when dealing with registers that have
    `alternateGroup` attributes. The `alternateGroup` is used to group registers that can function as alternatives
    to each other, and this test ensures that the parser correctly interprets and differentiates these alternate
    groups during path resolution. In this setup, `RegisterA` in `PeripheralB` is marked with an `alternateGroup`
    named `RegisterX`, while the same-named register in `PeripheralA` does not have this attribute. The goal is to
    verify that when the parser encounters a path pointing to `PeripheralB.RegisterA`, it can correctly identify
    `RegisterA` and handle the `alternateGroup` reference. Paths that explicitly specify `RegisterA_RegisterX`
    should resolve to `PeripheralB.RegisterA`, reflecting its alternate group, while paths that point to
    `PeripheralA.RegisterA` should reference the original register without any alternate association. `svdconv`
    can't resolve `alternateGroup` paths, if they are named equal as a element outside of the alternate group. A
    robust parser should be able to do so.

    **Expected Outcome:** Paths that correctly reference the target should be processed successfully. Invalid paths
    should raise an error, and the parser should provide clear diagnostics indicating the issue.

    **Processable with svdconv:** partly
    """

    file_name = "derivedfrom_path_resolving/test_setup_7.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"PATH", path.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 3

    assert device.peripherals[2].name == "PeripheralC"
    assert len(device.peripherals[2].registers_clusters) == 1
    assert isinstance(device.peripherals[2].registers_clusters[0], Register)
    assert device.peripherals[2].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[2].registers_clusters[0].description == "PeripheralA_RegisterA"


@pytest.mark.parametrize(
    "path",
    [
        pytest.param(
            "ClusterA.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "ClusterB.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "PeripheralA.ClusterA.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "PeripheralA.ClusterB.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
    ],
)
def test_test_setup_8(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    """
    This test setup examines how the parser resolves `derivedFrom` references when inheritance cascades within
    clusters, specifically focusing on paths that ultimately reference a register created through inheritance.
    Here, `RegisterA` is initially defined within `ClusterA`. The second cluster, `ClusterB`, inherits properties
    from `ClusterA`, effectively creating an inherited version of `RegisterA` within `ClusterB`. Thus, while
    `RegisterA` is not explicitly present in `ClusterB` in the original SVD file, it becomes accessible there due
    to inheritance.

    **Expected Outcome:** Paths that correctly reference the target should be processed successfully. Invalid paths
    should raise an error, and the parser should provide clear diagnostics indicating the issue.

    **Processable with svdconv:** partly
    """

    file_name = "derivedfrom_path_resolving/test_setup_8.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"PATH", path.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 3

    assert device.peripherals[0].registers_clusters[2].name == "RegisterC"
    assert device.peripherals[0].registers_clusters[2].address_offset == 0xC
    assert device.peripherals[0].registers_clusters[2].size == 32


@pytest.mark.parametrize(
    "path",
    [
        pytest.param(
            "ClusterA.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "ClusterB.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "PeripheralA.ClusterA.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "PeripheralA.ClusterB.RegisterA",
            marks=pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning"),
        ),
        pytest.param(
            "RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
    ],
)
def test_test_setup_9(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    """
    Same as Test Setup 8, but with a forward reference.

    **Expected Outcome:** Paths that correctly reference the target should be processed successfully. Invalid paths
    should raise an error, and the parser should provide clear diagnostics indicating the issue.

    **Processable with svdconv:** partly
    """

    file_name = "derivedfrom_path_resolving/test_setup_9.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"PATH", path.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 3

    assert device.peripherals[0].registers_clusters[2].name == "RegisterC"
    assert device.peripherals[0].registers_clusters[2].description == "RegisterA description"
    assert device.peripherals[0].registers_clusters[2].address_offset == 0xC
    assert device.peripherals[0].registers_clusters[2].size == 32
