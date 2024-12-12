import itertools
from typing import Any, Callable

from svdsuite.resolve.graph import ResolverGraph
from svdsuite.resolve.graph_elements import ElementNode
from svdsuite.util.html_generator import HTMLGenerator


class ResolverLogger:
    def __init__(self, resolver_logging_file_path: None | str, resolver_graph: ResolverGraph):
        self._resolver_logging_file_path = resolver_logging_file_path
        self._resolver_graph = resolver_graph
        self._current_round_counter = itertools.count(1)
        self._current_round_resolved_placeholders: list[str] = []

        if self._resolver_logging_file_path is not None:
            self._html_generator = HTMLGenerator(self._resolver_logging_file_path)

    @staticmethod
    def _only_execute_if_logging_is_active[R](method: Callable[..., R]) -> Callable[..., R | None]:
        def wrapper(self: "ResolverLogger", *args: Any, **kwargs: Any) -> R | None:
            if self._resolver_logging_file_path is None:  # pylint: disable=protected-access
                return None
            return method(self, *args, **kwargs)

        return wrapper

    @_only_execute_if_logging_is_active
    def log_init_constructed_graph(self):
        self._html_generator.add_h1("Initialization")
        self._html_generator.add_h2("Construct Directed Graph")
        self._html_generator.add_paragraph("Graph after construction:")
        self._html_generator.add_svg(self._resolver_graph.get_svg())

    @_only_execute_if_logging_is_active
    def log_parent_child_relationships_for_placeholders(self):
        self._html_generator.add_h2("Ensure Accurate Parent-Child Relationships for Placeholders")
        self._html_generator.add_paragraph("Graph after adding parent-child relationships for placeholders:")
        self._html_generator.add_svg(self._resolver_graph.get_svg())

    @_only_execute_if_logging_is_active
    def log_repeating_steps_start(self):
        self._html_generator.add_h1("Repeating Steps")

    @_only_execute_if_logging_is_active
    def log_round_start(self):
        self._html_generator.add_h2(f"{next(self._current_round_counter)}. Round")

    @_only_execute_if_logging_is_active
    def log_round_end(self):
        self._html_generator.add_paragraph("Graph at end of round:")
        self._html_generator.add_svg(self._resolver_graph.get_svg())

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
            self._html_generator.add_svg(self._resolver_graph.get_svg())
        else:
            self._html_generator.add_paragraph("No placeholders resolved in this round")

        self._current_round_resolved_placeholders = []

    @_only_execute_if_logging_is_active
    def log_processable_elements(self, topological_sorted_nodes: list[ElementNode]):
        self._html_generator.add_h3("Processable Elements")

        if not topological_sorted_nodes:
            self._html_generator.add_paragraph("No processable elements found")
            return

        self._html_generator.add_scrollable_div_with_description(
            "Elements to process (sorted by process order ascending)",
            "<br />".join(
                [
                    f"{self._resolver_graph._node_to_rx_index[node]}: "  # pylint: disable=W0212  #pyright: ignore[reportPrivateUsage]
                    f"{node.name or 'no name'} ({node.level.value})"
                    for node in topological_sorted_nodes
                ]
            ),
        )

    @_only_execute_if_logging_is_active
    def log_finalize(self):
        self._html_generator.generate_html_file()
