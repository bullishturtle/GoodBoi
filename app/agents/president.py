from openclaw import SelfEnhancer

class OverseerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            AgentConfig(
                name="overseer",
                role="Memory & Evolution Overseer",
                description="Proposes improvements and new automations.",
                style="Calm, systems-thinking, focused on continuous improvement."
            )
        )
        self.self_enhancer = SelfEnhancer()

    def propose_improvements(self):
        return self.self_enhancer.analyze_and_propose()