from fastapi.testclient import TestClient

from main import app


client = TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 50000))


def test_untrusted_host_is_rejected() -> None:
    response = client.get("/api/health", headers={"Host": "attacker.example"})
    assert response.status_code == 400


def test_remote_client_is_rejected() -> None:
    remote_client = TestClient(
        app, base_url="http://127.0.0.1", client=("203.0.113.10", 50000)
    )
    response = remote_client.get("/api/health")
    assert response.status_code == 403


def test_cors_is_not_exposed() -> None:
    response = client.options(
        "/api/health",
        headers={
            "Origin": "https://attacker.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in response.headers


def test_run_requires_local_control_header() -> None:
    response = client.post("/api/projects/not-a-real-project/run")
    assert response.status_code == 403


def test_local_control_header_is_accepted() -> None:
    response = client.post(
        "/api/projects/not-a-real-project/pause",
        headers={"X-AIPE-Control": "1"},
    )
    assert response.status_code == 200


def test_shutdown_requires_local_control_header() -> None:
    # Do not send the valid header here: a regression would terminate the test
    # process, which is exactly what this guard is intended to prevent.
    response = client.post("/api/shutdown")
    assert response.status_code == 403
