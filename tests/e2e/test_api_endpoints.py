from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_api_calculate_cpm_endpoint() -> None:
    payload = {
        "activities": [
            {"id": "A", "name": "Tarea A", "optimistic": 3, "most_likely": 3, "pessimistic": 3, "predecessors": []},
            {"id": "B", "name": "Tarea B", "optimistic": 4, "most_likely": 4, "pessimistic": 4, "predecessors": []},
            {"id": "C", "name": "Tarea C", "optimistic": 2, "most_likely": 2, "pessimistic": 2, "predecessors": ["A"]},
            {"id": "D", "name": "Tarea D", "optimistic": 5, "most_likely": 5, "pessimistic": 5, "predecessors": ["B"]},
            {
                "id": "E",
                "name": "Tarea E",
                "optimistic": 3,
                "most_likely": 3,
                "pessimistic": 3,
                "predecessors": ["C", "D"],
            },
        ],
        "target_duration": 14.0,
    }

    response = client.post("/api/v1/pert/calculate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "result" in data
    assert "vis_graph" in data
    assert "mermaid_code" in data

    res = data["result"]
    assert res["project_duration"] == 12.0
    assert res["critical_paths"] == [["B", "D", "E"]]
    assert len(res["activities"]) == 5

    # Vis.js format
    vis = data["vis_graph"]
    assert "nodes" in vis
    assert "edges" in vis
    assert len(vis["nodes"]) == 5
    assert len(vis["edges"]) == 4

    # Mermaid
    assert "graph LR" in data["mermaid_code"]


def test_api_calculate_cycle_error() -> None:
    payload = {
        "activities": [
            {"id": "A", "name": "A", "optimistic": 1, "most_likely": 1, "pessimistic": 1, "predecessors": ["B"]},
            {"id": "B", "name": "B", "optimistic": 1, "most_likely": 1, "pessimistic": 1, "predecessors": ["A"]},
        ]
    }
    response = client.post("/api/v1/pert/calculate", json=payload)
    assert response.status_code == 422
    assert "ciclo" in response.json()["detail"].lower()


def test_api_validate_dag_endpoint() -> None:
    activities = [
        {"id": "A", "name": "A", "optimistic": 1, "most_likely": 1, "pessimistic": 1, "predecessors": []},
        {"id": "B", "name": "B", "optimistic": 1, "most_likely": 1, "pessimistic": 1, "predecessors": ["A"]},
    ]
    response = client.post("/api/v1/pert/validate-dag", json=activities)
    assert response.status_code == 200
    data = response.json()
    assert data["is_dag"] is True
    assert data["cycles"] == []
