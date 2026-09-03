from typing import Any

import networkx as nx

from src.application.pert.dtos.activity_dto import ActivityInputDTO


class NetworkXAdapter:
    """Adaptador de infraestructura que utiliza NetworkX para análisis topológico y validación de DAGs."""

    @classmethod
    def build_digraph(cls, activities: list[ActivityInputDTO]) -> nx.DiGraph:
        """Construye un DiGraph de NetworkX a partir de las actividades de entrada."""
        graph = nx.DiGraph()

        for act in activities:
            graph.add_node(
                act.id,
                name=act.name,
                optimistic=act.optimistic,
                most_likely=act.most_likely,
                pessimistic=act.pessimistic,
            )

        for act in activities:
            for pred_id in act.predecessors:
                # Arista dirigida desde el predecesor hacia la actividad sucesora
                graph.add_edge(pred_id, act.id)

        return graph

    @classmethod
    def validate_acyclic(cls, graph: nx.DiGraph) -> tuple[bool, list[list[str]]]:
        """Verifica si el grafo es estrictamente acíclico (DAG).

        Retorna (is_dag, cycles_found).
        """
        is_dag = nx.is_directed_acyclic_graph(graph)
        if is_dag:
            return True, []

        cycles = list(nx.simple_cycles(graph))
        return False, cycles

    @classmethod
    def get_topological_order(cls, graph: nx.DiGraph) -> list[str]:
        """Obtiene el ordenamiento topológico del grafo con NetworkX."""
        if not nx.is_directed_acyclic_graph(graph):
            return []
        return list(nx.topological_sort(graph))

    @classmethod
    def analyze_graph_metrics(cls, graph: nx.DiGraph) -> dict[str, Any]:
        """Calcula métricas estructurales del grafo."""
        is_dag = nx.is_directed_acyclic_graph(graph)
        return {
            "node_count": graph.number_of_nodes(),
            "edge_count": graph.number_of_edges(),
            "is_dag": is_dag,
            "density": nx.density(graph),
            "in_degree": dict(graph.in_degree()),
            "out_degree": dict(graph.out_degree()),
        }
