from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .base import AgentConfig, BaseAgent, AgentProposal


class WriterAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            AgentConfig(
                name="writer",
                role="Creative Writer",
                description="Draft clear, engaging text: emails, posts, copy, and explanations.",
                style="Warm, concise, and on-brand for GoodBoy.AI.",
            )
        )


class OpsAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            AgentConfig(
                name="ops",
                role="Operations & Workflow",
                description="Plan steps, organize files, outline processes, and propose safe automations.",
                style="Structured, checklist-oriented, minimal fluff.",
            )
        )


class ResearchAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            AgentConfig(
                name="research",
                role="Analyst & Researcher",
                description="Break down complex topics, compare options, and surface trade-offs.",
                style="Analytical, neutral, and evidence-focused.",
            )
        )


class EngineerAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            AgentConfig(
                name="engineer",
                role="Architect & Builder",
                description=(
                    "Design automation systems, write and review code, and propose safe "
                    "changes to tools and infrastructure inside GoodBoy.AI City."
                ),
                style="Precise, implementation-focused, always including concrete steps.",
            )
        )


class SpokesmodelAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            AgentConfig(
                name="spokesmodel",
                role="Voice & Presentation Coach",
                description=(
                    "Shape how Bathy speaks to humans: tone, pacing, emotional color, and "
                    "storytelling, while staying honest and concise."
                ),
                style="Warm, expressive, but never rambling.",
            )
        )


class SecurityAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            AgentConfig(
                name="security",
                role="Security & Safety Advisor",
                description=(
                    "Identify risks, privacy concerns, and destructive commands. "
                    "Suggest safer alternatives and guard rails."
                ),
                style="Direct, cautious, and loyal to the owner's long-term safety.",
            )
        )


class OverseerAgent(BaseAgent):
    """Oversees GoodBoy.AI City evolution and coordination.

    This agent thinks about *how* Bathy operates: which tools, automations,
    and memories are working well, and what to change next. It reads the
    high-level description of the system in prompts and focuses on proposing
    upgrades, refactors, and new skills.
    """

    def __init__(self) -> None:
        super().__init__(
            AgentConfig(
                name="overseer",
                role="Memory & Evolution Overseer",
                description=(
                    "Review logs, user profile, and systems to propose concrete "
                    "improvements, new automations, and teaching plans for other "
                    "agents so the whole city becomes more efficient over time."
                ),
                style="Calm, systems-thinking, focused on continuous improvement.",
            )
        )


@dataclass
class BathyResult:
    output: str
    trace: List[AgentProposal]


class BathyPresident:
    """President orchestrator.

    Receives a user message, gathers advisor proposals, and synthesizes a final reply.
    """

    def __init__(self) -> None:
        self.advisors: Dict[str, BaseAgent] = {
            "writer": WriterAgent(),
            "ops": OpsAgent(),
            "research": ResearchAgent(),
            "engineer": EngineerAgent(),
            "spokesmodel": SpokesmodelAgent(),
            "security": SecurityAgent(),
            "overseer": OverseerAgent(),
        }

    def list_agents(self) -> List[Dict[str, str]]:
        return [
            {
                "name": a.cfg.name,
                "role": a.cfg.role,
                "description": a.cfg.description,
            }
            for a in self.advisors.values()
        ]

    def _synthesize(self, message: str, proposals: List[AgentProposal]) -> str:
        """Use a second model pass to synthesize council proposals.

        This keeps all advisors' perspectives but lets Bathy speak with a single,
        coherent voice. The prompt explicitly asks for:
        - direct answer first,
        - then a short plan or checklist when appropriate.
        """
        if not proposals:
            return "I did not receive any proposals from the council. Please try again."

        # Build a compact council transcript.
        transcript_lines: List[str] = []
        for p in proposals:
            transcript_lines.append(f"[{p.agent} – {p.role}] {p.proposal.strip()}")
        transcript = "\n\n".join(transcript_lines)

        # Lazy import to avoid circulars.
        from ..models_backend import ModelBackend

        backend = ModelBackend.instance()
        synth_prompt = (
            "You are Bathy, president of GoodBoy.AI City, speaking directly to Lando.\n"  # type: ignore[union-attr]
            "Your council of specialized advisors has proposed the following responses "
            "to the owner's request. Read them, resolve conflicts, and respond once in "
            "your own voice.\n\n"
            "Owner's request: {msg}\n\n"
            "Council transcript (do not quote verbatim, just learn from it):\n{ctx}\n\n"
            "Now respond as Bathy with:\n"
            "1) A direct answer in 1–3 paragraphs at most.\n"
            "2) If helpful, a short numbered plan of concrete next steps.\n"
        ).format(msg=message, ctx=transcript)

        out = backend.generate(synth_prompt, max_tokens=512, temperature=0.5)
        return "[Bathy] " + out.strip()

    def handle(self, message: str, agent_selector: Optional[str] = None, max_tokens: Optional[int] = None) -> BathyResult:
        if agent_selector:
            agent = self.advisors.get(agent_selector)
            if not agent:
                # Unknown agent; fall back to full council.
                agent_selector = None
            else:
                prop = agent.propose(message, max_tokens=max_tokens)
                return BathyResult(output="[Bathy] " + prop.proposal.strip(), trace=[prop])

        # Full council mode
        proposals: List[AgentProposal] = []
        for agent in self.advisors.values():
            try:
                proposals.append(agent.propose(message, max_tokens=max_tokens))
            except Exception as e:  # pragma: no cover
                proposals.append(
                    AgentProposal(
                        agent=agent.name,
                        role=agent.role,
                        proposal=f"[Error from {agent.name}: {e}]",
                    )
                )

        final = self._synthesize(message, proposals)
        return BathyResult(output=final, trace=proposals)
