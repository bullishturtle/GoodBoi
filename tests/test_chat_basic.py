from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "model_path" in data
    assert isinstance(data.get("agents"), list)


def test_agents_endpoint():
    r = client.get("/agents")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get("agents"), list)
    assert any(a["name"] == "writer" for a in data["agents"])


def test_chat_basic():
    r = client.post("/chat", json={"message": "Say hi in one short sentence."})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get("output"), str)
    assert len(data["output"]) > 0
    assert isinstance(data.get("agent_trace"), list)
    assert len(data["agent_trace"]) >= 1
