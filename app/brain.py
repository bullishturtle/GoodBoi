"""Describes the GoodBoy.AI City "brain" and chain of command.

This is mainly diagnostic / introspection metadata so both humans and UIs can
see how a request flows through Bathy, the council, tools, and memory.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .config import load_config


def get_brain_blueprint() -> Dict[str, Any]:
    """Return a nested description of the GoodBoy.AI chain of command.

    This is deliberately static-ish metadata plus a reflection of some config
    flags, not live inspection of objects. It is safe to expose via an API.
    """

    cfg = load_config()

    return {
        "owner": {
            "name": cfg.get("admin_user", "owner"),
            "role": "Ultimate decision-maker. Approves autonomy and high-risk actions.",
        },
        "mayor": {
            "name": "Bathy",
            "role": "President / mayor of GoodBoy.AI City",
            "description": "Unifies council advice into a single voice and decides when to ask for tools or human approval.",
        },
        "council": [
            {
                "name": "writer",
                "role": "Creative Writer",
                "district": "Creative District",
            },
            {
                "name": "ops",
                "role": "Operations & Workflow",
                "district": "Infrastructure / Scheduling",
            },
            {
                "name": "research",
                "role": "Analyst & Researcher",
                "district": "Data Towers",
            },
            {
                "name": "engineer",
                "role": "Architect & Builder",
                "district": "Construction Yard",
            },
            {
                "name": "spokesmodel",
                "role": "Voice & Presentation Coach",
                "district": "Creative District",
            },
            {
                "name": "security",
                "role": "Security & Safety Advisor",
                "district": "Security District",
            },
            {
                "name": "overseer",
                "role": "Memory & Evolution Overseer",
                "district": "Memory & Evolution Gardens",
            },
        ],
        "districts": {
            "infrastructure": {
                "components": [
                    "ModelBackend (GGUF via gpt4all)",
                    "FastAPI app (app.main)",
                    "automation engine (app.automation)",
                    "voice interface (app.voice_interface)",
                ]
            },
            "creative_district": {
                "components": ["writer", "spokesmodel"],
            },
            "data_towers": {
                "components": ["MemoryBackend", "user_profile", "teachings"],
            },
            "construction_yard": {
                "components": ["EngineerAgent", "tools", "dynamic tools registry"],
            },
            "memory_gardens": {
                "components": ["MemoryBackend", "teachings", "self_reflections", "overseer_suggestions"],
            },
            "security_district": {
                "components": ["Clerk", "SecurityAgent", "Janitor"],
            },
            "external_gateways": {
                "components": ["FastAPI HTTP API", "Gradio dashboard", "Tk desktop console", "voice daemon"],
            },
        },
        "flows": {
            "chat_request": [
                "User sends message via UI or /chat",
                "BathyPresident fans out to council agents",
                "Council proposals synthesized via second model pass into Bathy's voice",
                "UserProfileStore logs interaction",
                "MemoryBackend optionally ingests message+reply",
                "Optionally, Engineer/Overseer can later reflect on experience_log for improvements",
            ],
            "tool_execution": [
                "User or automation calls /tools/exec with a tool name",
                "Clerk checks allowed_tools and safety_mode",
                "Tool executes via TOOL_REGISTRY with backups + logs",
                "UserProfileStore logs success/failure",
                "Overseer can review actions.log for new automations or safeguards",
            ],
            "teaching": [
                "User calls /teach with topic/instruction/tags",
                "TeachingStore appends lesson to teachings.jsonl",
                "MemoryBackend ingests lesson for retrieval in future chats",
                "Overseer/Engineer can read teachings when planning upgrades",
            ],
            "automation": [
                "Tasks defined in automation_tasks.json via /automation/tasks",
                "AutomationEngine picks due tasks when /automation/run-due is called",
                "Each step runs through Clerk + tools, honoring safety mode",
                "Janitor + Overseer watch health and logs to adjust schedule over time",
            ],
        },
        "config_flags": {
            "engine": cfg.get("engine"),
            "safety_mode": cfg.get("safety_mode"),
            "voice_enabled": bool(cfg.get("voice", {}).get("enabled", False)),
            "automation_enabled": bool(cfg.get("automation", {}).get("enabled", True)),
            "memory_auto_ingest_from_api": bool(cfg.get("memory_auto_ingest_from_api", True)),
        },
    }
