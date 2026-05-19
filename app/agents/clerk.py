from openclaw import ToolManager

class Clerk:
    def __init__(self):
        self.tool_manager = ToolManager()

    def execute(self, name: str, args: Dict[str, Any]) -> ClerkResult:
        if not self.tool_manager.is_tool_allowed(name):
            return ClerkResult(False, f"Tool '{name}' is not allowed.", ToolResult(name, False, "blocked", {}))

        result = self.tool_manager.run_tool(name, args)
        return ClerkResult(result.success, result.detail, result)