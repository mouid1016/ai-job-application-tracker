from types import SimpleNamespace

import openai

from app.ai_service import StructuredAssistantResponse, openai_assistant_response


def test_openai_assistant_receives_recent_conversation(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponses:
        def parse(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                output_parsed=StructuredAssistantResponse(
                    answer="Focus on the interview application first.",
                    highlights=["One interview is active"],
                    recommended_actions=["Prepare two STAR examples"],
                    related_application_ids=[7, 999],
                )
            )

    class FakeClient:
        responses = FakeResponses()

    monkeypatch.setattr(openai, "OpenAI", lambda **_kwargs: FakeClient())

    result = openai_assistant_response(
        "What should I prepare?",
        [{"id": 7, "company": "Example Labs", "role": "Engineer", "status": "interview"}],
        ["Docker"],
        [
            {"role": "user", "content": "Which application matters most?"},
            {"role": "assistant", "content": "Example Labs is at interview stage."},
        ],
    )

    messages = captured["input"]
    assert messages[-3:] == [
        {"role": "user", "content": "Which application matters most?"},
        {"role": "assistant", "content": "Example Labs is at interview stage."},
        {"role": "user", "content": "What should I prepare?"},
    ]
    assert result.related_application_ids == [7]
