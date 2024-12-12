from svdsuite.model.parse import (
    SVDDevice,
    SVDPeripheral,
    SVDCluster,
    SVDRegister,
    SVDField,
    SVDEnumeratedValueContainer,
)
from svdsuite.resolve.graph import ResolverGraph
from svdsuite.resolve.graph_elements import ElementNode, ElementLevel, NodeStatus, EdgeType, PlaceholderNode


class GraphBuilder:
    def __init__(self, resolver_graph: ResolverGraph):
        self._resolver_graph = resolver_graph

    def construct_directed_graph(self, parsed_device: SVDDevice) -> ElementNode:
        root_node = ElementNode(
            name="Device",
            level=ElementLevel.DEVICE,
            status=NodeStatus.PROCESSED,
            parsed=parsed_device,
        )
        self._resolver_graph.add_root(root_node)
        self._constr_graph_peripherals(parsed_device.peripherals, root_node)

        return root_node

    def _constr_graph_peripherals(self, parsed_peripherals: list[SVDPeripheral], parent_node: ElementNode):
        for parsed_peripheral in parsed_peripherals:
            peripheral_node = ElementNode(
                name=parsed_peripheral.name,
                level=ElementLevel.PERIPHERAL,
                status=NodeStatus.UNPROCESSED,
                parsed=parsed_peripheral,
            )
            self._add_child_to_graph(peripheral_node, parent_node)
            self._add_placeholder_for_derived(peripheral_node)
            self._constr_graph_registers_clusters(parsed_peripheral.registers_clusters, peripheral_node)

    def _constr_graph_registers_clusters(
        self, parsed_registers_clusters: list[SVDCluster | SVDRegister], parent_node: ElementNode
    ):
        for parsed_register_cluster in parsed_registers_clusters:
            if isinstance(parsed_register_cluster, SVDCluster):
                cluster_node = ElementNode(
                    name=parsed_register_cluster.name,
                    level=ElementLevel.CLUSTER,
                    status=NodeStatus.UNPROCESSED,
                    parsed=parsed_register_cluster,
                )
                self._add_child_to_graph(cluster_node, parent_node)
                self._add_placeholder_for_derived(cluster_node)
                self._constr_graph_registers_clusters(parsed_register_cluster.registers_clusters, cluster_node)
            elif isinstance(parsed_register_cluster, SVDRegister):  # pyright: ignore[reportUnnecessaryIsInstance]
                register_node = ElementNode(
                    name=parsed_register_cluster.name,
                    level=ElementLevel.REGISTER,
                    status=NodeStatus.UNPROCESSED,
                    parsed=parsed_register_cluster,
                )
                self._add_child_to_graph(register_node, parent_node)
                self._add_placeholder_for_derived(register_node)
                self._constr_graph_fields(parsed_register_cluster.fields, register_node)

    def _constr_graph_fields(self, parsed_fields: list[SVDField], parent_node: ElementNode):
        for parsed_field in parsed_fields:
            field_node = ElementNode(
                name=parsed_field.name,
                level=ElementLevel.FIELD,
                status=NodeStatus.UNPROCESSED,
                parsed=parsed_field,
            )
            self._add_child_to_graph(field_node, parent_node)
            self._add_placeholder_for_derived(field_node)
            self._constr_graph_enum_containers(parsed_field.enumerated_value_containers, field_node)

    def _constr_graph_enum_containers(
        self, parsed_enum_containers: list[SVDEnumeratedValueContainer], parent_node: ElementNode
    ):
        for parsed_enum_container in parsed_enum_containers:
            enum_container_node = ElementNode(
                name=parsed_enum_container.name,
                level=ElementLevel.ENUMCONT,
                status=NodeStatus.UNPROCESSED,
                parsed=parsed_enum_container,
            )
            self._add_child_to_graph(enum_container_node, parent_node)
            self._add_placeholder_for_derived(enum_container_node)

    def _add_child_to_graph(self, child_node: ElementNode, parent_node: ElementNode):
        if parent_node.status == NodeStatus.PROCESSED:
            edge_type = EdgeType.CHILD_RESOLVED
        else:
            edge_type = EdgeType.CHILD_UNRESOLVED

        self._resolver_graph.add_element_child(parent_node, child_node, edge_type)

    def _add_placeholder_for_derived(self, child_node: ElementNode):
        assert not isinstance(child_node.parsed, SVDDevice)

        if child_node.parsed.derived_from is not None:
            placeholder_node = PlaceholderNode(derive_path=child_node.parsed.derived_from)
            self._resolver_graph.add_placeholder(placeholder_node, child_node)
