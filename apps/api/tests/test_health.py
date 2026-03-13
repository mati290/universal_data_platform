from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_healthcheck() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "universal-data-platform-api"


def test_healthcheck() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "environment": "local"}


def test_data_source_csv_flow() -> None:
    create_response = client.post(
        "/api/v1/data-sources",
        json={"name": "sales-csv", "source_type": "crypto", "description": "Monthly sales feed"},
    )
    assert create_response.status_code == 201
    source_id = create_response.json()["id"]
    assert create_response.json()["source_type"] == "crypto"

    csv_payload = "country,value\nPL,10\nDE,20\n".encode("utf-8")
    upload_response = client.post(
        f"/api/v1/data-sources/{source_id}/upload-csv",
        files={"file": ("sample.csv", BytesIO(csv_payload), "text/csv")},
    )
    assert upload_response.status_code == 200
    assert upload_response.json()["rows_loaded"] == 2

    data_response = client.get(f"/api/v1/data-sources/{source_id}/data")
    assert data_response.status_code == 200
    payload = data_response.json()
    assert payload["source_id"] == source_id
    assert payload["total_rows"] == 2
    assert len(payload["rows"]) == 2


def test_source_crud_endpoints() -> None:
    create_response = client.post(
        "/api/v1/sources",
        json={"name": "weather-eu", "type": "weather", "description": "Weather source"},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    source_id = created["id"]
    assert created["name"] == "weather-eu"
    assert created["type"] == "weather"
    assert created["description"] == "Weather source"
    assert "created_at" in created

    list_response = client.get("/api/v1/sources")
    assert list_response.status_code == 200
    listed_ids = [item["id"] for item in list_response.json()]
    assert source_id in listed_ids

    delete_response = client.delete(f"/api/v1/sources/{source_id}")
    assert delete_response.status_code == 204

    delete_again_response = client.delete(f"/api/v1/sources/{source_id}")
    assert delete_again_response.status_code == 404


def test_upload_endpoint_with_source_id() -> None:
    create_response = client.post(
        "/api/v1/sources",
        json={"name": "transport-feed", "type": "transport", "description": "Transport source"},
    )
    assert create_response.status_code == 201
    source_id = create_response.json()["id"]

    csv_payload = "line,delay_minutes\nA,3\nB,0\n".encode("utf-8")
    upload_response = client.post(
        "/api/v1/upload",
        data={"source_id": source_id},
        files={"file": ("transport.csv", BytesIO(csv_payload), "text/csv")},
    )
    assert upload_response.status_code == 200
    assert upload_response.json()["source_id"] == source_id
    assert upload_response.json()["rows_loaded"] == 2

    data_response = client.get(f"/api/v1/data-sources/{source_id}/data")
    assert data_response.status_code == 200
    payload = data_response.json()
    assert payload["total_rows"] == 2
    assert payload["rows"][0]["line"] == "A"


def test_raw_data_api_ingest_flow() -> None:
    create_response = client.post(
        "/api/v1/sources",
        json={"name": "api-ingest", "type": "weather", "description": "API source"},
    )
    assert create_response.status_code == 201
    source_id = create_response.json()["id"]

    ingest_response = client.post(
        "/api/v1/raw-data",
        json={
            "source_id": source_id,
            "records": [
                {"city": "Warsaw", "temperature": 19.2},
                {"city": "Gdansk", "temperature": 17.1},
            ],
        },
    )
    assert ingest_response.status_code == 201
    assert ingest_response.json() == {"source_id": source_id, "records_saved": 2}

    data_response = client.get(f"/api/v1/data-sources/{source_id}/data")
    assert data_response.status_code == 200
    payload = data_response.json()
    assert payload["total_rows"] == 2
    assert payload["rows"][0]["city"] == "Warsaw"
