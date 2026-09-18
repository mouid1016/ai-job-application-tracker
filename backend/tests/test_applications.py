from collections.abc import Callable

from fastapi.testclient import TestClient


def test_application_crud_activity_and_stats(
    client: TestClient,
    register: Callable[[str, str], dict[str, str]],
    create_application: Callable[[dict[str, str], dict[str, object] | None], dict[str, object]],
) -> None:
    headers = register("Owner", "owner@example.com")
    application = create_application(headers, {"company": "OpenAI", "status": "applied"})
    application_id = application["id"]

    listed = client.get("/api/applications", headers=headers)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [application_id]

    updated = client.patch(
        f"/api/applications/{application_id}",
        headers=headers,
        json={"status": "interview", "notes": "Prepare API examples"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "interview"

    activity = client.get(f"/api/applications/{application_id}/activities", headers=headers)
    assert activity.status_code == 200
    event_types = {event["event_type"] for event in activity.json()}
    assert {"created", "status_changed", "details_updated"}.issubset(event_types)

    stats = client.get("/api/stats", headers=headers)
    assert stats.status_code == 200
    assert stats.json()["total"] == 1
    assert stats.json()["interviews"] == 1

    deleted = client.delete(f"/api/applications/{application_id}", headers=headers)
    assert deleted.status_code == 204
    assert client.get(f"/api/applications/{application_id}", headers=headers).status_code == 404


def test_users_cannot_access_each_others_applications(
    client: TestClient,
    register: Callable[[str, str], dict[str, str]],
    create_application: Callable[[dict[str, str], dict[str, object] | None], dict[str, object]],
) -> None:
    owner = register("Owner", "owner@example.com")
    outsider = register("Outsider", "outsider@example.com")
    application = create_application(owner)

    assert client.get(f"/api/applications/{application['id']}", headers=outsider).status_code == 404
    assert client.patch(f"/api/applications/{application['id']}", headers=outsider, json={"status": "offer"}).status_code == 404
    assert client.delete(f"/api/applications/{application['id']}", headers=outsider).status_code == 404
    assert client.get("/api/applications", headers=outsider).json() == []
