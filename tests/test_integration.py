"""Integration tests for GoodBoy.AI council system."""
import pytest
from pathlib import Path

# Ensure test directories exist
Path("data").mkdir(exist_ok=True)
Path("memory").mkdir(exist_ok=True)
Path("models").mkdir(exist_ok=True)


class TestHealthCheck:
    """Test basic health endpoints."""
    
    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["app"] == "GoodBoy.AI"
        assert len(data["agents"]) == 6

    def test_agents_endpoint(self, client):
        r = client.get("/agents")
        assert r.status_code == 200
        data = r.json()
        assert len(data["agents"]) == 6
        agent_names = {a["name"] for a in data["agents"]}
        expected = {"Batman", "Alfred", "Jarvis", "DaVinci", "Architect", "Analyst"}
        assert agent_names == expected


class TestChat:
    """Test chat functionality."""
    
    def test_chat_basic(self, client):
        r = client.post("/chat", json={"message": "Hello GoodBoy"})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data["output"], str)
        assert len(data["output"]) > 0
        assert "route_metadata" in data

    def test_chat_empty_message(self, client):
        r = client.post("/chat", json={"message": ""})
        assert r.status_code == 400

    def test_chat_modes(self, client):
        for mode in ["auto", "reflex", "council", "strategic"]:
            r = client.post("/chat", json={"message": "Test", "mode": mode})
            assert r.status_code == 200
            data = r.json()
            assert data["route_metadata"]["mode"] == mode


class TestEvolution:
    """Test evolution system."""
    
    def test_evolution_status(self, client):
        r = client.get("/evolution/status")
        assert r.status_code == 200
        data = r.json()
        assert "generation" in data
        assert "total_interactions" in data
        assert "agent_proficiency" in data

    def test_evolution_generate(self, client):
        r = client.post("/evolution/generate")
        assert r.status_code == 200
        data = r.json()
        assert "generation_info" in data


class TestJanitor:
    """Test janitor/health system."""
    
    def test_janitor_run(self, client):
        r = client.post("/janitor/run")
        assert r.status_code == 200
        data = r.json()
        assert "timestamp" in data
        assert "evolution_status" in data
        assert "agents_healthy" in data


class TestMemory:
    """Test memory system."""
    
    def test_memory_search(self, client):
        # First add some data via chat
        client.post("/chat", json={"message": "Remember this test message"})
        
        r = client.get("/memory/search", params={"q": "test", "k": 5})
        assert r.status_code == 200
        data = r.json()
        assert "results" in data


class TestTeachings:
    """Test teachings system."""
    
    def test_add_teaching(self, client):
        r = client.post("/teachings/add", json={
            "topic": "test-topic",
            "instruction": "This is a test instruction",
            "tags": ["test", "integration"]
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "added"

    def test_search_teachings(self, client):
        # Add a teaching first
        client.post("/teachings/add", json={
            "topic": "search-test",
            "instruction": "Searchable instruction",
            "tags": ["searchable"]
        })
        
        r = client.get("/teachings/search", params={"q": "searchable", "k": 5})
        assert r.status_code == 200


class TestMinibots:
    """Test minibot system."""
    
    def test_list_minibots(self, client):
        r = client.get("/minibots/list")
        assert r.status_code == 200
        data = r.json()
        assert "minibots" in data
        assert "count" in data


# Pytest fixtures
@pytest.fixture
def client():
    """Create test client."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)
