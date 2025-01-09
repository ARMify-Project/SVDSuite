from collections import defaultdict, deque
from typing import cast, Callable, DefaultDict, Deque
import tempfile
import copy
import rustworkx as rx
from rustworkx.visualization import graphviz_draw  # pyright: ignore[reportUnknownVariableType]

from svdsuite.resolve.graph_elements import (
    ResolverNode,
    ElementNode,
    ElementLevel,
    NodeStatus,
    PlaceholderNode,
    EdgeType,
)
from svdsuite.resolve.exception import ResolverGraphException


class ResolverGraph:
    def __init__(self):
        self._graph: rx.PyDiGraph[ResolverNode, EdgeType] = rx.PyDiGraph(check_cycle=True)  # pylint: disable=no-member
        self._node_to_rx_index: dict[ResolverNode, int] = {}
        self._placeholders: list[PlaceholderNode] = []
        self._unprocessed_rx_indicies: list[int] = []

    def add_root(self, root: ElementNode):
        rx_index = self._graph.add_node(root)
        self._node_to_rx_index[root] = rx_index

    def add_element_child(self, parent: ElementNode, child: ElementNode, edge_type: EdgeType):
        parent_rx_index = self._node_to_rx_index[parent]
        child_rx_index = self._graph.add_node(child)
        self._graph.add_edge(parent_rx_index, child_rx_index, edge_type)

        self._node_to_rx_index[child] = child_rx_index

    def add_edge(self, parent: ElementNode, child: ElementNode | PlaceholderNode, edge_type: EdgeType):
        try:
            self._graph.add_edge(self._node_to_rx_index[parent], self._node_to_rx_index[child], edge_type)
        except rx.DAGWouldCycle as exc:  # pylint: disable=no-member
            message = f"Inheritance cycle detected for parent node '{parent}' and child node {child}"
            raise ResolverGraphException(message) from exc

    def add_placeholder(self, placeholder: PlaceholderNode, derivation_node: ElementNode):
        derivation_node_rx_index = self._node_to_rx_index[derivation_node]
        placeholder_rx_index = self._graph.add_node(placeholder)
        self._graph.add_edge(placeholder_rx_index, derivation_node_rx_index, EdgeType.PLACEHOLDER)

        self._node_to_rx_index[placeholder] = placeholder_rx_index

        self._placeholders.append(placeholder)

    def get_placeholders(self) -> list[PlaceholderNode]:
        return self._placeholders

    def get_placeholder_co_parent(self, placeholder: PlaceholderNode) -> None | ElementNode:
        children = self._graph.successors(self._node_to_rx_index[placeholder])

        if not children:
            raise ResolverGraphException(f"Placeholder '{placeholder.derive_path}' has no child")

        if len(children) != 1:
            raise ResolverGraphException(f"Placeholder '{placeholder.derive_path}' has more than one child")

        parents = self._graph.predecessors(self._node_to_rx_index[children[0]])

        # only _ElementNode nodes
        parents = [parent for parent in parents if isinstance(parent, ElementNode)]

        if not parents:
            return None

        if len(parents) != 1:
            raise ResolverGraphException(f"Placeholder '{placeholder.derive_path}' has more than one co-parent")

        return parents[0]

    def get_element_parents(self, node: ElementNode) -> list[ElementNode]:
        incoming_edges = self._graph.in_edges(self._node_to_rx_index[node])

        parents = [
            self._graph[parent_rx_index]
            for parent_rx_index, _, edge_data in incoming_edges
            if isinstance(self._graph[parent_rx_index], ElementNode)
            and edge_data in (EdgeType.CHILD_UNRESOLVED, EdgeType.CHILD_RESOLVED)
        ]

        return cast(list[ElementNode], parents)

    def get_element_childrens(self, node: ElementNode) -> list[ElementNode]:
        outgoing_edges = self._graph.out_edges(self._node_to_rx_index[node])

        children = [
            self._graph[child_rx_index]
            for _, child_rx_index, edge_data in outgoing_edges
            if isinstance(self._graph[child_rx_index], ElementNode)
            and edge_data in (EdgeType.CHILD_UNRESOLVED, EdgeType.CHILD_RESOLVED)
        ]

        return cast(list[ElementNode], children)

    def get_element_siblings(self, node: ElementNode) -> list[ElementNode]:
        parents = self.get_element_parents(node)

        if not parents:
            return []

        # _ElementNode has one parent, except resolved dim nodes, which may have multiple with the same children
        # hence, the first parent suffices to find siblings
        parent = parents[0]

        siblings: list[ElementNode] = []
        for child in self._graph.successors(self._node_to_rx_index[parent]):
            if not isinstance(child, ElementNode):
                continue

            if child == node:
                continue

            siblings.append(child)

        return siblings

    def remove_placeholder(self, placeholder: PlaceholderNode):
        self._remove_node(placeholder)
        self._placeholders.remove(placeholder)

    def remove_node(self, node: ElementNode):
        self._remove_node(node)

    def _remove_node(self, node: ElementNode | PlaceholderNode):
        rx_index = self._node_to_rx_index[node]
        self._graph.remove_node(rx_index)

        del self._node_to_rx_index[node]

    def has_incoming_edge_of_types(self, node: ElementNode, edge_types_to_find: set[EdgeType]) -> bool:
        rx_index = self._node_to_rx_index[node]
        for _, _, edge_type in self._graph.in_edges(rx_index):
            if edge_type in edge_types_to_find:
                return True
        return False

    def get_topological_sorted_nodes(self, nodes: list[ElementNode]) -> list[ElementNode]:
        def sort_key(node: ResolverNode) -> str:
            # correct type of node for static type checking
            node = cast(ElementNode, node)

            # derived nodes should be processed as late as possible
            if self.has_incoming_edge_of_types(node, {EdgeType.DERIVE}):
                return "B"

            return "A"

        subgraph = self._graph.subgraph(
            [self._node_to_rx_index[node] for node in nodes if node.status == NodeStatus.UNPROCESSED]
        )

        topological_sorted_nodes = rx.lexicographical_topological_sort(  # pylint: disable=no-member
            subgraph, key=sort_key
        )

        del subgraph

        # correct type of topological_sorted_nodes for static type checking
        return cast(list[ElementNode], topological_sorted_nodes)

    def get_base_element_node(self, derive_node: ElementNode) -> None | ElementNode:
        for parent_rx_index, _, edge_type in self._graph.in_edges(self._node_to_rx_index[derive_node]):
            if edge_type == EdgeType.DERIVE:
                return cast(ElementNode, self._graph[parent_rx_index])

        return None

    def remove_edge(self, parent: ElementNode, child: ElementNode):
        parent_rx_index = self._node_to_rx_index[parent]
        child_rx_index = self._node_to_rx_index[child]

        self._graph.remove_edge(parent_rx_index, child_rx_index)

    def update_edge(self, parent: ElementNode, child: ElementNode, edge_type: EdgeType):
        parent_rx_index = self._node_to_rx_index[parent]
        child_rx_index = self._node_to_rx_index[child]

        self._graph.update_edge(parent_rx_index, child_rx_index, edge_type)

    def get_placeholder_child(self, placeholder: PlaceholderNode) -> ElementNode:
        outgoing_edges = self._graph.out_edges(self._node_to_rx_index[placeholder])

        children = [
            self._graph[child_rx_index]
            for _, child_rx_index, edge_data in outgoing_edges
            if isinstance(self._graph[child_rx_index], ElementNode) and edge_data == EdgeType.PLACEHOLDER
        ]

        if not children:
            raise ResolverGraphException(f"Placeholder '{placeholder.derive_path}' has no children")

        if len(children) != 1:
            raise ResolverGraphException(f"Placeholder '{placeholder.derive_path}' has more than one child")

        return cast(ElementNode, children[0])

    def get_placeholder_parent(self, placeholder: PlaceholderNode) -> ElementNode:
        incoming_edges = self._graph.in_edges(self._node_to_rx_index[placeholder])

        parents = [
            self._graph[parent_rx_index]
            for parent_rx_index, _, edge_data in incoming_edges
            if isinstance(self._graph[parent_rx_index], ElementNode) and edge_data == EdgeType.PLACEHOLDER
        ]

        if not parents:
            raise ResolverGraphException(f"Placeholder '{placeholder.derive_path}' has no parent")

        if len(parents) != 1:
            raise ResolverGraphException(f"Placeholder '{placeholder.derive_path}' has more than one parent")

        return cast(ElementNode, parents[0])

    def replicate_descendants(self, source_node: ElementNode, target_node: ElementNode):
        source_rx_index = self._node_to_rx_index[source_node]

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
                if edge_type == EdgeType.DERIVE:
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

            self._node_to_rx_index[new_node] = new_node_rx_index

            if isinstance(new_node, PlaceholderNode):
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
                if edge_type == EdgeType.DERIVE:
                    self._graph.add_edge(parent_rx_index, replica_mapping[rx_index], edge_type)

        # find immediate children of source_node that are part of the replication
        immediate_children = [
            child_rx_index
            for _, child_rx_index, _ in self._graph.out_edges(source_rx_index)
            if child_rx_index in rx_indices_to_replicate
        ]

        # attach the replicated subgraph to target_node
        target_rx_index = self._node_to_rx_index[target_node]
        for child_rx_index in immediate_children:
            replicated_child_rx_index = replica_mapping[child_rx_index]
            if isinstance(self._graph[replicated_child_rx_index], PlaceholderNode):
                self._graph.add_edge(target_rx_index, replicated_child_rx_index, EdgeType.PLACEHOLDER)
            else:
                self._graph.add_edge(
                    target_rx_index,
                    replicated_child_rx_index,
                    (
                        EdgeType.CHILD_RESOLVED
                        if source_node.status == NodeStatus.PROCESSED
                        else EdgeType.CHILD_UNRESOLVED
                    ),
                )

    def get_unprocessed_root_nodes(self) -> list[ElementNode]:
        def filter_function(node: ResolverNode) -> bool:
            return isinstance(node, ElementNode) and node.status == NodeStatus.UNPROCESSED

        rx_indices = self._graph.filter_nodes(filter_function)
        self._unprocessed_rx_indicies = list(rx_indices)

        unprocessed_root_nodes: list[ElementNode] = []
        for rx_index in rx_indices:
            for _, _, edge_data in self._graph.in_edges(rx_index):
                if edge_data == EdgeType.CHILD_RESOLVED:
                    unprocessed_root_nodes.append(cast(ElementNode, self._graph[rx_index]))
                    break

        return unprocessed_root_nodes

    def get_unprocessed_nodes(self) -> set[ElementNode]:
        return {cast(ElementNode, self._graph[rx_index]) for rx_index in self._unprocessed_rx_indicies}

    def bottom_up_node_traversal(self, finalize_node_cb: Callable[[ElementNode, list[ElementNode]], None]):
        # Step 1: Build data structures
        pending_children: dict[ElementNode, int] = {}
        children_of_node: DefaultDict[ElementNode, list[ElementNode]] = defaultdict(list)
        parents_of_node: DefaultDict[ElementNode, list[ElementNode]] = defaultdict(list)

        # Get all nodes
        all_nodes_rx_indices = self._graph.node_indices()
        for rx_index in all_nodes_rx_indices:
            node = cast(ElementNode, self._graph[rx_index])
            # Get children
            children = cast(list[ElementNode], self._graph.successors(rx_index))
            children_of_node[node].extend(children)
            # Set pending_children[node] = number of children
            pending_children[node] = len(children)
            # For each child, add node as parent
            for child in children:
                parents_of_node[child].append(node)

        # Step 2: Initialize queue with nodes whose pending_children[node] == 0 (leaves)
        queue: Deque[ElementNode] = deque()
        for node, count in pending_children.items():
            if count == 0:
                queue.append(node)

        # Step 3: Process nodes (call finalize_node callback) in a bottom-up manner
        while queue:
            node = queue.popleft()
            # Call finalize_node for the node and its children, but only node is not a leaf (empty children)
            children = children_of_node[node]
            if children:
                finalize_node_cb(node, children)
            # For each parent of the node
            for parent in parents_of_node[node]:
                # Decrement pending_children[parent]
                pending_children[parent] -= 1
                if pending_children[parent] == 0:
                    # Add parent to the queue
                    queue.append(parent)

    def get_svg(self) -> str:
        def node_attr_fn(node: ResolverNode) -> dict[str, str]:
            if isinstance(node, ElementNode):
                if node.level == ElementLevel.DEVICE:
                    return {"label": "Device", "color": "blue", "fontcolor": "blue"}

                return {
                    "label": (
                        f"{node.name}\n({node.level.value})\nrx_index: {self._node_to_rx_index[node]}"
                        if node.name
                        else f"no name\n({node.level.value})\nrx_index: {self._node_to_rx_index[node]}"
                    ),
                    "color": "black" if node.status == NodeStatus.UNPROCESSED else "blue",
                    "fontcolor": "black" if node.status == NodeStatus.UNPROCESSED else "blue",
                }
            elif isinstance(node, PlaceholderNode):
                return {
                    "label": f"{node.derive_path}\n(Placeholder)\nrx_index: {self._node_to_rx_index[node]}",
                    "color": "red",
                    "fontcolor": "red",
                }
            else:
                return {}

        def edge_attr_fn(edge: EdgeType) -> dict[str, str]:
            if edge == EdgeType.CHILD_UNRESOLVED:
                return {"color": "black"}
            elif edge == EdgeType.CHILD_RESOLVED:
                return {"color": "blue"}
            elif edge == EdgeType.PLACEHOLDER:
                return {"color": "red"}
            elif edge == EdgeType.DERIVE:
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

    def _create_replicated_node(self, existing_node: ResolverNode) -> ResolverNode:
        if isinstance(existing_node, ElementNode):
            return ElementNode(
                name=existing_node.name,
                level=existing_node.level,
                status=existing_node.status,
                parsed=existing_node.parsed,
                processed=copy.copy(existing_node.processed_or_none),
                is_dim_template=existing_node.is_dim_template,
            )

        if isinstance(existing_node, PlaceholderNode):
            return PlaceholderNode(derive_path=existing_node.derive_path)

        raise ResolverGraphException("Unknown node type")
