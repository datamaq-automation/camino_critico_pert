from src.application.pert.dtos.activity_dto import ActivityInputDTO
from src.infrastructure.graph.networkx_adapter import NetworkXAdapter


def test_networkx_dag_validation_success() -> None:
    activities = [
        ActivityInputDTO(id="A", name="Task A", optimistic=2, most_likely=2, pessimistic=2, predecessors=[]),
        ActivityInputDTO(id="B", name="Task B", optimistic=3, most_likely=3, pessimistic=3, predecessors=["A"]),
        ActivityInputDTO(id="C", name="Task C", optimistic=1, most_likely=1, pessimistic=1, predecessors=["A", "B"]),
    ]

    graph = NetworkXAdapter.build_digraph(activities)
    is_dag, cycles = NetworkXAdapter.validate_acyclic(graph)

    assert is_dag is True
    assert cycles == []

    topo_order = NetworkXAdapter.get_topological_order(graph)
    assert topo_order.index("A") < topo_order.index("B")
    assert topo_order.index("B") < topo_order.index("C")

    metrics = NetworkXAdapter.analyze_graph_metrics(graph)
    assert metrics["node_count"] == 3
    assert metrics["edge_count"] == 3
    assert metrics["is_dag"] is True


def test_networkx_cycle_detection() -> None:
    # Grafo cíclico: A -> B -> C -> A
    activities = [
        ActivityInputDTO(id="A", name="A", optimistic=1, most_likely=1, pessimistic=1, predecessors=["C"]),
        ActivityInputDTO(id="B", name="B", optimistic=1, most_likely=1, pessimistic=1, predecessors=["A"]),
        ActivityInputDTO(id="C", name="C", optimistic=1, most_likely=1, pessimistic=1, predecessors=["B"]),
    ]

    graph = NetworkXAdapter.build_digraph(activities)
    is_dag, cycles = NetworkXAdapter.validate_acyclic(graph)

    assert is_dag is False
    assert len(cycles) > 0
