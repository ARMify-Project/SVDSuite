"""
For this feature, test cases cover scenarios where a derived cluster inherits properties from a base cluster, ensuring
correct behavior when values are inherited.
"""

from typing import Callable
import pytest

from svdsuite.process import ProcessException, ProcessWarning
from svdsuite.model.process import Device, Register, Cluster
from svdsuite.model.types import AccessType, ProtectionStringType


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_inheritance_backward_reference_same_scope(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case examines the functionality of cluster inheritance using the `derivedFrom` attribute,
    specifically when a derived cluster references a base cluster that has been defined earlier within the same
    scope. The SVD file contains two clusters: `ClusterA`, which serves as the base, and `ClusterB`, which derives
    its properties from `ClusterA`. The test verifies that `ClusterB` correctly inherits the settings of
    `ClusterA`, such as address offsets and register definitions, without requiring explicit redefinition. This
    allows for efficient reuse of configurations and consistency across similar clusters.

    **Expected Outcome:** The parser should successfully interpret the SVD file, recognizing `ClusterB` as a
    derivative of `ClusterA`. `ClusterB` should inherit all properties from `ClusterA`, including the register
    within it. The test should confirm that the derived cluster behaves exactly as if it were fully defined on its
    own, ensuring no loss of information or incorrect settings. The implementation must accurately parse and apply
    the inheritance mechanism, consistent with how `svdconv` processes the file.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_inheritance_forward_reference_same_scope(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case evaluates the functionality of cluster inheritance via the `derivedFrom` attribute when a
    derived cluster refers to a base cluster that is defined later in the same scope. Unlike backward references,
    this scenario involves the base cluster being declared after the derived cluster. This setup is used to ensure
    that the parser can correctly resolve forward references, allowing `ClusterA` to derive from `ClusterB`, even
    though `ClusterB` is defined later in the SVD file. `svdconv` cannot handle forward references within the same
    scope, leading to an error, but a robust parser should be capable of managing such cases without issues.

    **Expected Outcome:** The parser should successfully process the SVD file, correctly handling the forward
    reference so that `ClusterA` inherits all properties from `ClusterB`. This includes the register defined
    within the base cluster. The test should confirm that `ClusterA` behaves as though it were explicitly defined
    with the same settings as `ClusterB`, ensuring consistency and accurate inheritance. The implementation must
    be able to parse these forward references efficiently, overcoming the limitations observed in `svdconv`.

    **Processable with svdconv:** no
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_inheritance_backward_reference_different_scope(
    get_processed_device_from_testfile: Callable[[str], Device]
):
    """
    This test case evaluates how a parser handles cluster inheritance via the `derivedFrom` attribute when the
    derived cluster refers to a base cluster that is defined within a different peripheral. In this scenario,
    `ClusterA` from one peripheral acts as the base cluster, while a similarly named `ClusterA` in another
    peripheral inherits its properties. This setup is intended to confirm that cross-scope inheritance works
    correctly, ensuring that the derived cluster can access and copy properties from a base cluster, even when
    they reside within different scopes or peripherals.

    **Expected Outcome:** The parser should accurately resolve the `derivedFrom` reference across different scopes,
    allowing `ClusterA` in the second peripheral to inherit all the properties from `ClusterA` in the first
    peripheral. This includes settings such as size and any registers defined within the original cluster. The
    implementation should validate that properties are correctly inherited and applied to the derived cluster,
    ensuring consistency and accuracy. The parser's ability to handle this cross-scope inheritance efficiently is
    crucial, as `svdconv` processes these scenarios without issues.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_simple_inheritance_forward_reference_different_scope(
    get_processed_device_from_testfile: Callable[[str], Device]
):
    """
    This test case explores how a parser manages cluster inheritance using the `derivedFrom` attribute when a
    derived cluster refers to a base cluster defined later within a different peripheral. Unlike backward
    references, forward references imply that the parser must anticipate and correctly resolve a reference to a
    cluster that has not yet been defined, adding complexity to the inheritance mechanism. This setup checks
    whether the parser can seamlessly link the derived cluster to its base cluster, even when the base cluster
    appears later and exists within a different peripheral scope. `svdconv` cannot handle forward references
    within a different scope, leading to an error, but a robust parser should be capable of managing such cases
    without issues.

    **Expected Outcome:** The parser should successfully handle the `derivedFrom` reference, allowing `ClusterA` in
    the first peripheral to inherit from `ClusterA` defined in the second peripheral. It must accurately inherit
    all properties, including sizes and register definitions. The parser should ensure that cross-scope and
    forward references do not disrupt the resolution of inherited properties, maintaining consistent and accurate
    behavior.

    **Processable with svdconv:** no
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_value_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case focuses on the inheritance of properties within clusters when utilizing the `derivedFrom`
    attribute. Specifically, it examines how a derived cluster can inherit various attributes—such as description,
    alternate clusters, header structure names, access permissions, and reset configurations—from a base cluster.
    The goal is to ensure that the parser accurately handles the propagation of these values, maintaining
    consistency across derived clusters without requiring them to redefine attributes that are already specified
    in their base counterparts.

    **Expected Outcome:** The parser should successfully interpret the `derivedFrom` attribute and apply all the
    relevant properties from the base cluster to the derived cluster. For instance, `ClusterB` should inherit
    settings from `ClusterA`, including but not limited to description, access permissions, protection level, and
    reset values. The properties like `alternateCluster`, `headerStructName`, and size should also be correctly
    propagated, ensuring `ClusterB` maintains the same effective behavior as `ClusterA` unless explicitly
    overridden. Furthermore, nested structures within the clusters, such as registers, should also reflect
    inherited attributes, demonstrating the parser’s ability to resolve and apply complex inheritance patterns.
    This behavior mirrors the expected output of `svdconv`, which processes these scenarios correctly, reinforcing
    the parser's robustness in dealing with value inheritance via `derivedFrom`.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/value_inheritance.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], Cluster)
    assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
    assert device.peripherals[0].registers_clusters[0].description == "ClusterA description"
    assert device.peripherals[0].registers_clusters[0].alternate_cluster == "ClusterA"
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
    assert device.peripherals[0].registers_clusters[1].alternate_cluster == "ClusterA"
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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_override_behavior(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case examines how derived clusters can override specific properties inherited from their base
    cluster using the `derivedFrom` attribute. When a derived cluster redefines certain attributes, it should
    effectively replace the values that would otherwise be inherited.

    **Expected Outcome:** The parser should correctly handle scenarios where a derived cluster overrides properties
    inherited from a base cluster. For `ClusterA`, all attributes should match those defined in the base
    configuration, reflecting typical inheritance. However, `ClusterB`, while still inheriting from a similar
    base, should show overridden properties where explicitly defined. Attributes such as `alternate_cluster`,
    `header_struct_name`, and `protection` should reflect the customizations specified within `ClusterB`.
    Moreover, registers within `ClusterB` should inherit general properties but may also have some overridden
    settings, such as `size` or `access`. The parser must correctly interpret both inherited and redefined values,
    ensuring that `ClusterB` retains a consistent but modified behavior compared to `ClusterA`. This behavior
    mirrors what `svdconv` processes, ensuring that derived configurations accurately apply the specified
    overrides without causing any inconsistencies.

    **Processable with svdconv:** yes
    """

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
    assert device.peripherals[0].registers_clusters[0].alternate_cluster == "ClusterB"
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
    assert device.peripherals[0].registers_clusters[1].alternate_cluster == "ClusterA"
    assert device.peripherals[0].registers_clusters[1].header_struct_name == "HeaderStructName2"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x2
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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_multiple_inheritance_backward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case evaluates how the parser handles multiple levels of inheritance using the `derivedFrom`
    attribute. The scenario consists of three clusters: `ClusterA`, defined as the base cluster; `ClusterB`, which
    derives from `ClusterA`; and `ClusterC`, which in turn derives from `ClusterB`. The SVD file defines these
    clusters in a backward-compatible order, starting with `ClusterA` and then progressively building upon it with
    `ClusterB` and `ClusterC`. This setup tests the parser's ability to correctly inherit properties across
    multiple layers of derivation, ensuring that each derived cluster appropriately inherits all relevant
    attributes from its predecessors.

    **Expected Outcome:** The parser should successfully process the multiple inheritance chain, maintaining the
    correct properties throughout each level. `ClusterA` should be recognized as the base, with all its defined
    properties and a register named `RegisterA`. `ClusterB`, derived from `ClusterA`, should inherit all the base
    attributes and the `RegisterA` structure, located at a new offset, demonstrating that it has extended the
    base. Finally, `ClusterC` should inherit the cumulative properties from both `ClusterA` and `ClusterB`,
    further verifying the parser's capability to manage complex inheritance patterns across multiple derived
    entities. This behavior should mirror `svdconv`'s processing and ensure consistent, hierarchical inheritance.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_multiple_inheritance_forward_reference(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case assesses the parser's handling of complex inheritance structures where the base cluster
    (`ClusterC`) is referenced by derived clusters (`ClusterB` and `ClusterA`) in a forward manner. In this setup,
    the SVD file defines `ClusterA` first, followed by `ClusterB`, and finally `ClusterC`, which serves as the
    base for the other clusters. The `derivedFrom` attribute is used to create a chain of inheritance starting
    from `ClusterC` as the base, with `ClusterB` inheriting from it, and `ClusterA` inheriting from `ClusterB`.
    This configuration challenges the parser to correctly resolve references even when the base entity appears
    later in the file.

    **Expected Outcome:** The parser should be able to process the forward references correctly, linking each derived
    cluster back to its base cluster despite the forward order of definition. `ClusterA`, appearing first in the
    SVD file, should correctly inherit properties from `ClusterB`, which in turn inherits from `ClusterC`. Each
    derived cluster should maintain the properties defined in its base and apply them consistently. `ClusterA`,
    `ClusterB`, and `ClusterC` should all include the expected attributes, registers, and configurations inherited
    through the chain, confirming that the parser effectively handles forward inheritance. This contrasts with
    `svdconv`, which fails to process such forward references, making robust support for this feature a valuable
    enhancement in the parser.

    **Processable with svdconv:** no
    """

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
    """
    This test case examines how the parser handles scenarios where clusters are involved in circular inheritance.
    In this setup, `ClusterA`, which is defined first in the SVD file, is set to inherit from `ClusterB`.
    Conversely, `ClusterB` is also configured to inherit from `ClusterA`. This creates a loop of inheritance,
    which is logically invalid and should not be allowed. Proper parsing should identify this circular reference
    and raise an error, preventing further processing. Circular inheritance could lead to infinite loops or
    unresolved dependencies if not handled correctly.

    **Expected Outcome:** The parser should detect the circular inheritance between `ClusterA` and `ClusterB` and
    raise an appropriate error, indicating that circular references are not supported. Unlike some other complex
    inheritance scenarios, where forward or backward references might be resolved by proper linkage, circular
    inheritance represents a fundamental logical flaw.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/circular_inheritance.svd")


@pytest.mark.xfail(strict=True, raises=ProcessException, reason="Nested inheritance is not supported")
def test_nested_cluster_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case explores the scenario where a cluster contains another cluster, and the inner cluster attempts
    to inherit properties from its parent using the `derivedFrom` attribute. In the provided SVD file, `ClusterB`
    is nested within `ClusterA`, and it is set to inherit from `ClusterA`. This creates a situation where a
    cluster is attempting to derive from its own parent, forming a nested inheritance pattern that is logically
    flawed. Proper parsing should recognize that this setup is invalid because nested clusters should not inherit
    from their parent clusters in this manner. Attempting to resolve such inheritance could lead to recursive
    loops or other unintended behavior, making it essential for the parser to detect and handle this case
    appropriately.

    **Expected Outcome:** The parser should raise an error upon encountering this nested inheritance, clearly
    indicating that this pattern is not supported. The parser's robustness should ensure that it does not attempt
    to process the inheritance further, as doing so could result in a circular dependency or recursive issues.
    Unlike `svdconv`, which crashes with a segmentation fault (SigSegV) when encountering such a configuration, a
    well-implemented parser should gracefully handle this invalid setup by issuing a clear error message,
    preventing further processing of the file.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/nested_cluster_inheritance.svd")


@pytest.mark.xfail(
    strict=True,
    raises=ProcessException,
    reason="RegisterA is already defined in ClusterA and cannot be inherited because it has the same name",
)
def test_register_inheritance_same_name(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case addresses a situation where a derived cluster attempts to inherit a register from a base
    cluster, but there is a naming conflict because the derived cluster defines a register with the same name as
    the one it is inheriting. In the SVD file, `ClusterA` defines a register named `RegisterA`, and `ClusterB`,
    which is derived from `ClusterA`, also defines its own `RegisterA`. Since `ClusterB` inherits from `ClusterA`,
    this results in a conflict where `RegisterA` is effectively defined twice within `ClusterB`. While `svdconv`
    correctly identifies this issue and raises an error, a robust parser must also handle this case by issuing an
    appropriate error message.

    **Expected Outcome:** The parser should raise an error indicating that `RegisterA` is already defined in
    `ClusterA`, and therefore cannot be inherited by `ClusterB` because it has the same name. The error should be
    explicit, preventing further processing and avoiding any ambiguity around the derived cluster's register
    structure.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/register_inheritance_same_name.svd")


def test_register_inheritance_same_address(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test scenario evaluates how a derived cluster handles cases where it inherits a register from a base
    cluster, and the derived cluster also defines another register at the same address offset. In the SVD file,
    `ClusterA` defines `RegisterA` at address offset `0x0`, and `ClusterB`, which is derived from `ClusterA`, also
    defines `RegisterB` at the same address offset `0x0`. As a result, both `RegisterA` (inherited from
    `ClusterA`) and `RegisterB` (defined within `ClusterB`) occupy the same address space within `ClusterB`.
    `svdconv` processes this case without raising a hard error but issues a warning to highlight the overlap,
    because of [compatibility reasons](https://github.com/Open-CMSIS-Pack/devtools/blob/44643999691347946562c526fc
    0474194f865c74/tools/svdconv/SVDModel/src/SvdPeripheral.cpp#L721). For a parser designed to work with both new
    and old SVD files, it is recommended to allow registers with the same addresses but issue a warning to the
    user.

    **Expected Outcome:** The parser should process the file successfully but must issue a warning indicating that
    `RegisterB` is assigned the same address as `RegisterA` due to inheritance. The warning should explicitly
    state the address conflict, providing enough information for developers to recognize and address any
    unintended overlaps in the register configurations.

    **Processable with svdconv:** yes
    """

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
    """
    This test case evaluates how a derived cluster manages address space conflicts when it inherits registers from
    a base cluster and defines additional registers that cause overlapping addresses. In the provided SVD file,
    `ClusterA` defines `RegisterA` at address offset `0x0` with a size of 32 bits, while `ClusterB`, which is
    derived from `ClusterA`, also defines `RegisterB` at address offset `0x2` with a size of 16 bits. Because of
    their sizes, `RegisterB` ends up overlapping with the address space occupied by `RegisterA`. Older versions of
    `svdconv` did not recognize this behavior and therefore, newer versions issue a warning instead of an error to
    inform users of the potential address conflict. A parser that aims to maintain compatibility with older SVD
    files should similarly allow registers with overlapping addresses while issuing a clear warning to alert users
    of the overlap. This approach ensures that backward compatibility is maintained, but it also makes developers
    aware of potential problems that could arise from such configurations.

    **Expected Outcome:** The parser should successfully process the SVD file, but it must issue a warning indicating
    that `RegisterB` overlaps with `RegisterA` within `ClusterB`. The warning should clearly state the address
    conflict and provide details about the overlapping addresses and sizes. This behavior mirrors that of
    `svdconv`, ensuring that the parser maintains backward compatibility while still alerting developers to
    potential configuration issues that could cause unexpected behavior in hardware interaction.

    **Processable with svdconv:** yes
    """

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
    """
    This test case examines how the parser handles situations where two clusters, `ClusterA` and `ClusterB`, are
    defined at the same address offset within a peripheral. In the provided SVD file, both clusters are located at
    address offset `0x0`, which leads to potential address conflicts. Older versions of `svdconv` did not
    recognize this behavior and for compatibility, newer versions issue a warning instead of an error to inform
    users of the potential address conflict. A modern parser should replicate this behavior by allowing the SVD
    file to be processed but should issue a warning to alert the user of the address overlap.

    **Expected Outcome:** The parser should successfully parse the SVD file, identifying both `ClusterA` and
    `ClusterB` at the same address offset (`0x0`). However, a warning should be issued to inform the user that
    `ClusterB` shares the same address as `ClusterA`, indicating a potential conflict.

    **Processable with svdconv:** yes
    """

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
    """
    This test case evaluates how the parser handles overlapping clusters within a peripheral, where `ClusterB` is
    derived from `ClusterA` but is assigned an address offset that causes an overlap. In the SVD file, `ClusterA`
    is defined at address offset `0x0` with a size of `16`, and `ClusterB`, derived from `ClusterA`, is placed at
    address offset `0x1` with a size of `8`. This configuration leads to overlapping address ranges for these
    clusters. While `svdconv` processes this file without detecting the overlap, this behavior appears to be a
    bug. Ideally, a parser should issue a warning to alert the user of the overlap, ensuring that any unintended
    address conflicts are recognized and can be corrected.

    **Expected Outcome:** The parser should correctly process the SVD file, identifying both `ClusterA` and `ClusterB`
    while issuing a warning to indicate that their address ranges overlap. Specifically, `ClusterA` occupies the
    range starting at `0x0` for `16` bytes, and `ClusterB` starts at `0x1` with a size of `8`, causing the two
    clusters to share overlapping addresses. The warning should provide clear information about which clusters are
    affected and the nature of the overlap, giving users the necessary insights to address any configuration
    issues in their SVD definitions.

    **Processable with svdconv:** yes
    """

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


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_alternate_cluster(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case assesses the correct handling of the `alternateCluster` feature in the SVD file, which allows
    one cluster to act as an alternate version of another. In this scenario, `ClusterB` is derived from `ClusterA`
    and is marked as an alternate cluster by specifying `ClusterA` in the `<alternateCluster>` tag. Both clusters
    share the same address offset (`0x0`), implying that they can be used interchangeably, depending on the use
    case.

    **Expected Outcome:** The parser should correctly interpret `ClusterB` as an alternate of `ClusterA`. It should
    process the `derivedFrom` attribute, allowing `ClusterB` to inherit all characteristics from `ClusterA`.
    Additionally, the parser should recognize the `<alternateCluster>` tag and confirm that `ClusterB` is
    designated as an alternate of `ClusterA`. Both clusters should be treated as residing at the same address
    offset (`0x0`), with `ClusterA` having no `alternateCluster` association, while `ClusterB` explicitly
    references `ClusterA`. The parsing process should proceed without errors or warnings, consistent with the
    behavior of `svdconv`, which correctly handles this feature.

    **Processable with svdconv:** yes
    """

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
    """
    This test case evaluates a scenario where a cluster attempts to derive from itself, creating an invalid
    configuration. In the SVD file, `ClusterA` is defined with a `derivedFrom` attribute pointing to its own name.
    Such configurations should be detected as erroneous because a cluster cannot logically inherit properties from
    itself. This kind of self-reference should lead to a parsing error.

    **Expected Outcome:** The parser should detect the invalid self-referential inheritance and raise an error,
    indicating that a cluster cannot derive from itself. This ensures that the system handles such configurations
    correctly by stopping further processing and informing the user of the issue.

    **Processable with svdconv:** no
    """

    get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/derive_from_self.svd")


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_size_inheritance(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test case verifies that the `size` attribute is correctly inherited when using `derivedFrom` on clusters
    and registers. In the provided setup, `ClusterB` is derived from `ClusterA`, which has a specified `size` of 8
    for `RegisterA`. Since `RegisterB` in `ClusterB` does not define its own `size`, it should inherit the `size`
    attribute from `RegisterA` in `ClusterA`. This test confirms that the parser correctly applies this
    inheritance, ensuring consistent `size` values across derived elements without explicit redefinition.

    **Expected Outcome:** The parser should successfully inherit the `size` attribute for `RegisterB`, resulting in
    `ClusterB` and its registers having the same size attributes as the elements in `ClusterA`. Specifically,
    `RegisterB` in `ClusterB` should inherit a `size` of 8.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile("cluster_inheritance_via_derivedfrom/size_inheritance.svd")

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2
    assert device.peripherals[0].size == 32

    assert isinstance(device.peripherals[0].registers_clusters[1], Cluster)
    assert device.peripherals[0].registers_clusters[1].name == "ClusterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert len(device.peripherals[0].registers_clusters[1].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[0], Register)
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].name == "RegisterA"
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].address_offset == 0x0
    assert device.peripherals[0].registers_clusters[1].registers_clusters[0].size == 8

    assert isinstance(device.peripherals[0].registers_clusters[1].registers_clusters[1], Register)
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].registers_clusters[1].size == 32
