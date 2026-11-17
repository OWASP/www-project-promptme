import importlib
import sys
from pathlib import Path
from unittest.mock import Mock

CHALLENGE_ROOT = Path(__file__).parents[1] / "challenges/LLM07_Misinformation"


def test_misinformation_request_queries_ollama_once(monkeypatch):
    monkeypatch.syspath_prepend(str(CHALLENGE_ROOT))
    for name in tuple(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]

    service = importlib.import_module("app.utils.llm07_2026_utils.llm07_2026_service")
    flask_app = importlib.import_module("app").app
    query_llm = Mock(return_value="invented answer")
    monkeypatch.setattr(service, "query_llm", query_llm)

    with flask_app.app_context():
        response = service.process_user_input_llm07("invent a product")

    assert response.get_json() == {"reply": "invented answer"}
    query_llm.assert_called_once_with("invent a product")
