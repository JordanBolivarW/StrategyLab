from typing import Any
from pydantic import ValidationError

from ..schemas import StrategyGraph, StrategyGraphNode, StrategyGraphEdge


class StrategyEngine:
    """Validates and executes strategy graphs"""

    def __init__(self):
        self.node_types = self._load_node_types()

    def _load_node_types(self) -> dict[str, dict]:
        """Load available node type definitions"""
        return {
            # Data nodes
            "data.open": {"category": "data", "outputs": ["value"]},
            "data.high": {"category": "data", "outputs": ["value"]},
            "data.low": {"category": "data", "outputs": ["value"]},
            "data.close": {"category": "data", "outputs": ["value"]},
            "data.volume": {"category": "data", "outputs": ["value"]},
            "data.timestamp": {"category": "data", "outputs": ["value"]},
            # Indicator nodes
            "indicator.sma": {"category": "indicator", "inputs": ["source", "period"], "outputs": ["value"]},
            "indicator.ema": {"category": "indicator", "inputs": ["source", "period"], "outputs": ["value"]},
            "indicator.rsi": {"category": "indicator", "inputs": ["source", "period"], "outputs": ["value"]},
            "indicator.macd": {"category": "indicator", "inputs": ["source", "fast", "slow", "signal"], "outputs": ["macd", "signal", "histogram"]},
            "indicator.atr": {"category": "indicator", "inputs": ["high", "low", "close", "period"], "outputs": ["value"]},
            "indicator.bollinger_bands": {"category": "indicator", "inputs": ["source", "period", "std_dev"], "outputs": ["upper", "middle", "lower"]},
            # Comparator nodes
            "logic.gt": {"category": "comparator", "inputs": ["a", "b"], "outputs": ["result"]},
            "logic.lt": {"category": "comparator", "inputs": ["a", "b"], "outputs": ["result"]},
            "logic.gte": {"category": "comparator", "inputs": ["a", "b"], "outputs": ["result"]},
            "logic.lte": {"category": "comparator", "inputs": ["a", "b"], "outputs": ["result"]},
            "logic.cross_above": {"category": "comparator", "inputs": ["a", "b"], "outputs": ["result"]},
            "logic.cross_below": {"category": "comparator", "inputs": ["a", "b"], "outputs": ["result"]},
            # Logic nodes
            "logic.and": {"category": "logic", "inputs": ["a", "b"], "outputs": ["result"]},
            "logic.or": {"category": "logic", "inputs": ["a", "b"], "outputs": ["result"]},
            "logic.not": {"category": "logic", "inputs": ["a"], "outputs": ["result"]},
            # Action nodes
            "action.buy": {"category": "action", "inputs": ["condition"], "outputs": ["signal"]},
            "action.sell": {"category": "action", "inputs": ["condition"], "outputs": ["signal"]},
            "action.long": {"category": "action", "inputs": ["condition"], "outputs": ["signal"]},
            "action.short": {"category": "action", "inputs": ["condition"], "outputs": ["signal"]},
            "action.close": {"category": "action", "inputs": ["condition"], "outputs": ["signal"]},
            # Risk nodes
            "risk.position_size": {"category": "risk", "inputs": ["risk_pct", "equity"], "outputs": ["size"]},
            "risk.stop_loss": {"category": "risk", "inputs": ["entry", "pct"], "outputs": ["price"]},
            "risk.take_profit": {"category": "risk", "inputs": ["entry", "pct"], "outputs": ["price"]},
        }

    def validate_graph(self, graph: StrategyGraph) -> tuple[bool, list[str]]:
        """Validate a strategy graph structure"""
        errors = []

        if not graph.nodes:
            errors.append("Graph must have at least one node")
            return False, errors

        if not graph.edges:
            errors.append("Graph must have at least one edge")
            return False, errors

        # Check node types exist
        for node in graph.nodes:
            if node.type not in self.node_types:
                errors.append(f"Unknown node type: {node.type}")

        # Check for entry and exit nodes
        entry_types = {"action.buy", "action.sell", "action.long", "action.short"}
        exit_types = {"action.close", "risk.stop_loss", "risk.take_profit"}

        has_entry = any(n.type in entry_types for n in graph.nodes)
        has_exit = any(n.type in exit_types for n in graph.nodes)

        if not has_entry:
            errors.append("Graph must have at least one entry node (buy/sell/long/short)")
        if not has_exit:
            errors.append("Graph must have at least one exit node (close/stop_loss/take_profit)")

        # Validate edges reference valid nodes
        node_ids = {n.id for n in graph.nodes}
        for edge in graph.edges:
            if edge.source not in node_ids:
                errors.append(f"Edge references unknown source node: {edge.source}")
            if edge.target not in node_ids:
                errors.append(f"Edge references unknown target node: {edge.target}")

        # Check for cycles (simplified - just check if graph is a DAG)
        if self._has_cycles(graph):
            errors.append("Graph contains cycles")

        return len(errors) == 0, errors

    def _has_cycles(self, graph: StrategyGraph) -> bool:
        """Check if graph has cycles using DFS"""
        node_map = {n.id: n for n in graph.nodes}
        adj = {n.id: [] for n in graph.nodes}
        for edge in graph.edges:
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
        entry_nodes = [n for n in graph.nodes if n.type in {"action.buy", "action.sell", "action.long", "action.short"}]
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