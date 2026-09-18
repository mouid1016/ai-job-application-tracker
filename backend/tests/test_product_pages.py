from collections.abc import Callable
from datetime import date, timedelta

from fastapi.testclient import TestClient


def test_analytics_are_private_and_calculated_from_pipeline(
    client: TestClient,
    register: Callable[[str, str], dict[str, str]],
    create_application: Callable[[dict[str, str], dict[str, object] | None], dict[str, object]],
) -> None:
    owner = register("Analytics User", "analytics@example.com")
    outsider = register("Other User", "other@example.com")
    create_application(owner, {"company": "Alpha", "status": "interview", "match_score": 80, "deadline": (date.today() + timedelta(days=4)).isoformat()})
    create_application(owner, {"company": "Beta", "status": "offer", "match_score": 90})
    create_application(outsider, {"company": "Private", "status": "rejected", "match_score": 10})

    response = client.get("/api/analytics", headers=owner)
    assert response.status_code == 200
    analytics = response.json()
    assert analytics["total"] == 2
    assert analytics["active"] == 1
    assert analytics["interview_rate"] == 100
    assert analytics["offer_rate"] == 50
    assert analytics["average_match_score"] == 85
    assert analytics["status_counts"]["rejected"] == 0
    assert analytics["top_matches"][0]["company"] == "Beta"
    assert analytics["upcoming_deadlines"][0]["company"] == "Alpha"
    assert len(analytics["monthly_applications"]) == 6


def test_cross_application_assistant_uses_only_current_users_data(
    client: TestClient,
    register: Callable[[str, str], dict[str, str]],
    create_application: Callable[[dict[str, str], dict[str, object] | None], dict[str, object]],
) -> None:
    owner = register("Assistant User", "assistant@example.com")
    outsider = register("Other User", "other@example.com")
    own_application = create_application(owner, {"company": "Priority Labs", "status": "interview", "match_score": 88})
    private_application = create_application(outsider, {"company": "Secret Corp", "status": "interview", "match_score": 99})

    response = client.post("/api/assistant", headers=owner, json={"question": "Which applications should I prioritise?"})
    assert response.status_code == 200
    answer = response.json()
    assert answer["provider"] == "local"
    assert own_application["id"] in answer["related_application_ids"]
    assert private_application["id"] not in answer["related_application_ids"]
    assert "Priority Labs" in answer["answer"]
    assert "Secret Corp" not in answer["answer"]
    assert answer["recommended_actions"]

    follow_up = client.post(
        "/api/assistant",
        headers=owner,
        json={
            "question": "What should I do next?",
            "history": [
                {"role": "user", "content": "Help me prepare for my interview."},
                {"role": "assistant", "content": "Focus on Priority Labs first."},
            ],
        },
    )
    assert follow_up.status_code == 200


def test_assistant_rejects_oversized_conversation_history(
    client: TestClient,
    register: Callable[[str, str], dict[str, str]],
) -> None:
    headers = register("History User", "history@example.com")
    history = [{"role": "user", "content": f"Message {index}"} for index in range(11)]

    response = client.post(
        "/api/assistant",
        headers=headers,
        json={"question": "What should I do next?", "history": history},
    )

    assert response.status_code == 422


def test_profile_password_export_and_account_deletion(
    client: TestClient,
    register: Callable[[str, str], dict[str, str]],
    create_application: Callable[[dict[str, str], dict[str, object] | None], dict[str, object]],
) -> None:
    headers = register("Settings User", "settings@example.com")
    create_application(headers, {"company": "Export Ltd"})

    settings = client.get("/api/settings", headers=headers)
    assert settings.status_code == 200
    assert settings.json()["ai"]["configured"] is False
    assert "api_key" not in str(settings.json()).lower()

    profile = client.patch(
        "/api/settings/profile",
        headers=headers,
        json={"name": "Updated User", "email": "updated@example.com"},
    )
    assert profile.status_code == 200
    assert profile.json()["name"] == "Updated User"

    wrong_password = client.post(
        "/api/settings/password",
        headers=headers,
        json={"current_password": "incorrect", "new_password": "new-secure-password"},
    )
    assert wrong_password.status_code == 400
    changed = client.post(
        "/api/settings/password",
        headers=headers,
        json={"current_password": "securepass123", "new_password": "new-secure-password"},
    )
    assert changed.status_code == 204
    assert client.post("/api/auth/login", json={"email": "updated@example.com", "password": "securepass123"}).status_code == 401
    assert client.post("/api/auth/login", json={"email": "updated@example.com", "password": "new-secure-password"}).status_code == 200

    exported = client.get("/api/settings/export", headers=headers)
    assert exported.status_code == 200
    assert exported.json()["user"]["email"] == "updated@example.com"
    assert exported.json()["applications"][0]["company"] == "Export Ltd"

    assert client.request("DELETE", "/api/settings/account", headers=headers, json={"current_password": "incorrect"}).status_code == 400
    deleted = client.request("DELETE", "/api/settings/account", headers=headers, json={"current_password": "new-secure-password"})
    assert deleted.status_code == 204
    assert client.get("/api/auth/me", headers=headers).status_code == 401
