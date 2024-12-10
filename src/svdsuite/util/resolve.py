import itertools
from collections import defaultdict, deque
from abc import ABC
from enum import Enum, auto
from typing import TypeAlias, cast, Any, Callable, DefaultDict, Deque
import tempfile
import copy
import rustworkx as rx
from rustworkx.visualization import graphviz_draw  # pyright: ignore[reportUnknownVariableType]

from svdsuite.util.html_generator import HTMLGenerator
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
from svdsuite.model.process import EnumUsageType, AccessType, ProtectionStringType
from svdsuite.util.enumerated_value import process_binary_value_with_wildcard

ParsedPeripheralTypes: TypeAlias = SVDPeripheral | SVDCluster | SVDRegister | SVDField | SVDEnumeratedValueContainer
ParsedDimablePeripheralTypes: TypeAlias = SVDPeripheral | SVDCluster | SVDRegister | SVDField
ProcessedPeripheralTypes: TypeAlias = Peripheral | Cluster | Register | Field | EnumeratedValueContainer
ProcessedDimablePeripheralTypes: TypeAlias = Peripheral | Cluster | Register | Field


# TODO remove here
def _or_if_none[T](a: None | T, b: None | T) -> None | T:
    return a if a is not None else b


class ResolveException(Exception):
    pass


# TODO remove here
class ProcessException(Exception):
    pass


class _ElementLevel(Enum):
    DEVICE = "Device"
    PERIPHERAL = "Peripheral"
    CLUSTER = "Cluster"
    REGISTER = "Register"
    FIELD = "Field"
    ENUMCONT = "Enum"


class _NodeStatus(Enum):
    UNPROCESSED = auto()  # black
    PROCESSED = auto()  # blue


class _EdgeType(Enum):
    CHILD_UNRESOLVED = auto()  # black
    CHILD_RESOLVED = auto()  # blue
    PLACEHOLDER = auto()  # red
    DERIVE = auto()  # green


class _ResolverNode(ABC):
    _node_counter = itertools.count()

    def __init__(self):
        self._node_id = next(self._node_counter)

    @property
    def node_id(self) -> int:
        return self._node_id


class _PlaceholderNode(_ResolverNode):
    def __init__(self, derive_path: str):
        self._derive_path = derive_path

        super().__init__()

    @property
    def derive_path(self) -> str:
        return self._derive_path


class _ElementNode(_ResolverNode):
    def __init__(
        self,
        name: None | str,
        level: _ElementLevel,
        status: _NodeStatus,
        parsed: SVDDevice | ParsedPeripheralTypes,
        processed: None | Device | ProcessedPeripheralTypes = None,
        is_dim_template: bool = False,
    ):
        self._name = name
        self._level = level
        self.status = status
        self._parsed = parsed
        self._is_dim_template = is_dim_template
        self._processed = processed

        super().__init__()

    @property
    def name(self) -> None | str:
        return self._name

    @property
    def level(self) -> _ElementLevel:
        return self._level

    @property
    def parsed(self) -> SVDDevice | ParsedPeripheralTypes:
        return self._parsed

    @parsed.setter
    def parsed(self, parsed: SVDEnumeratedValueContainer):
        if not isinstance(parsed, SVDEnumeratedValueContainer):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ResolveException("parsed attribute can only be set to SVDEnumeratedValueContainer")

        self._parsed = parsed

    @property
    def is_dim_template(self) -> bool:
        return self._is_dim_template

    @is_dim_template.setter
    def is_dim_template(self, is_dim_template: bool):
        if self._is_dim_template is True and is_dim_template is False:
            raise ResolveException("is_dim_template attribute is already set to True and can't be set to False")

        self._is_dim_template = is_dim_template

    @property
    def node_id(self) -> int:
        return self._node_id

    @property
    def processed(self) -> Device | ProcessedPeripheralTypes:
        if self._processed is None:
            raise ResolveException(f"Processed attribute of node '{self.name}' is None")

        return self._processed

    @property
    def processed_or_none(self) -> None | Device | ProcessedPeripheralTypes:
        return self._processed

    @processed.setter
    def processed(self, processed: ProcessedPeripheralTypes):
        if self._processed is not None:
            raise ResolveException(f"Processed attribute of node '{self.name}' is already set")

        self._processed = processed


class _ResolverGraphException(Exception):
    pass


class _ResolverGraph:
    def __init__(self):
        self._graph: rx.PyDiGraph[_ResolverNode, _EdgeType] = rx.PyDiGraph(  # pylint: disable=no-member
            check_cycle=True
        )
        self._node_id_to_rx_index: dict[int, int] = {}
        self._rx_index_to_node_id: dict[int, int] = {}
        self._placeholders: list[_PlaceholderNode] = []
        self._unprocessed_rx_indicies: list[int] = []

    def add_root(self, root: _ElementNode):
        rx_index = self._graph.add_node(root)

        self._node_id_to_rx_index[root.node_id] = rx_index
        self._rx_index_to_node_id[rx_index] = root.node_id

    def add_element_child(self, parent: _ElementNode, child: _ElementNode, edge_type: _EdgeType):
        parent_rx_index = self._node_id_to_rx_index[parent.node_id]
        child_rx_index = self._graph.add_node(child)
        self._graph.add_edge(parent_rx_index, child_rx_index, edge_type)

        self._node_id_to_rx_index[child.node_id] = child_rx_index
        self._rx_index_to_node_id[child_rx_index] = child.node_id

    def add_edge(self, parent: _ElementNode, child: _ElementNode | _PlaceholderNode, edge_type: _EdgeType):
        self._graph.add_edge(
            self._node_id_to_rx_index[parent.node_id], self._node_id_to_rx_index[child.node_id], edge_type
        )

    def add_placeholder(self, placeholder: _PlaceholderNode, derivation_node: _ElementNode):
        derivation_node_rx_index = self._node_id_to_rx_index[derivation_node.node_id]
        placeholder_rx_index = self._graph.add_node(placeholder)
        self._graph.add_edge(placeholder_rx_index, derivation_node_rx_index, _EdgeType.PLACEHOLDER)

        self._node_id_to_rx_index[placeholder.node_id] = placeholder_rx_index
        self._rx_index_to_node_id[placeholder_rx_index] = placeholder.node_id

        self._placeholders.append(placeholder)

    def get_placeholders(self) -> list[_PlaceholderNode]:
        return self._placeholders

    def get_placeholder_co_parent(self, placeholder: _PlaceholderNode) -> None | _ElementNode:
        children = self._graph.successors(self._node_id_to_rx_index[placeholder.node_id])

        if not children:
            raise _ResolverGraphException(f"Placeholder '{placeholder.derive_path}' has no child")

        if len(children) != 1:
            raise _ResolverGraphException(f"Placeholder '{placeholder.derive_path}' has more than one child")

        parents = self._graph.predecessors(self._node_id_to_rx_index[children[0].node_id])

        # only _ElementNode nodes
        parents = [parent for parent in parents if isinstance(parent, _ElementNode)]

        if not parents:
            return None

        if len(parents) != 1:
            raise _ResolverGraphException(f"Placeholder '{placeholder.derive_path}' has more than one co-parent")

        return parents[0]

    def get_element_parents(self, node: _ElementNode) -> list[_ElementNode]:
        incoming_edges = self._graph.in_edges(self._node_id_to_rx_index[node.node_id])

        parents = [
            self._graph[parent_rx_index]
            for parent_rx_index, _, edge_data in incoming_edges
            if isinstance(self._graph[parent_rx_index], _ElementNode)
            and edge_data in (_EdgeType.CHILD_UNRESOLVED, _EdgeType.CHILD_RESOLVED)
        ]

        return cast(list[_ElementNode], parents)

    def get_element_childrens(self, node: _ElementNode) -> list[_ElementNode]:
        outgoing_edges = self._graph.out_edges(self._node_id_to_rx_index[node.node_id])

        children = [
            self._graph[child_rx_index]
            for _, child_rx_index, edge_data in outgoing_edges
            if isinstance(self._graph[child_rx_index], _ElementNode)
            and edge_data in (_EdgeType.CHILD_UNRESOLVED, _EdgeType.CHILD_RESOLVED)
        ]

        return cast(list[_ElementNode], children)

    def get_element_siblings(self, node: _ElementNode) -> list[_ElementNode]:
        parents = self.get_element_parents(node)

        if not parents:
            return []

        # _ElementNode has one parent, except resolved dim nodes, which may have multiple with the same children
        # hence, the first parent suffices to find siblings
        parent = parents[0]

        siblings: list[_ElementNode] = []
        for child in self._graph.successors(self._node_id_to_rx_index[parent.node_id]):
            if not isinstance(child, _ElementNode):
                continue

            if child.node_id == node.node_id:
                continue

            siblings.append(child)

        return siblings

    def remove_placeholder(self, placeholder: _PlaceholderNode):
        self._remove_node(placeholder)
        self._placeholders.remove(placeholder)

    def remove_node(self, node: _ElementNode):
        self._remove_node(node)

    def _remove_node(self, node: _ElementNode | _PlaceholderNode):
        rx_index = self._node_id_to_rx_index[node.node_id]
        self._graph.remove_node(rx_index)

        del self._node_id_to_rx_index[node.node_id]
        del self._rx_index_to_node_id[rx_index]

    def has_incoming_edge_of_types(self, node: _ElementNode, edge_types_to_find: set[_EdgeType]) -> bool:
        rx_index = self._node_id_to_rx_index[node.node_id]
        for _, _, edge_type in self._graph.in_edges(rx_index):
            if edge_type in edge_types_to_find:
                return True
        return False

    def get_topological_sorted_nodes(self, nodes: list[_ElementNode]) -> list[_ElementNode]:
        def sort_key(node: _ResolverNode) -> str:
            # correct type of node for static type checking
            node = cast(_ElementNode, node)

            # derived nodes should be processed as late as possible
            if self.has_incoming_edge_of_types(node, {_EdgeType.DERIVE}):
                return "B"

            return "A"

        subgraph = self._graph.subgraph(
            [self._node_id_to_rx_index[node.node_id] for node in nodes if node.status == _NodeStatus.UNPROCESSED]
        )

        topological_sorted_nodes = rx.lexicographical_topological_sort(  # pylint: disable=no-member
            subgraph, key=sort_key
        )

        del subgraph

        # correct type of topological_sorted_nodes for static type checking
        return cast(list[_ElementNode], topological_sorted_nodes)

    def get_element_node_by_node_id(self, node_id: int) -> None | _ElementNode:
        try:
            node = self._graph[self._node_id_to_rx_index[node_id]]
        except KeyError:
            return None

        if not isinstance(node, _ElementNode):
            return None

        return node

    def get_base_element_node(self, derive_node: _ElementNode) -> None | _ElementNode:
        for parent_rx_index, _, edge_type in self._graph.in_edges(self._node_id_to_rx_index[derive_node.node_id]):
            if edge_type == _EdgeType.DERIVE:
                return cast(_ElementNode, self._graph[parent_rx_index])

        return None

    def remove_edge(self, parent: _ElementNode, child: _ElementNode):
        parent_rx_index = self._node_id_to_rx_index[parent.node_id]
        child_rx_index = self._node_id_to_rx_index[child.node_id]

        self._graph.remove_edge(parent_rx_index, child_rx_index)

    def update_edge(self, parent: _ElementNode, child: _ElementNode, edge_type: _EdgeType):
        parent_rx_index = self._node_id_to_rx_index[parent.node_id]
        child_rx_index = self._node_id_to_rx_index[child.node_id]

        self._graph.update_edge(parent_rx_index, child_rx_index, edge_type)

    def get_placeholder_child(self, placeholder: _PlaceholderNode) -> _ElementNode:
        outgoing_edges = self._graph.out_edges(self._node_id_to_rx_index[placeholder.node_id])

        children = [
            self._graph[child_rx_index]
            for _, child_rx_index, edge_data in outgoing_edges
            if isinstance(self._graph[child_rx_index], _ElementNode) and edge_data == _EdgeType.PLACEHOLDER
        ]

        if not children:
            raise ResolveException(f"Placeholder '{placeholder.derive_path}' has no children")

        if len(children) != 1:
            raise ResolveException(f"Placeholder '{placeholder.derive_path}' has more than one child")

        return cast(_ElementNode, children[0])

    def get_placeholder_parent(self, placeholder: _PlaceholderNode) -> _ElementNode:
        incoming_edges = self._graph.in_edges(self._node_id_to_rx_index[placeholder.node_id])

        parents = [
            self._graph[parent_rx_index]
            for parent_rx_index, _, edge_data in incoming_edges
            if isinstance(self._graph[parent_rx_index], _ElementNode) and edge_data == _EdgeType.PLACEHOLDER
        ]

        if not parents:
            raise ResolveException(f"Placeholder '{placeholder.derive_path}' has no parent")

        if len(parents) != 1:
            raise ResolveException(f"Placeholder '{placeholder.derive_path}' has more than one parent")

        return cast(_ElementNode, parents[0])

    def replicate_descendants(self, source_node: _ElementNode, target_node: _ElementNode):
        source_rx_index = self._node_id_to_rx_index[source_node.node_id]

        # get rx_index for all descendants of source_node, excluding edges of type _EdgeType.DERIVE
        rx_indices_to_replicate: set[int] = set()
        visited: set[int] = set()
        stack: list[int] = [source_rx_index]

        while stack:
            current_rx_index = stack.pop()
            if current_rx_index in visited:
                continue
            visited.add(current_rx_index)

            # get outgoing edges
            for _, child_rx_index, edge_type in self._graph.out_edges(current_rx_index):
                if edge_type == _EdgeType.DERIVE:
                    continue
                rx_indices_to_replicate.add(child_rx_index)
                stack.append(child_rx_index)

        # replicate the nodes and map the indicies
        replica_mapping: dict[int, int] = {}
        for rx_index in rx_indices_to_replicate:
            existing_node = self._graph[rx_index]
            new_node = self._create_replicated_node(existing_node)
            new_node_rx_index = self._graph.add_node(new_node)
            replica_mapping[rx_index] = new_node_rx_index

            self._node_id_to_rx_index[new_node.node_id] = new_node_rx_index
            self._rx_index_to_node_id[new_node_rx_index] = new_node.node_id

            if isinstance(new_node, _PlaceholderNode):
                self._placeholders.append(new_node)

        # replicate the edges
        for rx_index in rx_indices_to_replicate:
            # replicate outgoing _EdgeType.PROCESSED and _EdgeType.UNPROCESSED edges
            for _, child_rx_index, edge_type in self._graph.out_edges(rx_index):
                if child_rx_index not in rx_indices_to_replicate:
                    continue

                self._graph.add_edge(replica_mapping[rx_index], replica_mapping[child_rx_index], edge_type)

            # replicate incoming _EdgeType.DERIVE edges
            for parent_rx_index, _, edge_type in self._graph.in_edges(rx_index):
                if edge_type == _EdgeType.DERIVE:
                    self._graph.add_edge(parent_rx_index, replica_mapping[rx_index], edge_type)

        # find immediate children of source_node that are part of the replication
        immediate_children = [
            child_rx_index
            for _, child_rx_index, _ in self._graph.out_edges(source_rx_index)
            if child_rx_index in rx_indices_to_replicate
        ]

        # attach the replicated subgraph to target_node
        target_rx_index = self._node_id_to_rx_index[target_node.node_id]
        for child_rx_index in immediate_children:
            replicated_child_rx_index = replica_mapping[child_rx_index]
            if isinstance(self._graph[replicated_child_rx_index], _PlaceholderNode):
                self._graph.add_edge(target_rx_index, replicated_child_rx_index, _EdgeType.PLACEHOLDER)
            else:
                self._graph.add_edge(
                    target_rx_index,
                    replicated_child_rx_index,
                    (
                        _EdgeType.CHILD_RESOLVED
                        if source_node.status == _NodeStatus.PROCESSED
                        else _EdgeType.CHILD_UNRESOLVED
                    ),
                )

    def get_unprocessed_root_nodes(self) -> list[_ElementNode]:
        def filter_function(node: _ResolverNode) -> bool:
            return isinstance(node, _ElementNode) and node.status == _NodeStatus.UNPROCESSED

        rx_indices = self._graph.filter_nodes(filter_function)
        self._unprocessed_rx_indicies = list(rx_indices)

        unprocessed_root_nodes: list[_ElementNode] = []
        for rx_index in rx_indices:
            for _, _, edge_data in self._graph.in_edges(rx_index):
                if edge_data == _EdgeType.CHILD_RESOLVED:
                    unprocessed_root_nodes.append(cast(_ElementNode, self._graph[rx_index]))
                    break

        return unprocessed_root_nodes

    def get_unprocessed_node_ids(self) -> set[int]:
        return {self._rx_index_to_node_id[rx_index] for rx_index in self._unprocessed_rx_indicies}

    def bottom_up_sibling_traversal(self, finalize_siblings_cb: Callable[[_ElementNode, list[_ElementNode]], None]):
        # TODO can probably be optimized

        # Step 1: Build data structures
        pending_children: dict[_ElementNode, int] = {}
        children_of_node: DefaultDict[_ElementNode, list[_ElementNode]] = defaultdict(list)
        parents_of_node: DefaultDict[_ElementNode, list[_ElementNode]] = defaultdict(list)

        # Get all nodes
        all_nodes_rx_indices = self._graph.node_indices()
        for rx_index in all_nodes_rx_indices:
            node = cast(_ElementNode, self._graph[rx_index])
            # Get children
            children = cast(list[_ElementNode], self._graph.successors(rx_index))
            children_of_node[node].extend(children)
            # Set pending_children[node] = number of children
            pending_children[node] = len(children)
            # For each child, add node as parent
            for child in children:
                parents_of_node[child].append(node)

        # Step 2: Initialize queue with nodes whose pending_children[node] == 0 (leaves)
        queue: Deque[_ElementNode] = deque()
        for node, count in pending_children.items():
            if count == 0:
                queue.append(node)

        # Step 3: Process nodes (call finalize_siblings callback) in a bottom-up manner
        while queue:
            node = queue.popleft()
            # Call finalize_siblings for the node and its children, but only node is not a leaf (empty children)
            children = children_of_node[node]
            if children:
                finalize_siblings_cb(node, children)
            # For each parent of the node
            for parent in parents_of_node[node]:
                # Decrement pending_children[parent]
                pending_children[parent] -= 1
                if pending_children[parent] == 0:
                    # Add parent to the queue
                    queue.append(parent)

    def get_svg(self) -> str:
        def node_attr_fn(node: _ResolverNode) -> dict[str, str]:
            if isinstance(node, _ElementNode):
                if node.level == _ElementLevel.DEVICE:
                    return {"label": "Device", "color": "blue", "fontcolor": "blue"}

                return {
                    "label": (
                        f"{node.name}\n({node.level.value})\nId:{node.node_id}"
                        if node.name
                        else f"no name\n({node.level.value})\nId:{node.node_id}"
                    ),
                    "color": "black" if node.status == _NodeStatus.UNPROCESSED else "blue",
                    "fontcolor": "black" if node.status == _NodeStatus.UNPROCESSED else "blue",
                }
            elif isinstance(node, _PlaceholderNode):
                return {
                    "label": f"{node.derive_path}\n(Placeholder)\nId: {node.node_id}",
                    "color": "red",
                    "fontcolor": "red",
                }
            else:
                return {}

        def edge_attr_fn(edge: _EdgeType) -> dict[str, str]:
            if edge == _EdgeType.CHILD_UNRESOLVED:
                return {"color": "black"}
            elif edge == _EdgeType.CHILD_RESOLVED:
                return {"color": "blue"}
            elif edge == _EdgeType.PLACEHOLDER:
                return {"color": "red"}
            elif edge == _EdgeType.DERIVE:
                return {"color": "green"}
            else:
                return {}

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".svg") as temp_file:
            graphviz_draw(
                self._graph,
                node_attr_fn=node_attr_fn,
                edge_attr_fn=edge_attr_fn,
                image_type="svg",
                filename=temp_file.name,
            )
            temp_file.seek(0)
            svg_content = temp_file.read()

        return svg_content

    def _create_replicated_node(self, existing_node: _ResolverNode) -> _ResolverNode:
        if isinstance(existing_node, _ElementNode):
            return _ElementNode(
                name=existing_node.name,
                level=existing_node.level,
                status=existing_node.status,
                parsed=existing_node.parsed,
                processed=copy.copy(existing_node.processed_or_none),
                is_dim_template=existing_node.is_dim_template,
            )

        if isinstance(existing_node, _PlaceholderNode):
            return _PlaceholderNode(derive_path=existing_node.derive_path)

        raise ResolveException("Unknown node type")


class _ResolverLogger:
    def __init__(self, resolver_logging_file_path: None | str, get_svg_callback: Callable[[], str]):
        self._resolver_logging_file_path = resolver_logging_file_path
        self._get_svg_callback = get_svg_callback
        self._current_round_counter = itertools.count(1)
        self._current_round_resolved_placeholders: list[str] = []

        if self._resolver_logging_file_path is not None:
            self._html_generator = HTMLGenerator(self._resolver_logging_file_path)

    @staticmethod
    def _only_execute_if_logging_is_active[R](method: Callable[..., R]) -> Callable[..., R | None]:
        def wrapper(self: "_ResolverLogger", *args: Any, **kwargs: Any) -> R | None:
            if self._resolver_logging_file_path is None:  # pylint: disable=protected-access
                return None
            return method(self, *args, **kwargs)

        return wrapper

    @_only_execute_if_logging_is_active
    def log_init_constructed_graph(self):
        self._html_generator.add_h1("Initialization")
        self._html_generator.add_h2("Construct Directed Graph")
        self._html_generator.add_paragraph("Graph after construction:")
        self._html_generator.add_svg(self._get_svg_callback())

    @_only_execute_if_logging_is_active
    def log_parent_child_relationships_for_placeholders(self):
        self._html_generator.add_h2("Ensure Accurate Parent-Child Relationships for Placeholders")
        self._html_generator.add_paragraph("Graph after adding parent-child relationships for placeholders:")
        self._html_generator.add_svg(self._get_svg_callback())

    @_only_execute_if_logging_is_active
    def log_repeating_steps_start(self):
        self._html_generator.add_h1("Repeating Steps")

    @_only_execute_if_logging_is_active
    def log_round_start(self):
        self._html_generator.add_h2(f"{next(self._current_round_counter)}. Round")

    @_only_execute_if_logging_is_active
    def log_round_end(self):
        self._html_generator.add_paragraph("Graph at end of round:")
        self._html_generator.add_svg(self._get_svg_callback())

    @_only_execute_if_logging_is_active
    def log_loop_detected(self):
        self._html_generator.add_paragraph("Loop detected")
        self._html_generator.generate_html_file()

    @_only_execute_if_logging_is_active
    def log_repeating_steps_finished(self):
        self._html_generator.add_paragraph("Repeating steps finished successfully")

    @_only_execute_if_logging_is_active
    def log_resolved_placeholder(self, derive_path: str):
        self._current_round_resolved_placeholders.append(derive_path)

    @_only_execute_if_logging_is_active
    def log_resolve_placeholder_finished(self):
        self._html_generator.add_h3("Resolve Placeholders")

        if self._current_round_resolved_placeholders:
            self._html_generator.add_scrollable_div_with_description(
                "Resolved placeholders", "<br />".join(self._current_round_resolved_placeholders)
            )
            self._html_generator.add_paragraph("Graph after resolving placeholders:")
            self._html_generator.add_svg(self._get_svg_callback())
        else:
            self._html_generator.add_paragraph("No placeholders resolved in this round")

        self._current_round_resolved_placeholders = []

    @_only_execute_if_logging_is_active
    def log_processable_elements(self, topological_sorted_nodes: list[_ElementNode]):
        self._html_generator.add_h3("Processable Elements")

        if not topological_sorted_nodes:
            self._html_generator.add_paragraph("No processable elements found")
            return

        self._html_generator.add_scrollable_div_with_description(
            "Elements to process (sorted by process order ascending)",
            "<br />".join(
                [f"{node.node_id}: {node.name or 'no name'} ({node.level.value})" for node in topological_sorted_nodes]
            ),
        )

    @_only_execute_if_logging_is_active
    def log_finalize(self):
        self._html_generator.generate_html_file()


class Resolver:
    def __init__(self, resolver_logging_file_path: None | str):
        self._resolver_graph = _ResolverGraph()
        self._root_node_: None | _ElementNode = None
        self.logger = _ResolverLogger(resolver_logging_file_path, self._resolver_graph.get_svg)
        self._repeating_steps_finisehd_after_current_round = False

    @property
    def _root_node(self) -> _ElementNode:
        if self._root_node_ is None:
            raise ResolveException("Root node is not set")

        return self._root_node_

    def initialization(self, device: Device):
        self._construct_directed_graph(device)
        self.logger.log_init_constructed_graph()

        self._ensure_accurate_parent_child_relationships_for_placeholders()
        self.logger.log_parent_child_relationships_for_placeholders()

    def finalize_processing(self):
        self._resolver_graph.bottom_up_sibling_traversal(self._finalize_siblings)

    def repeating_steps_finished_after_current_round(self) -> bool:
        return self._repeating_steps_finisehd_after_current_round

    def resolve_placeholders(self):
        for placeholder in list(self._resolver_graph.get_placeholders()):  # copy to avoid modifying list while iter.
            self._resolve_placeholder(placeholder)

        self.logger.log_resolve_placeholder_finished()

    def get_topological_sorted_processable_elements(self) -> list[tuple[int, ParsedPeripheralTypes]]:
        processable_nodes = self._find_processable_nodes()
        topological_sorted_nodes = self._resolver_graph.get_topological_sorted_nodes(processable_nodes)

        processable_elements: list[tuple[int, ParsedPeripheralTypes]] = []
        for node in topological_sorted_nodes:
            if isinstance(node.parsed, SVDDevice):
                raise ResolveException("Device node should not be in processable nodes")
            processable_elements.append((node.node_id, node.parsed))

        self.logger.log_processable_elements(topological_sorted_nodes)

        return processable_elements

    def get_base_element(self, derive_node_id: int) -> tuple[None | ProcessedPeripheralTypes, int]:
        derived_node = self._resolver_graph.get_element_node_by_node_id(derive_node_id)

        if derived_node is None:
            raise ResolveException(f"_ElementNode with node_id '{derive_node_id}' not found")

        base_node = self._resolver_graph.get_base_element_node(derived_node)

        if base_node is None:
            raise ResolveException(f"Base node not found for node '{derived_node.name}'")

        if derived_node.level != base_node.level:
            raise ResolveException(
                f"Node '{derived_node.name}' and its base node '{base_node.name}' have different levels"
            )

        if isinstance(base_node.processed_or_none, Device):
            raise ResolveException("Base node can't be a Device")

        return base_node.processed_or_none, base_node.node_id

    def update_element(self, node_id: int, base_node_id: None | int, processed: ProcessedPeripheralTypes):
        node = self._resolver_graph.get_element_node_by_node_id(node_id)
        if node is None:
            raise ResolveException(f"Element with node_id '{node_id}' not found")

        self._update_element(node, base_node_id, processed)

    def update_enumerated_value_container(self, node_id: int, base_node_id: None | int):
        node = self._resolver_graph.get_element_node_by_node_id(node_id)

        if node is None:
            raise ResolveException(f"Element with node_id '{node_id}' not found")

        # if base_node_id is not None, update the node with the base node's parsed attribute (copy from base)
        if base_node_id is not None:
            base_node = self._resolver_graph.get_element_node_by_node_id(base_node_id)

            if base_node is None:
                raise ResolveException(f"Base element with node_id '{base_node_id}' not found")

            node.parsed = cast(SVDEnumeratedValueContainer, base_node.parsed)
            self._post_process_derive(node, base_node_id)

        # update node
        node.status = _NodeStatus.PROCESSED

    def _update_element(
        self,
        node: _ElementNode,
        base_node_id: None | int,
        processed: ProcessedPeripheralTypes,
        is_dim_template: bool = False,
    ):
        # if derived, remove the derive edge and replicate the base node's descendants as descendants of current node
        self._post_process_derive(node, base_node_id)

        # update node
        node.status = _NodeStatus.PROCESSED
        node.processed = processed
        if is_dim_template:
            node.is_dim_template = True

        # update outgoing CHILD_UNRESOLVED edges to CHILD_RESOLVED
        for child in self._resolver_graph.get_element_childrens(node):
            self._resolver_graph.update_edge(node, child, _EdgeType.CHILD_RESOLVED)

    def _post_process_derive(self, node: _ElementNode, base_node_id: None | int):
        if base_node_id is None:
            return

        base_node = self._resolver_graph.get_element_node_by_node_id(base_node_id)
        if base_node is None:
            raise ResolveException(f"Base element with node_id '{base_node_id}' not found")

        # remove the derive edge
        self._resolver_graph.remove_edge(base_node, node)

        # replicate the base node's descendants as descendants of current node
        self._resolver_graph.replicate_descendants(base_node, node)

    def update_dim_element(
        self,
        node_id: int,
        base_node_id: None | int,
        processed_elements: list[ProcessedDimablePeripheralTypes],
        processed_dim_element: ProcessedDimablePeripheralTypes,
    ):
        node = self._resolver_graph.get_element_node_by_node_id(node_id)
        if node is None:
            raise ResolveException(f"Element with node_id '{node_id}' not found")

        # update dim element itself (must be called before the new nodes are created in the next step)
        self._update_element(node, base_node_id, processed_dim_element, is_dim_template=True)

        # _ElementNode has one parent, except parents are also dim nodes
        parents = self._resolver_graph.get_element_parents(node)

        # create new nodes
        new_nodes: list[_ElementNode] = []
        for parent in parents:
            for processed_element in processed_elements:
                new_node = _ElementNode(
                    name=processed_element.name,
                    level=node.level,
                    status=_NodeStatus.PROCESSED,
                    parsed=node.parsed,
                    processed=processed_element,
                )
                self._resolver_graph.add_element_child(parent, new_node, _EdgeType.CHILD_RESOLVED)
                new_nodes.append(new_node)

        # create edges to childs
        for new_node in new_nodes:
            for child in self._resolver_graph.get_element_childrens(node):
                self._resolver_graph.add_edge(new_node, child, _EdgeType.CHILD_RESOLVED)

    def _find_processable_nodes(self) -> list[_ElementNode]:
        not_allowed_edge_types = {
            _EdgeType.PLACEHOLDER,
        }

        result: list[_ElementNode] = []
        visited: set[_ElementNode] = set()
        stack: list[_ElementNode] = []

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

        self._update_are_repeating_steps_finished_after_current_round({node.node_id for node in result})
        return result

    def _update_are_repeating_steps_finished_after_current_round(self, getting_processed_node_ids: set[int]):
        unprocessed_node_ids = self._resolver_graph.get_unprocessed_node_ids()
        unprocessed_after_round_node_ids = unprocessed_node_ids - getting_processed_node_ids

        if not unprocessed_after_round_node_ids:
            self._repeating_steps_finisehd_after_current_round = True

    def _resolve_placeholder(self, placeholder: _PlaceholderNode):
        if not self._is_placeholder_parent_resolved(placeholder):
            return

        derive_node = self._get_placeholder_derive_node(placeholder)
        base_node = self._find_base_node(derive_node, placeholder.derive_path)

        if base_node is None:
            return

        self._resolver_graph.remove_placeholder(placeholder)

        try:
            self._resolver_graph.add_edge(base_node, derive_node, _EdgeType.DERIVE)
        except rx.DAGWouldCycle as exc:  # pylint: disable=no-member
            message = (
                f"Inheritance cycle detected for node '{derive_node.name}' with derive path {placeholder.derive_path}"
            )
            raise ResolveException(message) from exc

        self.logger.log_resolved_placeholder(placeholder.derive_path)

    def _find_base_node(self, derived_node: _ElementNode, derive_path: str) -> None | _ElementNode:
        derive_path_parts = derive_path.split(".")
        level = derived_node.level

        def find_base_node_recursive(node: _ElementNode, path_parts: list[str]) -> None | _ElementNode:
            if node.node_id == derived_node.node_id:
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

        def find_base_node_in_nodes(nodes: list[_ElementNode]) -> None | _ElementNode:
            base_nodes: list[_ElementNode] = []
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

    def _get_placeholder_derive_node(self, placeholder: _PlaceholderNode) -> _ElementNode:
        return self._resolver_graph.get_placeholder_child(placeholder)

    def _is_placeholder_parent_resolved(self, placeholder: _PlaceholderNode) -> bool:
        parent = self._resolver_graph.get_placeholder_parent(placeholder)

        if parent.status == _NodeStatus.PROCESSED:
            return True

        return False

    def _finalize_siblings(self, parent: _ElementNode, siblings: list[_ElementNode]):
        if parent.is_dim_template:
            return

        if isinstance(parent.processed, Device):
            self._finalize_device(parent, siblings)
        elif isinstance(parent.processed, Peripheral):
            self._finalize_peripheral(parent, siblings)
        elif isinstance(parent.processed, Cluster):
            self._finalize_cluster(parent, siblings)
        elif isinstance(parent.processed, Register):
            self._finalize_register(parent, siblings)
        elif isinstance(parent.processed, Field):
            self._finalize_field(parent, siblings)
        else:
            raise ResolveException("Unknown node type")

    def _finalize_device(self, device_node: _ElementNode, children_nodes: list[_ElementNode]):
        device = cast(Device, device_node.processed)
        peripherals = [cast(Peripheral, node.processed) for node in children_nodes if not node.is_dim_template]

        device.peripherals = sorted(peripherals, key=lambda p: (p.base_address, p.name))

        self._inherit_register_properties(device)

    def _finalize_peripheral(self, peripheral_node: _ElementNode, children_nodes: list[_ElementNode]):
        peripheral = cast(Peripheral, peripheral_node.processed)
        peripheral.size = self._calculate_size(
            peripheral_node, [cast(Register | Cluster, node.processed) for node in children_nodes]
        )

        registers_clusters = [
            cast(Register | Cluster, node.processed) for node in children_nodes if not node.is_dim_template
        ]

        peripheral.registers_clusters = sorted(registers_clusters, key=lambda rc: (rc.address_offset, rc.name))

    def _finalize_cluster(self, cluster_node: _ElementNode, children_nodes: list[_ElementNode]):
        cluster = cast(Cluster, cluster_node.processed)
        cluster.size = self._calculate_size(
            cluster_node, [cast(Register | Cluster, node.processed) for node in children_nodes]
        )

        registers_clusters = [
            cast(Register | Cluster, node.processed) for node in children_nodes if not node.is_dim_template
        ]

        cluster.registers_clusters = sorted(registers_clusters, key=lambda rc: (rc.address_offset, rc.name))

    def _finalize_register(self, register_node: _ElementNode, children_nodes: list[_ElementNode]):
        register = cast(Register, register_node.processed)
        fields = [cast(Field, node.processed) for node in children_nodes if not node.is_dim_template]

        register.fields = sorted(fields, key=lambda f: (f.lsb, f.name))

    def _finalize_field(self, field_node: _ElementNode, children_nodes: list[_ElementNode]):
        field = cast(Field, field_node.processed)
        enum_containers: list[EnumeratedValueContainer] = []
        for child in children_nodes:
            enum_container = _ProcessEnumeratedValueContainers().create_enumerated_value_container(
                cast(SVDEnumeratedValueContainer, child.parsed), field.lsb, field.msb
            )
            enum_containers.append(enum_container)

        field.enumerated_value_containers = enum_containers

    def _calculate_size(self, node: _ElementNode, child_elements: list[Register | Cluster]) -> int:
        element = cast(Register | Cluster, node.processed)

        own_size = element.size if element.size is not None else -1

        inherited_size = self._get_parent_size_recursively(node)

        child_sizes = [child.size for child in child_elements if child.size is not None]
        max_child_size = max(child_sizes) if child_sizes else -1

        return max(own_size, inherited_size, max_child_size)

    def _get_parent_size_recursively(self, node: _ElementNode) -> int:
        parents = self._resolver_graph.get_element_parents(node)

        if not parents:
            return -1

        parent = parents[0]  # only dim nodes have multiple parents, but all have same size
        element = cast(Cluster | Peripheral | Device, parent.processed)

        if element.size is not None:
            return element.size

        return self._get_parent_size_recursively(parent)

    def _inherit_register_properties(self, device: Device):
        for peripheral in device.peripherals:
            peripheral.size = _or_if_none(peripheral.size, device.size)
            peripheral.access = _or_if_none(peripheral.access, device.access)
            peripheral.protection = _or_if_none(peripheral.protection, device.protection)
            peripheral.reset_value = _or_if_none(peripheral.reset_value, device.reset_value)
            peripheral.reset_mask = _or_if_none(peripheral.reset_mask, device.reset_mask)

            self._inherit_register_properties_registers_clusters(
                peripheral.registers_clusters,
                peripheral.size,
                peripheral.access,
                peripheral.protection,
                peripheral.reset_value,
                peripheral.reset_mask,
            )

    def _inherit_register_properties_registers_clusters(
        self,
        registers_clusters: list[Cluster | Register],
        size: None | int,
        access: None | AccessType,
        protection: None | ProtectionStringType,
        reset_value: None | int,
        reset_mask: None | int,
    ):
        for register_cluster in registers_clusters:
            register_cluster.size = _or_if_none(register_cluster.size, size)
            register_cluster.access = _or_if_none(register_cluster.access, access)
            register_cluster.protection = _or_if_none(register_cluster.protection, protection)
            register_cluster.reset_value = _or_if_none(register_cluster.reset_value, reset_value)
            register_cluster.reset_mask = _or_if_none(register_cluster.reset_mask, reset_mask)

            if isinstance(register_cluster, Cluster):
                self._inherit_register_properties_registers_clusters(
                    register_cluster.registers_clusters,
                    register_cluster.size,
                    register_cluster.access,
                    register_cluster.protection,
                    register_cluster.reset_value,
                    register_cluster.reset_mask,
                )
            elif isinstance(register_cluster, Register):  # pyright: ignore[reportUnnecessaryIsInstance]
                self._inherit_register_properties_fields(
                    register_cluster.fields,
                    register_cluster.access,
                )
            else:
                raise ResolveException("Unknown register cluster type")

    def _inherit_register_properties_fields(self, fields: list[Field], access: None | AccessType):
        for field in fields:
            field.access = _or_if_none(field.access, access)

    def _construct_directed_graph(self, device: Device):
        self._root_node_ = _ElementNode(
            name="Device",
            level=_ElementLevel.DEVICE,
            status=_NodeStatus.PROCESSED,
            parsed=device.parsed,
            processed=device,
        )
        self._resolver_graph.add_root(self._root_node)
        self._constr_graph_peripherals(device.parsed.peripherals, self._root_node)

    def _ensure_accurate_parent_child_relationships_for_placeholders(self):
        for placeholder in self._resolver_graph.get_placeholders():
            co_parent = self._resolver_graph.get_placeholder_co_parent(placeholder)

            if co_parent is None:
                continue

            self._resolver_graph.add_edge(co_parent, placeholder, _EdgeType.PLACEHOLDER)

    def _add_child_to_graph_and_handle_derive_from(self, child_node: _ElementNode, parent_node: _ElementNode):
        if parent_node.status == _NodeStatus.PROCESSED:
            edge_type = _EdgeType.CHILD_RESOLVED
        else:
            edge_type = _EdgeType.CHILD_UNRESOLVED

        self._resolver_graph.add_element_child(parent_node, child_node, edge_type)

        if not isinstance(child_node.parsed, SVDDevice):
            if child_node.parsed.derived_from is not None:
                placeholder_node = _PlaceholderNode(derive_path=child_node.parsed.derived_from)
                self._resolver_graph.add_placeholder(placeholder_node, child_node)

    def _constr_graph_peripherals(self, parsed_peripherals: list[SVDPeripheral], parent_node: _ElementNode):
        for parsed_peripheral in parsed_peripherals:
            peripheral_node = _ElementNode(
                name=parsed_peripheral.name,
                level=_ElementLevel.PERIPHERAL,
                status=_NodeStatus.UNPROCESSED,
                parsed=parsed_peripheral,
            )
            self._add_child_to_graph_and_handle_derive_from(peripheral_node, parent_node)
            self._constr_graph_registers_clusters(parsed_peripheral.registers_clusters, peripheral_node)

    def _constr_graph_registers_clusters(
        self, parsed_registers_clusters: list[SVDCluster | SVDRegister], parent_node: _ElementNode
    ):
        for parsed_register_cluster in parsed_registers_clusters:
            if isinstance(parsed_register_cluster, SVDCluster):
                cluster_node = _ElementNode(
                    name=parsed_register_cluster.name,
                    level=_ElementLevel.CLUSTER,
                    status=_NodeStatus.UNPROCESSED,
                    parsed=parsed_register_cluster,
                )
                self._add_child_to_graph_and_handle_derive_from(cluster_node, parent_node)
                self._constr_graph_registers_clusters(parsed_register_cluster.registers_clusters, cluster_node)
            elif isinstance(parsed_register_cluster, SVDRegister):  # pyright: ignore[reportUnnecessaryIsInstance]
                register_node = _ElementNode(
                    name=parsed_register_cluster.name,
                    level=_ElementLevel.REGISTER,
                    status=_NodeStatus.UNPROCESSED,
                    parsed=parsed_register_cluster,
                )
                self._add_child_to_graph_and_handle_derive_from(register_node, parent_node)
                self._constr_graph_fields(parsed_register_cluster.fields, register_node)

    def _constr_graph_fields(self, parsed_fields: list[SVDField], parent_node: _ElementNode):
        for parsed_field in parsed_fields:
            field_node = _ElementNode(
                name=parsed_field.name,
                level=_ElementLevel.FIELD,
                status=_NodeStatus.UNPROCESSED,
                parsed=parsed_field,
            )
            self._add_child_to_graph_and_handle_derive_from(field_node, parent_node)
            self._constr_graph_enum_containers(parsed_field.enumerated_value_containers, field_node)

    def _constr_graph_enum_containers(
        self, parsed_enum_containers: list[SVDEnumeratedValueContainer], parent_node: _ElementNode
    ):
        for parsed_enum_container in parsed_enum_containers:
            enum_container_node = _ElementNode(
                name=parsed_enum_container.name,
                level=_ElementLevel.ENUMCONT,
                status=_NodeStatus.UNPROCESSED,
                parsed=parsed_enum_container,
            )
            self._add_child_to_graph_and_handle_derive_from(enum_container_node, parent_node)


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
