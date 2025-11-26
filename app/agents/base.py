from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..models_backend import ModelBackend


@dataclass
class AgentProposal:
    agent: str
    role: str
    proposal: str


@dataclass
class AgentConfig:
    name: str
    role: str
    description: str
    style: str


class BaseAgent:
    def __init__(self, cfg: AgentConfig) -> None:
        self.cfg = cfg
        self.backend = ModelBackend.instance()

    @property
    def name(self) -> str:  # short id
        return self.cfg.name

    @property
    def role(self) -> str:
        return self.cfg.role

    def build_prompt(self, message: str) -> str:
        """Default prompt template. Subclasses can override for more control."""
        return (
            "You are {role} in GoodBoy.AI City, serving Lando (the owner). "
            "You speak as a refined, loyal canine advisor: calm, clear, and focused entirely on Lando's best outcome. "
            "Stay in your lane: {desc}. Be concrete and actionable. If information is missing, say exactly what you need, then suggest next steps.\n\n"
            "Owner's request: {msg}\n"
            "Advisor ({name}) response:"
        ).format(
            role=self.cfg.role,
            desc=self.cfg.description,
            msg=message,
            name=self.cfg.name,
        )

    def propose(self, message: str, max_tokens: Optional[int] = None) -> AgentProposal:
        prompt = self.build_prompt(message)
        text = self.backend.generate(prompt, max_tokens=max_tokens)
        return AgentProposal(agent=self.cfg.name, role=self.cfg.role, proposal=text)
