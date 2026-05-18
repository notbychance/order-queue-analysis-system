from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_swagger_docs_are_available():
    response = client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_redoc_docs_are_available():
    response = client.get("/redoc")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_openapi_schema_contains_metadata_and_tags():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    assert schema["info"]["title"]
    assert "M/M/1" in schema["info"]["description"]

    tag_names = {tag["name"] for tag in schema["tags"]}

    assert "system" in tag_names
    assert "queue-analysis" in tag_names


def test_openapi_schema_contains_actual_queue_paths():
    response = client.get("/openapi.json")

    schema = response.json()
    paths = schema["paths"]

    assert "/health" in paths
    assert "/api/v1/queue/analyze" in paths
    assert "/api/v1/queue/formulas" in paths

    assert "/api/v1/queue/default" not in paths


def test_openapi_schema_uses_current_client_contract():
    response = client.get("/openapi.json")

    schema = response.json()
    properties = schema["components"]["schemas"]["QueueAnalysisResponse"]["properties"]

    assert "utilization" in properties
    assert "arrival_rate_unit" in properties
    assert "service_rate_unit" in properties
    assert "time_unit" in properties
    assert "conclusion" in properties

    assert "rho" not in properties
    assert "rate_unit" not in properties
    assert "rate_unit_label" not in properties
    assert "time_unit_label" not in properties
    assert "message" not in properties
