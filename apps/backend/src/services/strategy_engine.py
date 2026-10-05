from typing import Any

from pydantic import ValidationError

from ..schemas import StrategyGraph
from .node_registry import ENTRY_NODE_TYPES, EXIT_NODE_TYPES, NODE_TYPES, get_legacy_node_types


class StrategyEngine:
    """Validates and executes strategy graphs.

    Validation rules and error contract: SPECS/strategy-graph.md §8.
    """

    def __init__(self):
        self.node_types = self._load_node_types()

    def _load_node_types(self) -> dict[str, dict]:
        """Load available node type definitions from the registry.

        SPECS/strategy-graph.md §5 (R1): single source of truth.
        """
        return get_legacy_node_types()

    @staticmethod
    def _check_param_type(expected: str, value: Any) -> bool:
        """Check a node data value against a registry parameter type.

        int is accepted where float is expected (JSON has no float/int
        distinction); bool is never a valid number.
        """
        if expected == "int":
            return isinstance(value, int) and not isinstance(value, bool)
        if expected == "float":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if expected == "string":
            return isinstance(value, str)
        if expected == "boolean":
            return isinstance(value, bool)
        return True

    def validate_graph(self, graph: StrategyGraph) -> tuple[bool, list[str]]:
        """Validate a strategy graph structure.

        Rules and messages: SPECS/strategy-graph.md §8 (E1-E13).
        """
        errors = []

        # E1: at least one node (early return: errors[0] is pinned by tests)
        if not graph.nodes:
            errors.append("Graph must have at least one node")
            return False, errors

        # E2: at least one edge (early return, same as before)
        if not graph.edges:
            errors.append("Graph must have at least one edge")
            return False, errors

        # E3: duplicate node ids
        seen_nodes: set[str] = set()
        for node in graph.nodes:
            if node.id in seen_nodes:
                errors.append(f"Duplicate node id: '{node.id}'")
            seen_nodes.add(node.id)

        # E4: duplicate edge ids
        seen_edges: set[str] = set()
        for edge in graph.edges:
            if edge.id in seen_edges:
                errors.append(f"Duplicate edge id: '{edge.id}'")
            seen_edges.add(edge.id)

        # E5: node types must exist; E6/E7: params must be known and typed
        for node in graph.nodes:
            if node.type not in self.node_types:
                errors.append(f"Unknown node type: {node.type}")
                continue
            definition = NODE_TYPES[node.type]
            known_params = {p["name"]: p["type"] for p in definition["parameters"]}
            for key, value in (node.data or {}).items():
                if key not in known_params:
                    errors.append(f"Unknown parameter '{key}' for node type '{node.type}'")
                elif not self._check_param_type(known_params[key], value):
                    errors.append(f"Invalid value for parameter '{key}' of node '{node.id}'")

        node_map = {n.id: n for n in graph.nodes}

        # E8/E9: entry and exit nodes
        has_entry = any(n.type in ENTRY_NODE_TYPES for n in graph.nodes)
        has_exit = any(n.type in EXIT_NODE_TYPES for n in graph.nodes)

        if not has_entry:
            errors.append("Graph must have at least one entry node (buy/sell/long/short)")
        if not has_exit:
            errors.append("Graph must have at least one exit node (close/stop_loss/take_profit)")

        # E10: edges reference valid nodes; E11: handles resolve
        node_ids = set(node_map.keys())
        for edge in graph.edges:
            if edge.source not in node_ids:
                errors.append(f"Edge '{edge.id}' references unknown source node: {edge.source}")
            if edge.target not in node_ids:
                errors.append(f"Edge '{edge.id}' references unknown target node: {edge.target}")
            source_node = node_map.get(edge.source)
            target_node = node_map.get(edge.target)
            if source_node is not None and source_node.type in NODE_TYPES and edge.sourceHandle:
                outputs = NODE_TYPES[source_node.type]["outputs"]
                if edge.sourceHandle not in outputs:
                    errors.append(
                        f"Unknown output handle '{edge.sourceHandle}'"
                        f" for node type '{source_node.type}'"
                    )
            if target_node is not None and target_node.type in NODE_TYPES and edge.targetHandle:
                inputs = NODE_TYPES[target_node.type]["inputs"]
                if edge.targetHandle not in inputs:
                    errors.append(
                        f"Unknown input handle '{edge.targetHandle}'"
                        f" for node type '{target_node.type}'"
                    )

        # E12: no isolated nodes
        connected: set[str] = set()
        for edge in graph.edges:
            connected.add(edge.source)
            connected.add(edge.target)
        for node in graph.nodes:
            if node.id not in connected:
                errors.append(f"Node '{node.id}' is not connected to the graph")

        # E13: no cycles
        if self._has_cycles(graph):
            errors.append("Graph contains cycles")

        return len(errors) == 0, errors

    def _has_cycles(self, graph: StrategyGraph) -> bool:
        """Check if graph has cycles using DFS"""
        node_map = {n.id: n for n in graph.nodes}
        adj = {n.id: [] for n in graph.nodes}
        for edge in graph.edges:
            # Skip dangling edges (already reported as E10); they cannot
            # form a cycle between known nodes.
            if edge.source in adj and edge.target in adj:
                adj[edge.source].append(edge.target)

        visited = set()
        rec_stack = set()

        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            for neighbor in adj.get(node_id, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node_id)
            return False

        for node_id in node_map:
            if node_id not in visited:
                if dfs(node_id):
                    return True
        return False

    def get_execution_order(self, graph: StrategyGraph) -> list[str]:
        """Get topological execution order of nodes"""
        # Build adjacency list
        adj = {n.id: [] for n in graph.nodes}
        in_degree = {n.id: 0 for n in graph.nodes}

        for edge in graph.edges:
            # Skip dangling edges (reported as E10 by validate_graph)
            if edge.source in adj and edge.target in adj:
                adj[edge.source].append(edge.target)
                in_degree[edge.target] += 1

        # Kahn's algorithm
        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            node_id = queue.pop(0)
            order.append(node_id)
            for neighbor in adj[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(graph.nodes):
            raise ValueError("Graph has cycles")

        return order

    def explain_strategy(self, graph: StrategyGraph) -> str:
        """Generate human-readable explanation of strategy"""
        lines = ["STRATEGY EXPLANATION", "=" * 40, ""]

        # Find entry conditions
        entry_nodes = [n for n in graph.nodes if n.type in ENTRY_NODE_TYPES]
        for entry in entry_nodes:
            action = entry.type.replace("action.", "").upper()
            lines.append(f"ENTRY: {action}")
            # Trace back to find conditions
            conditions = self._trace_conditions(graph, entry.id)
            for cond in conditions:
                lines.append(f"  - {cond}")
            lines.append("")

        # Position management
        risk_nodes = [n for n in graph.nodes if n.type.startswith("risk.")]
        if risk_nodes:
            lines.append("POSITION MANAGEMENT")
            for risk in risk_nodes:
                if risk.type == "risk.position_size":
                    pct = risk.data.get("risk_pct", "N/A")
                    lines.append(f"  Position Size: {pct}% of equity")
                elif risk.type == "risk.stop_loss":
                    pct = risk.data.get("pct", "N/A")
                    lines.append(f"  Stop Loss: {pct}%")
                elif risk.type == "risk.take_profit":
                    pct = risk.data.get("pct", "N/A")
                    lines.append(f"  Take Profit: {pct}%")
            lines.append("")

        return "\n".join(lines)

    def _trace_conditions(self, graph: StrategyGraph, node_id: str, depth: int = 0) -> list[str]:
        """Trace back from a node to find input conditions"""
        if depth > 10:  # Prevent infinite recursion
            return ["... (max depth reached)"]

        node_map = {n.id: n for n in graph.nodes}
        edges_in = [e for e in graph.edges if e.target == node_id]

        conditions = []
        for edge in edges_in:
            source = node_map.get(edge.source)
            if not source:
                continue

            if source.type.startswith("indicator."):
                indicator = source.type.replace("indicator.", "").upper()
                period = source.data.get("period", "?")
                conditions.append(f"{indicator} (period={period})")
            elif source.type.startswith("logic."):
                op = source.type.replace("logic.", "").upper()
                # Trace both inputs
                input_a = self._trace_conditions(graph, source.id, depth + 1)
                conditions.append(f"{op}: {', '.join(input_a)}")
            elif source.type.startswith("data."):
                data_type = source.type.replace("data.", "").upper()
                conditions.append(f"{data_type} price")

        return conditions

    def _dict_to_strategy_graph(self, graph_dict: dict[str, Any]) -> StrategyGraph:
        """Convert dictionary to StrategyGraph model"""
        return StrategyGraph.model_validate(graph_dict)


def validate_strategy_graph(graph_dict: dict[str, Any]) -> tuple[bool, list[str]]:
    """Standalone validation function"""
    try:
        graph = StrategyGraph.model_validate(graph_dict)
    except ValidationError as e:
        return False, [str(e)]

    engine = StrategyEngine()
    return engine.validate_graph(graph)
