from typing import cast, TYPE_CHECKING
import copy

from svdsuite.resolve.graph import ResolverGraph
from svdsuite.resolve.graph_builder import GraphBuilder
from svdsuite.resolve.graph_elements import ElementNode, PlaceholderNode, NodeStatus, EdgeType, ElementLevel
from svdsuite.resolve.exception import ResolveException, ResolverGraphException
from svdsuite.resolve.type_alias import (
    ProcessedPeripheralTypes,
    ProcessedDimablePeripheralTypes,
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
    SVDEnumeratedValue,
)
from svdsuite.model.process import (
    Device,
    Peripheral,
    Cluster,
    Register,
    Field,
    EnumeratedValueContainer,
    EnumeratedValue,
)
from svdsuite.model.process import EnumUsageType
from svdsuite.util.enumerated_value import process_binary_value_with_wildcard
from svdsuite.util.dim import resolve_dim
from svdsuite.util.helper import or_if_none

if TYPE_CHECKING:
    from svdsuite.process import Process


# TODO remove here
class ProcessException(Exception):
    pass


class Resolver:
    def __init__(self, process: "Process", resolver_logging_file_path: None | str):
        self._process = process
        self._resolver_graph = ResolverGraph()
        self._root_node_: None | ElementNode = None
        self._logger = ResolverLogger(resolver_logging_file_path, self._resolver_graph)
        self._are_repeating_steps_finished_after_current_round = False
        self._peripherals_resolved: None | list[Peripheral] = None

    @property
    def _root_node(self) -> ElementNode:
        if self._root_node_ is None:
            raise ResolveException("Root node is not set")

        return self._root_node_

    def resolve_peripherals(self, parsed_device: SVDDevice) -> list[Peripheral]:
        self._initialization(parsed_device)

        self._logger.log_repeating_steps_start()
        previous_nodes: list[ElementNode] = []
        while not self._are_repeating_steps_finished_after_current_round:
            self._logger.log_round_start()

            self._resolve_placeholders()
            processable_nodes = self._get_topological_sorted_processable_nodes()

            if processable_nodes == previous_nodes:
                self._logger.log_loop_detected()
                raise ProcessException("Stuck in a loop, the same elements are being processed repeatedly")

            previous_nodes = processable_nodes

            for node in processable_nodes:
                self._process_element(node)

            self._logger.log_round_end()

        self._logger.log_repeating_steps_finished()
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

    def _finalize_processing(self):
        self._resolver_graph.bottom_up_sibling_traversal(self._finalize_siblings)

    def _get_base_node(self, derived_node: ElementNode) -> ElementNode:
        base_node = self._resolver_graph.get_base_element_node(derived_node)

        if base_node is None:
            raise ResolveException(f"Base node not found for node '{derived_node.name}'")

        if derived_node.level != base_node.level:
            raise ResolveException(
                f"Node '{derived_node.name}' and its base node '{base_node.name}' have different levels"
            )

        if isinstance(base_node.processed_or_none, Device):
            raise ResolveException("Base node can't be a Device")

        return base_node

    def _update_enumerated_value_container(self, node: ElementNode, base_node: None | ElementNode):
        # if base_node_id is not None, update the node with the base node's parsed attribute (copy from base)
        if base_node is not None:
            node.parsed = cast(SVDEnumeratedValueContainer, base_node.parsed)

            # remove the derive edge
            self._resolver_graph.remove_edge(base_node, node)

            # replicate the base node's descendants as descendants of current node
            self._resolver_graph.replicate_descendants(base_node, node)

        # update node
        node.status = NodeStatus.PROCESSED

    def _update_element(
        self,
        node: ElementNode,
        base_node: None | ElementNode,
        processed: ProcessedPeripheralTypes,
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

    def _update_dim_element(
        self,
        node: ElementNode,
        base_node: None | ElementNode,
        processed_elements: list[ProcessedDimablePeripheralTypes],
        processed_dim_element: ProcessedDimablePeripheralTypes,
    ):
        # update dim element itself (must be called before the new nodes are created in the next step)
        self._update_element(node, base_node, processed_dim_element, is_dim_template=True)

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

        self._update_are_repeating_steps_finished_after_current_round(result)
        return result

    def _update_are_repeating_steps_finished_after_current_round(self, getting_processed_nodes: list[ElementNode]):
        unprocessed_nodes = self._resolver_graph.get_unprocessed_nodes()
        unprocessed_after_round_nodes = unprocessed_nodes - set(getting_processed_nodes)

        if not unprocessed_after_round_nodes:
            self._are_repeating_steps_finished_after_current_round = True

    def _resolve_placeholder(self, placeholder: PlaceholderNode):
        if not self._is_placeholder_parent_resolved(placeholder):
            return

        derive_node = self._get_placeholder_derive_node(placeholder)
        base_node = self._find_base_node(derive_node, placeholder.derive_path)

        if base_node is None:
            return

        self._resolver_graph.remove_placeholder(placeholder)

        try:
            self._resolver_graph.add_edge(base_node, derive_node, EdgeType.DERIVE)
        except ResolverGraphException as exc:  # pylint: disable=no-member
            message = (
                f"Inheritance cycle detected for node '{derive_node.name}' with derive path {placeholder.derive_path}"
            )
            raise ResolveException(message) from exc

        self._logger.log_resolved_placeholder(placeholder.derive_path)

    def _find_base_node(self, derived_node: ElementNode, derive_path: str) -> None | ElementNode:
        derive_path_parts = derive_path.split(".")
        level = derived_node.level

        def find_base_node_recursive(node: ElementNode, path_parts: list[str]) -> None | ElementNode:
            if node == derived_node:
                return None
            if node.name != path_parts[0]:
                return None
            if len(path_parts) == 1:
                return node if node.level == level else None
            children = self._resolver_graph.get_element_childrens(node)
            for child in children:
                result = find_base_node_recursive(child, path_parts[1:])
                if result is not None:
                    return result
            return None

        def find_base_node_in_nodes(nodes: list[ElementNode]) -> None | ElementNode:
            base_nodes: list[ElementNode] = []
            for node in nodes:
                result = find_base_node_recursive(node, derive_path_parts)
                if result:
                    base_nodes.append(result)

            if len(base_nodes) == 1:
                return base_nodes[0]
            elif len(base_nodes) > 1:
                raise ResolveException(f"Multiple base nodes found for derive path '{derive_path}'")

            return None

        # search in same scope
        siblings = self._resolver_graph.get_element_siblings(derived_node)
        base_node = find_base_node_in_nodes(siblings)

        if base_node is not None:
            return base_node

        # search over all peripherals
        peripherals = self._resolver_graph.get_element_childrens(self._root_node)
        base_node = find_base_node_in_nodes(peripherals)

        return base_node

    def _get_placeholder_derive_node(self, placeholder: PlaceholderNode) -> ElementNode:
        return self._resolver_graph.get_placeholder_child(placeholder)

    def _is_placeholder_parent_resolved(self, placeholder: PlaceholderNode) -> bool:
        parent = self._resolver_graph.get_placeholder_parent(placeholder)

        if parent.status == NodeStatus.PROCESSED:
            return True

        return False

    def _finalize_siblings(self, parent: ElementNode, siblings: list[ElementNode]):
        if parent.is_dim_template:
            return

        if parent.level == ElementLevel.DEVICE:
            self._finalize_device(parent, siblings)
        elif parent.level == ElementLevel.PERIPHERAL:
            self._finalize_peripheral(parent, siblings)
        elif parent.level == ElementLevel.CLUSTER:
            self._finalize_cluster(parent, siblings)
        elif parent.level == ElementLevel.REGISTER:
            self._finalize_register(parent, siblings)
        elif parent.level == ElementLevel.FIELD:
            self._finalize_field(parent, siblings)
        else:
            raise ResolveException("Unknown node type")

    def _finalize_device(self, _: ElementNode, children_nodes: list[ElementNode]):
        peripherals = [cast(Peripheral, node.processed) for node in children_nodes if not node.is_dim_template]
        self._peripherals_resolved = sorted(peripherals, key=lambda p: (p.base_address, p.name))

    def _finalize_peripheral(self, peripheral_node: ElementNode, children_nodes: list[ElementNode]):
        peripheral = cast(Peripheral, peripheral_node.processed)
        peripheral.size = self._calculate_size(
            peripheral_node, [cast(Register | Cluster, node.processed) for node in children_nodes]
        )

        registers_clusters = [
            cast(Register | Cluster, node.processed) for node in children_nodes if not node.is_dim_template
        ]

        peripheral.registers_clusters = sorted(registers_clusters, key=lambda rc: (rc.address_offset, rc.name))

    def _finalize_cluster(self, cluster_node: ElementNode, children_nodes: list[ElementNode]):
        cluster = cast(Cluster, cluster_node.processed)
        cluster.size = self._calculate_size(
            cluster_node, [cast(Register | Cluster, node.processed) for node in children_nodes]
        )

        registers_clusters = [
            cast(Register | Cluster, node.processed) for node in children_nodes if not node.is_dim_template
        ]

        cluster.registers_clusters = sorted(registers_clusters, key=lambda rc: (rc.address_offset, rc.name))

    def _finalize_register(self, register_node: ElementNode, children_nodes: list[ElementNode]):
        register = cast(Register, register_node.processed)
        fields = [cast(Field, node.processed) for node in children_nodes if not node.is_dim_template]

        register.fields = sorted(fields, key=lambda f: (f.lsb, f.name))

    def _finalize_field(self, field_node: ElementNode, children_nodes: list[ElementNode]):
        field = cast(Field, field_node.processed)
        enum_containers: list[EnumeratedValueContainer] = []
        for child in children_nodes:
            enum_container = _ProcessEnumeratedValueContainers().create_enumerated_value_container(
                cast(SVDEnumeratedValueContainer, child.parsed), field.lsb, field.msb
            )
            enum_containers.append(enum_container)

        field.enumerated_value_containers = enum_containers

    def _calculate_size(self, node: ElementNode, child_elements: list[Register | Cluster]) -> int:
        element = cast(Register | Cluster, node.processed)

        own_size = element.size if element.size is not None else -1

        inherited_size = self._get_parent_size_recursively(node)

        child_sizes = [child.size for child in child_elements if child.size is not None]
        max_child_size = max(child_sizes) if child_sizes else -1

        return max(own_size, inherited_size, max_child_size)

    def _get_parent_size_recursively(self, node: ElementNode) -> int:
        parents = self._resolver_graph.get_element_parents(node)

        if not parents:
            return -1

        parent = parents[0]  # only dim nodes have multiple parents, but all have same size

        if parent.level == ElementLevel.DEVICE:
            return 32  # default size for device

        element = parent.processed
        if not isinstance(element, Peripheral | Cluster):
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

    def _resolve_dim(
        self, parsed_element: ParsedDimablePeripheralTypes, base_element: None | ProcessedDimablePeripheralTypes
    ) -> tuple[bool, list[str]]:
        dim = or_if_none(parsed_element.dim, base_element.dim if base_element else None)
        dim_index = or_if_none(parsed_element.dim_index, base_element.dim_index if base_element else None)

        if dim is None and "%s" in parsed_element.name:
            raise ProcessException("Dim is None, but name contains '%s'")

        if dim is not None and "%s" not in parsed_element.name:
            raise ProcessException("Dim is not None, but name does not contain '%s'")

        return dim is not None, resolve_dim(parsed_element.name, dim, dim_index)

    # TODO split for dimabmle and enum containers
    def _process_element(self, node: ElementNode):
        parsed_element = node.parsed

        if isinstance(parsed_element, SVDDevice):
            raise ProcessException("Device should not be processed as an element")

        base_node = None
        base_processed_element = None
        if parsed_element.derived_from is not None:
            base_node = self._get_base_node(node)
            base_processed_element = base_node.processed_or_none

            # Ensure that the base element is processed, except for enum containers
            if base_processed_element is None and not isinstance(parsed_element, SVDEnumeratedValueContainer):
                raise ProcessException(f"Base element not found for node '{parsed_element.name}'")

        # Processing of enum containers is postboned to finalization, since lsb and msb from parent fields are required
        if isinstance(parsed_element, SVDEnumeratedValueContainer):
            self._update_enumerated_value_container(node, base_node)
            return

        if base_processed_element is not None and not isinstance(
            base_processed_element, ProcessedDimablePeripheralTypes
        ):
            raise ProcessException(f"Base element is not dimable for node '{parsed_element.name}'")

        is_dim, resolved_dim = self._resolve_dim(parsed_element, base_processed_element)
        processed_dimable_elements: list[ProcessedDimablePeripheralTypes] = []
        for index, name in enumerate(resolved_dim):
            processed_dimable_elements.append(
                self._create_dimable_element(index, name, parsed_element, base_processed_element)
            )

        if not processed_dimable_elements:
            raise ProcessException(f"No elements created for {parsed_element}")

        if is_dim:
            processed_dim_element = self._post_process_dim_elements(parsed_element.name, processed_dimable_elements)
            self._update_dim_element(node, base_node, processed_dimable_elements, processed_dim_element)
        else:
            self._update_element(node, base_node, processed_dimable_elements[0])

    def _post_process_dim_elements(
        self, dim_name: str, processed_dimable_elements: list[ProcessedDimablePeripheralTypes]
    ) -> ProcessedDimablePeripheralTypes:
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
        parsed_element: ParsedPeripheralTypes,
        base_element: None | ProcessedPeripheralTypes,
    ) -> ProcessedDimablePeripheralTypes:
        if isinstance(parsed_element, SVDPeripheral):
            return self._process._process_peripheral(  # pylint: disable=W0212 #pyright: ignore[reportPrivateUsage]
                index, name, parsed_element, cast(None | Peripheral, base_element)
            )
        elif isinstance(parsed_element, SVDCluster):
            return self._process._process_cluster(  # pylint: disable=W0212 #pyright: ignore[reportPrivateUsage]
                index, name, parsed_element, cast(None | Cluster, base_element)
            )
        elif isinstance(parsed_element, SVDRegister):
            return self._process._process_register(  # pylint: disable=W0212 #pyright: ignore[reportPrivateUsage]
                index, name, parsed_element, cast(None | Register, base_element)
            )
        elif isinstance(parsed_element, SVDField):
            return self._process._process_field(  # pylint: disable=W0212 #pyright: ignore[reportPrivateUsage]
                index, name, parsed_element, cast(None | Field, base_element)
            )
        else:
            raise ProcessException(f"Unknown type {type(parsed_element)} in _create_dimable_element")


# TODO shouldn't be in this file
class _ProcessEnumeratedValueContainers:
    def create_enumerated_value_container(
        self, parsed_enum_container: SVDEnumeratedValueContainer, lsb: int, msb: int
    ) -> EnumeratedValueContainer:
        return EnumeratedValueContainer(
            name=parsed_enum_container.name,
            header_enum_name=parsed_enum_container.header_enum_name,
            usage=parsed_enum_container.usage if parsed_enum_container.usage is not None else EnumUsageType.READ_WRITE,
            enumerated_values=self._process_enumerated_values(parsed_enum_container.enumerated_values, lsb, msb),
            parsed=parsed_enum_container,
        )

    def _process_enumerated_values(
        self, parsed_enumerated_values: list[SVDEnumeratedValue], lsb: int, msb: int
    ) -> list[EnumeratedValue]:
        enum_value_validator = _EnumeratedValueValidator()
        enumerated_values: list[EnumeratedValue] = []

        for parsed_enumerated_value in parsed_enumerated_values:
            processed_enumerated_values = self._process_enumerated_value_resolve_wildcard(parsed_enumerated_value)

            for value in processed_enumerated_values:
                enum_value_validator.add_value(value)

            enumerated_values.extend(processed_enumerated_values)

        if default_enumerated_value := enum_value_validator.get_default():
            enumerated_values = self._extend_enumerated_values_with_default(
                enumerated_values, default_enumerated_value, lsb, msb
            )

        return sorted(enumerated_values, key=lambda ev: ev.value if ev.value is not None else 0)

    def _process_enumerated_value_resolve_wildcard(self, parsed_value: SVDEnumeratedValue) -> list[EnumeratedValue]:
        value_list = self._convert_enumerated_value(parsed_value.value) if parsed_value.value else [None]

        enumerated_values: list[EnumeratedValue] = []
        for value in value_list:
            name = parsed_value.name
            if value is not None and parsed_value.value and "x" in parsed_value.value:
                name = f"{name}_{value}"

            enumerated_values.append(
                EnumeratedValue(
                    name=name,
                    description=parsed_value.description,
                    value=value,
                    is_default=parsed_value.is_default or False,
                    parsed=parsed_value,
                )
            )

        return enumerated_values

    def _extend_enumerated_values_with_default(
        self, enumerated_values: list[EnumeratedValue], default: EnumeratedValue, lsb: int, msb: int
    ) -> list[EnumeratedValue]:
        covered_values = {value.value for value in enumerated_values if value.value is not None}
        all_possible_values = set(range(pow(2, msb - lsb + 1)))

        uncovered_values = all_possible_values - covered_values

        for value in uncovered_values:
            enumerated_values.append(
                EnumeratedValue(
                    name=f"{default.name}_{value}",
                    description=default.description,
                    value=value,
                    is_default=False,
                    parsed=default.parsed,
                )
            )

        return [value for value in enumerated_values if not value.is_default]

    def _convert_enumerated_value(self, input_str: str) -> list[int]:
        try:
            if input_str.startswith("0b"):
                return process_binary_value_with_wildcard(input_str[2:])
            elif input_str.startswith("0x"):
                return [int(input_str, 16)]
            elif input_str.isdigit():
                return [int(input_str)]
            else:
                raise ProcessException(f"Unrecognized format for input: '{input_str}'")
        except ValueError as exc:
            raise ProcessException(f"Error processing input '{input_str}': {exc}") from exc


# TODO shouldn't be in this file
class _EnumeratedValueValidator:
    def __init__(self):
        self._seen_names: set[str] = set()
        self._seen_values: set[int] = set()
        self._seen_default = None

    def add_value(self, value: EnumeratedValue):
        # Ensure enumerated value names and values are unique
        if value.name in self._seen_names:
            raise ProcessException(f"Duplicate enumerated value name found: {value.name}")
        if value.value in self._seen_values:
            raise ProcessException(f"Duplicate enumerated value value found: {value.value}")
        if value.is_default:
            if value.value is not None:
                raise ProcessException("Default value must not have a value")
            if self._seen_default:
                raise ProcessException("Multiple default values found")
            self._seen_default = value

        # Add to seen names and values
        self._seen_names.add(value.name)
        if value.value is not None:
            self._seen_values.add(value.value)

    def get_default(self) -> None | EnumeratedValue:
        return self._seen_default
