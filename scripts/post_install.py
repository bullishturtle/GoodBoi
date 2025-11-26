"""Post-installation setup script."""
import os
import json
from pathlib import Path

def setup_directories():
    """Create necessary directories."""
    dirs = [
        Path("data"),
        Path("memory"),
        Path("memory/docs"),
        Path("models"),
        Path("logs"),
        Path("assets"),
    ]
    
    for d in dirs:
        d.mkdir(exist_ok=True, parents=True)
        gitkeep = d / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()
    
    print("✓ Created directory structure")

def create_default_config():
    """Create default configuration files."""
    config_path = Path("data/GoodBoy_config.json")
    if not config_path.exists():
        config = {
            "engine": "cloud",
            "model_path": "models/",
            "cloud_api_base": "http://127.0.0.1:8000",
            "max_tokens": 512,
            "temperature": 0.6,
            "user_name": "Mayor",
            "theme": "dark",
            "auto_start_server": True,
            "api_port": 8000,
        }
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        print("✓ Created default configuration")

def create_default_behavior():
    """Create default behavior instructions."""
    behavior_path = Path("data/Behavior_instructions.json")
    if not behavior_path.exists():
        behavior = {
            "system_prompt": (
                "You are GoodBoy.AI: a loyal, efficient, self-learning AI assistant. "
                "You have a council of specialized agents that help you process requests. "
                "Be concise, helpful, and action-oriented. Learn from every interaction."
            ),
            "personality_traits": [
                "Loyal and dependable",
                "Efficient and practical",
                "Learns continuously",
                "Security-conscious",
                "Proactive problem solver"
            ],
            "response_guidelines": [
                "Answer directly without repeating the user's question",
                "Use uploaded context when available",
                "Suggest next steps when appropriate",
                "Admit when you don't know something",
                "Be concise but thorough"
            ]
        }
        with open(behavior_path, "w") as f:
            json.dump(behavior, f, indent=2)
        print("✓ Created default behavior instructions")

def create_empty_chats():
    """Create empty chats file."""
    chats_path = Path("data/chats_content.json")
    if not chats_path.exists():
        with open(chats_path, "w") as f:
            json.dump([], f)
        print("✓ Created empty chats file")

def main():
    """Run post-installation setup."""
    print("=" * 50)
    print("GoodBoy.AI Post-Installation Setup")
    print("=" * 50)
    print()
    
    setup_directories()
    create_default_config()
    create_default_behavior()
    create_empty_chats()
    
    print()
    print("=" * 50)
    print("Setup complete! GoodBoy.AI is ready to use.")
    print("=" * 50)
    print()
    print("Next steps:")
    print("1. Run GoodBoy.AI from your Start menu or desktop")
    print("2. Download an AI model in Settings > Model Manager")
    print("3. Start chatting!")
    print()

if __name__ == "__main__":
    main()
