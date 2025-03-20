from typing import cast, TYPE_CHECKING
import copy

from svdsuite.resolve.graph import ResolverGraph
from svdsuite.resolve.graph_builder import GraphBuilder
from svdsuite.resolve.graph_elements import ElementNode, PlaceholderNode, NodeStatus, EdgeType, ElementLevel
from svdsuite.resolve.exception import (
    ResolveException,
    ResolverGraphException,
    EnumeratedValueContainerException,
    LoopException,
    CycleException,
    UnprocessedNodesException,
)
from svdsuite.model.type_alias import (
    IntermediatePeripheralTypes,
    IntermediateDimablePeripheralTypes,
    ParsedDimablePeripheralTypes,
    ParsedPeripheralTypes,
)
from svdsuite.resolve.logger import ResolverLogger
from svdsuite.model.parse import (
    SVDDevice,
    SVDPeripheral,
    SVDCluster,
    SVDRegister,
    SVDField,
    SVDEnumeratedValueContainer,
)
from svdsuite.model.process import (
    IDevice,
    IPeripheral,
    ICluster,
    IRegister,
    IField,
)
from svdsuite.model.types import EnumUsageType

if TYPE_CHECKING:
    from svdsuite.process import Process


class Resolver:
    def __init__(self, process: "Process", resolver_logging_file_path: None | str):
        self._process = process
        self._resolver_graph = ResolverGraph()
        self._root_node_: None | ElementNode = None
        self._logger = ResolverLogger(resolver_logging_file_path, self._resolver_graph)
        self._peripherals_resolved: None | list[IPeripheral] = None

    @property
    def _root_node(self) -> ElementNode:
        if self._root_node_ is None:
            raise ResolveException("Root node is not set")

        return self._root_node_

    def resolve_peripherals(self, parsed_device: SVDDevice) -> list[IPeripheral]:
        self._initialization(parsed_device)

        self._logger.log_repeating_steps_start()
        previous_nodes: list[ElementNode] = []
        while True:
            self._logger.log_round_start()

            self._resolve_placeholders()
            processable_nodes = self._get_topological_sorted_processable_nodes()

            if not processable_nodes:
                break

            if processable_nodes == previous_nodes:
                self._logger.log_loop_detected()
                raise LoopException("Stuck in a loop, the same elements are being processed repeatedly")

            previous_nodes = processable_nodes

            for node in processable_nodes:
                self._process_node(node)

            self._logger.log_round_end()

        self._logger.log_repeating_steps_finished()

        if self._resolver_graph.get_unprocessed_nodes():
            raise UnprocessedNodesException(
                f"Not all nodes were processed. Unresolved placeholders: {self._get_unresolved_placeholders_info()}"
            )

        self._finalize_processing()

        if self._peripherals_resolved is None:
            raise ResolveException("Peripherals not resolved")

        return self._peripherals_resolved

    def _initialization(self, parsed_device: SVDDevice):
        graph_builder = GraphBuilder(self._resolver_graph)
        self._root_node_ = graph_builder.construct_directed_graph(parsed_device)
        self._logger.log_init_constructed_graph()

        self._ensure_accurate_parent_child_relationships_for_placeholders()
        self._logger.log_parent_child_relationships_for_placeholders()

    def _resolve_placeholders(self):
        for placeholder in list(self._resolver_graph.get_placeholders()):  # copy to avoid modifying list while iter.
            self._resolve_placeholder(placeholder)

        self._logger.log_resolve_placeholder_finished()

    def _get_topological_sorted_processable_nodes(self) -> list[ElementNode]:
        processable_nodes = self._find_processable_nodes()
        topological_sorted_nodes = self._resolver_graph.get_topological_sorted_nodes(processable_nodes)
        self._logger.log_processable_elements(topological_sorted_nodes)

        return topological_sorted_nodes

    def _get_unresolved_placeholders_info(self) -> str:
        return ";".join(
            f"Element: '{node.name}' Level: {node.level}, derive_from_str: {placeholder.derive_path}"
            for node, placeholder in (
                (self._resolver_graph.get_placeholder_child(placeholder), placeholder)
                for placeholder in self._resolver_graph.get_placeholders()
            )
        )

    def _finalize_processing(self):
        self._resolver_graph.bottom_up_node_traversal(self._finalize_node)

    def _get_derived_from_base_node(self, derived_node: ElementNode) -> ElementNode:
        base_node = self._resolver_graph.get_base_element_node(derived_node)

        if base_node is None:
            raise ResolveException(f"Base node not found for node '{derived_node.name}'")

        if derived_node.level != base_node.level:
            raise ResolveException(
                f"Node '{derived_node.name}' and its base node '{base_node.name}' have different levels"
            )

        if isinstance(base_node.processed_or_none, IDevice):
            raise ResolveException("Base node can't be a Device")

        return base_node

    def _process_enumerated_value_container_node(self, node: ElementNode, base_node: None | ElementNode):
        # if base_node_id is not None, update the node with the base node's parsed attribute (copy from base)
        if base_node is not None:
            node.parsed = cast(SVDEnumeratedValueContainer, base_node.parsed)

            # remove the derive edge
            self._resolver_graph.remove_edge(base_node, node)

            # replicate the base node's descendants as descendants of current node
            self._resolver_graph.replicate_descendants(base_node, node)

        # update node
        node.status = NodeStatus.PROCESSED

    def _update_node(
        self,
        node: ElementNode,
        base_node: None | ElementNode,
        processed: IntermediatePeripheralTypes,
        is_dim_template: bool = False,
    ):
        # if derived, remove the derive edge and replicate the base node's descendants as descendants of current node
        if base_node is not None:
            # remove the derive edge
            self._resolver_graph.remove_edge(base_node, node)

            # replicate the base node's descendants as descendants of current node
            self._resolver_graph.replicate_descendants(base_node, node)

        # update node
        node.status = NodeStatus.PROCESSED
        node.processed = processed
        if is_dim_template:
            node.is_dim_template = True

        # update outgoing CHILD_UNRESOLVED edges to CHILD_RESOLVED
        for child in self._resolver_graph.get_element_childrens(node):
            self._resolver_graph.update_edge(node, child, EdgeType.CHILD_RESOLVED)

    def _update_dim_node(
        self,
        node: ElementNode,
        base_node: None | ElementNode,
        processed_elements: list[IntermediateDimablePeripheralTypes],
        processed_dim_element: IntermediateDimablePeripheralTypes,
    ):
        # update dim element itself (must be called before the new nodes are created in the next step)
        self._update_node(node, base_node, processed_dim_element, is_dim_template=True)

        # _ElementNode has one parent, except parents are also dim nodes
        parents = self._resolver_graph.get_element_parents(node)

        # create new nodes
        new_nodes: list[ElementNode] = []
        for parent in parents:
            for processed_element in processed_elements:
                new_node = ElementNode(
                    name=processed_element.name,
                    level=node.level,
                    status=NodeStatus.PROCESSED,
                    parsed=node.parsed,
                    processed=processed_element,
                )
                self._resolver_graph.add_element_child(parent, new_node, EdgeType.CHILD_RESOLVED)
                new_nodes.append(new_node)

        # create edges to childs
        for new_node in new_nodes:
            for child in self._resolver_graph.get_element_childrens(node):
                self._resolver_graph.add_edge(new_node, child, EdgeType.CHILD_RESOLVED)

    def _find_processable_nodes(self) -> list[ElementNode]:
        not_allowed_edge_types = {
            EdgeType.PLACEHOLDER,
        }

        result: list[ElementNode] = []
        visited: set[ElementNode] = set()
        stack: list[ElementNode] = []

        for node in self._resolver_graph.get_unprocessed_root_nodes():
            stack.append(node)

        # iterative depth search
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)

            if self._resolver_graph.has_incoming_edge_of_types(node, not_allowed_edge_types):
                continue

            result.append(node)

            for child in self._resolver_graph.get_element_childrens(node):
                stack.append(child)

        return result

    def _resolve_placeholder(self, placeholder: PlaceholderNode):
        if not self._is_placeholder_parent_resolved(placeholder):
            return

        derive_node = self._resolver_graph.get_placeholder_child(placeholder)
        base_node = self._derived_from_path_resolving(derive_node, placeholder.derive_path)

        if base_node is None:
            return

        self._resolver_graph.remove_placeholder(placeholder)

        try:
            self._resolver_graph.add_edge(base_node, derive_node, EdgeType.DERIVE)
        except ResolverGraphException as exc:  # pylint: disable=no-member
            message = (
                f"Inheritance cycle detected for node '{derive_node.name}' with derive path {placeholder.derive_path}"
            )
            raise CycleException(message) from exc

        self._logger.log_resolved_placeholder(placeholder.derive_path)

    def _derived_from_path_resolving(self, derived_node: ElementNode, derive_path: str) -> None | ElementNode:
        derive_path_parts = derive_path.split(".")
        level = derived_node.level

        def search_nodes(
            nodes: list[ElementNode], path_parts: list[str], exclude_node: ElementNode, target_level: ElementLevel
        ) -> list[ElementNode]:
            matches: list[ElementNode] = []
            for node in nodes:
                if node == exclude_node:
                    continue
                if node.name != path_parts[0]:
                    continue

                if len(path_parts) == 1:
                    # If we've matched the final part, check the level
                    if node.level == target_level:
                        matches.append(node)
                else:
                    # Recurse into children
                    child_matches = search_nodes(
                        self._resolver_graph.get_element_childrens(node), path_parts[1:], exclude_node, target_level
                    )
                    matches.extend(child_matches)

                if len(matches) > 1:
                    filtered_matches = [
                        match
                        for match in matches
                        if isinstance(match.processed, IRegister) and match.processed.alternate_group is None
                    ]
                    if len(filtered_matches) == 1:
                        return filtered_matches

                    # More than one match found – raise exception immediately
                    raise ResolveException(f"Multiple base nodes found for derive path '{'.'.join(path_parts)}'")

            return matches

        # Search in same scope
        siblings = self._resolver_graph.get_element_siblings(derived_node)
        matches = search_nodes(siblings, derive_path_parts, derived_node, level)
        if len(matches) == 1:
            return matches[0]

        # If not found, search over all peripherals
        peripherals = self._resolver_graph.get_element_childrens(self._root_node)
        matches = search_nodes(peripherals, derive_path_parts, derived_node, level)
        if len(matches) == 1:
            return matches[0]

        # No matches found
        return None

    def _is_placeholder_parent_resolved(self, placeholder: PlaceholderNode) -> bool:
        parent = self._resolver_graph.get_placeholder_parent(placeholder)

        if parent.status == NodeStatus.PROCESSED:
            return True

        return False

    def _finalize_node(self, node: ElementNode, child_nodes: list[ElementNode]):
        if node.is_dim_template:
            return

        if node.level == ElementLevel.DEVICE:
            self._finalize_device_node(node, child_nodes)
        elif node.level == ElementLevel.PERIPHERAL:
            self._finalize_peripheral_node(node, child_nodes)
        elif node.level == ElementLevel.CLUSTER:
            self._finalize_cluster_node(node, child_nodes)
        elif node.level == ElementLevel.REGISTER:
            self._finalize_register_node(node, child_nodes)
        elif node.level == ElementLevel.FIELD:
            self._finalize_field_node(node, child_nodes)
        else:
            raise ResolveException("Unknown node type")

    def _finalize_device_node(self, _: ElementNode, children_nodes: list[ElementNode]):
        peripherals = [cast(IPeripheral, node.processed) for node in children_nodes if not node.is_dim_template]
        self._peripherals_resolved = sorted(peripherals, key=lambda p: (p.base_address, p.name))

    def _finalize_peripheral_node(self, peripheral_node: ElementNode, children_nodes: list[ElementNode]):
        peripheral = cast(IPeripheral, peripheral_node.processed)
        peripheral.size = self._calculate_size(children_nodes)

        registers_clusters = [
            cast(IRegister | ICluster, node.processed) for node in children_nodes if not node.is_dim_template
        ]

        peripheral.registers_clusters = sorted(registers_clusters, key=lambda rc: (rc.address_offset, rc.name))

    def _finalize_cluster_node(self, cluster_node: ElementNode, children_nodes: list[ElementNode]):
        cluster = cast(ICluster, cluster_node.processed)
        cluster.size = self._calculate_size(children_nodes)

        registers_clusters = [
            cast(IRegister | ICluster, node.processed) for node in children_nodes if not node.is_dim_template
        ]

        cluster.registers_clusters = sorted(registers_clusters, key=lambda rc: (rc.address_offset, rc.name))

    def _finalize_register_node(self, register_node: ElementNode, children_nodes: list[ElementNode]):
        register = cast(IRegister, register_node.processed)
        fields = [cast(IField, node.processed) for node in children_nodes if not node.is_dim_template]

        register.fields = sorted(fields, key=lambda f: (f.lsb, f.name))

    def _finalize_field_node(self, field_node: ElementNode, children_nodes: list[ElementNode]):
        field = cast(IField, field_node.processed)

        containers = [
            self._process._process_enumerated_value_container(  # pylint: disable=W0212 #pyright: ignore[reportPrivateUsage]
                cast(SVDEnumeratedValueContainer, child.parsed), field.lsb, field.msb
            )
            for child in children_nodes
        ]

        # Check for duplicate usage
        usages = [container.usage for container in containers]
        if len(usages) != len(set(usages)):
            raise EnumeratedValueContainerException("Field has multiple EnumeratedValueContainers with the same usage")

        # Check total container count
        if len(containers) > 2:
            raise EnumeratedValueContainerException("Field has more than two EnumeratedValueContainers")

        # If exactly two containers, their usage must be READ/WRITE (subset check)
        if len(containers) == 2 and not set(usages).issubset({EnumUsageType.READ, EnumUsageType.WRITE}):
            raise EnumeratedValueContainerException("Invalid EnumeratedValueContainer usage combination")

        field.enumerated_value_containers = containers

    def _calculate_size(self, child_nodes: list[ElementNode]) -> int:
        max_size = -1
        for node in child_nodes:
            if not isinstance(node.processed, IRegister | ICluster):
                raise ResolveException("node is not of type Register or Cluster")

            if node.is_dim_template:
                continue

            child_size = node.processed.size

            # Elements with sizes that are not multiples of 8 will be ignored later.
            # Therefore, we set their size to zero here to ensure correct size calculations for other elements.
            if child_size is not None and child_size % 8 != 0:
                child_size = 0

            if child_size is None:
                child_size = self._get_parent_size_recursively(node)

            if child_size > max_size:
                max_size = child_size

        if max_size == -1:
            raise ResolveException("max_size can't be -1")

        return max_size

    def _get_parent_size_recursively(self, node: ElementNode) -> int:
        parents = self._resolver_graph.get_element_parents(node)

        if not parents:
            return -1

        parent = parents[0]  # only dim nodes have multiple parents, but all have same size

        if parent.level == ElementLevel.DEVICE:
            return 32  # default size for device

        element = parent.processed
        if not isinstance(element, IPeripheral | ICluster):
            raise ResolveException("Parent of node is not a Peripheral or Cluster")

        if element.size is not None:
            return element.size

        return self._get_parent_size_recursively(parent)

    def _ensure_accurate_parent_child_relationships_for_placeholders(self):
        for placeholder in self._resolver_graph.get_placeholders():
            co_parent = self._resolver_graph.get_placeholder_co_parent(placeholder)

            if co_parent is None:
                continue

            self._resolver_graph.add_edge(co_parent, placeholder, EdgeType.PLACEHOLDER)

    def _process_node(self, node: ElementNode):
        parsed_element = node.parsed

        if isinstance(parsed_element, SVDDevice):
            raise ResolveException("Device should not be processed as an element")

        base_node = None
        base_processed_element = None
        if parsed_element.derived_from is not None:
            base_node = self._get_derived_from_base_node(node)
            base_processed_element = base_node.processed_or_none

            # Ensure that the base element is processed, except for enum containers
            if base_processed_element is None and not isinstance(parsed_element, SVDEnumeratedValueContainer):
                raise ResolveException(f"Base element not found for node '{parsed_element.name}'")

        if isinstance(parsed_element, SVDEnumeratedValueContainer):
            self._process_enumerated_value_container_node(node, base_node)
            return

        if not isinstance(base_processed_element, None | IntermediateDimablePeripheralTypes):
            raise ResolveException(f"Unknown type {type(base_processed_element)} in _process_element")

        self._process_dimable_node(node, parsed_element, base_node, base_processed_element)

    def _process_dimable_node(
        self,
        node: ElementNode,
        parsed_element: ParsedDimablePeripheralTypes,
        base_node: None | ElementNode,
        base_processed_element: None | IntermediateDimablePeripheralTypes,
    ):
        is_dim, resolved_dim_names, resolved_dim_display_names = (
            self._process._extract_and_process_dimension(  # pylint: disable=W0212 #pyright: ignore[reportPrivateUsage]
                parsed_element, base_processed_element
            )
        )
        processed_dimable_elements: list[IntermediateDimablePeripheralTypes] = []
        for index, name in enumerate(resolved_dim_names):
            processed_dimable_elements.append(
                self._create_dimable_element(
                    index, name, resolved_dim_display_names[index], parsed_element, base_processed_element
                )
            )

        if not processed_dimable_elements:
            raise ResolveException(f"No elements created for {parsed_element}")

        if is_dim:
            processed_dim_element = self._post_process_dim_elements(parsed_element.name, processed_dimable_elements)
            self._update_dim_node(node, base_node, processed_dimable_elements, processed_dim_element)
        else:
            self._update_node(node, base_node, processed_dimable_elements[0])

    def _post_process_dim_elements(
        self, dim_name: str, processed_dimable_elements: list[IntermediateDimablePeripheralTypes]
    ) -> IntermediateDimablePeripheralTypes:
        assert len(processed_dimable_elements) >= 1

        processed_dim_template = copy.copy(processed_dimable_elements[0])
        processed_dim_template.name = dim_name

        for processed_dimable_element in processed_dimable_elements:
            processed_dimable_element.dim = None
            processed_dimable_element.dim_increment = None
            processed_dimable_element.dim_index = None

        return processed_dim_template

    def _create_dimable_element(
        self,
        index: int,
        name: str,
        display_name: None | str,
        parsed_element: ParsedPeripheralTypes,
        base_element: None | IntermediatePeripheralTypes,
    ) -> IntermediateDimablePeripheralTypes:
        if isinstance(parsed_element, SVDPeripheral):
            return self._process._process_peripheral(  # pylint: disable=W0212 #pyright: ignore[reportPrivateUsage]
                index, name, parsed_element, cast(None | IPeripheral, base_element)
            )
        elif isinstance(parsed_element, SVDCluster):
            return self._process._process_cluster(  # pylint: disable=W0212 #pyright: ignore[reportPrivateUsage]
                index, name, parsed_element, cast(None | ICluster, base_element)
            )
        elif isinstance(parsed_element, SVDRegister):
            return self._process._process_register(  # pylint: disable=W0212 #pyright: ignore[reportPrivateUsage]
                index, name, display_name, parsed_element, cast(None | IRegister, base_element)
            )
        elif isinstance(parsed_element, SVDField):
            return self._process._process_field(  # pylint: disable=W0212 #pyright: ignore[reportPrivateUsage]
                index, name, parsed_element, cast(None | IField, base_element)
            )
        else:
            raise ResolveException(f"Unknown type {type(parsed_element)} in _create_dimable_element")
