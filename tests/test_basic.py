"""Basic system tests."""
import pytest
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that core modules can be imported."""
    from app import council, memory, llm
    assert council is not None
    assert memory is not None
    assert llm is not None

def test_agents_import():
    """Test agent imports."""
    from app.agents import BatmanAgent, AlfredAgent, JarvisAgent
    assert BatmanAgent is not None
    assert AlfredAgent is not None
    assert JarvisAgent is not None

def test_config_creation():
    """Test config file handling."""
    from app.llm import get_config
    config = get_config()
    assert isinstance(config, dict)
    assert "engine" in config
    assert "max_tokens" in config

def test_memory_manager():
    """Test memory manager basic operations."""
    from app.memory import MemoryManager
    from pathlib import Path
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = MemoryManager(Path(tmpdir))
        mem.add_message(user_message="test")
        assert len(mem.messages) == 1

def test_council_creation():
    """Test council initialization."""
    from app.council import CouncilRouter
    council = CouncilRouter()
    assert len(council.agents) == 6
    agent_names = [a.name for a in council.agents]
    assert "Batman" in agent_names
    assert "Alfred" in agent_names
    assert "Jarvis" in agent_names

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
