import json

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_get_index_view() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Camino Crítico &amp; PERT" in response.text or "Camino Crítico" in response.text
    assert "activities-table" in response.text


def test_post_calculate_web_view_success() -> None:
    activities = [
        {"id": "A", "name": "Tarea A", "optimistic": 3, "most_likely": 3, "pessimistic": 3, "predecessors": []},
        {"id": "B", "name": "Tarea B", "optimistic": 4, "most_likely": 4, "pessimistic": 4, "predecessors": []},
        {"id": "C", "name": "Tarea C", "optimistic": 2, "most_likely": 2, "pessimistic": 2, "predecessors": ["A"]},
        {"id": "D", "name": "Tarea D", "optimistic": 5, "most_likely": 5, "pessimistic": 5, "predecessors": ["B"]},
        {"id": "E", "name": "Tarea E", "optimistic": 3, "most_likely": 3, "pessimistic": 3, "predecessors": ["C", "D"]},
    ]

    form_data = {
        "activities_json": json.dumps(activities),
        "target_duration": "14",
    }

    response = client.post("/calculate", data=form_data)
    assert response.status_code == 200
    assert "network-container" in response.text
    assert "Diagrama de Red (AON)" in response.text
    assert "Tabla Detallada de Tiempos y Holguras" in response.text
    assert "B ➔ D ➔ E" in response.text


def test_post_calculate_web_view_cycle_error() -> None:
    activities = [
        {"id": "A", "name": "Tarea A", "optimistic": 1, "most_likely": 1, "pessimistic": 1, "predecessors": ["B"]},
        {"id": "B", "name": "Tarea B", "optimistic": 1, "most_likely": 1, "pessimistic": 1, "predecessors": ["A"]},
    ]

    form_data = {
        "activities_json": json.dumps(activities),
    }

    response = client.post("/calculate", data=form_data)
    assert response.status_code == 422
    assert "Error en el grafo" in response.text
