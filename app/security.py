"""Security layer for GoodBoy.AI."""
from typing import Optional, Dict, Any
import hashlib
from datetime import datetime

class SecurityManager:
    """Manages security, permissions, and action validation."""
    
    # Safe tools that can run without explicit confirmation
    SAFE_TOOLS = {
        "code_review", "memory_search", "suggest_refactor", 
        "format_code", "lint_check"
    }
    
    # Dangerous operations requiring approval
    DANGEROUS_OPERATIONS = {
        "delete_files", "system_command", "modify_core", 
        "export_data", "reset_state"
    }
    
    def __init__(self):
        self.audit_log = []
    
    def can_execute(self, tool_name: str, context: Optional[Dict] = None) -> bool:
        """Check if tool can be executed safely."""
        if tool_name in self.SAFE_TOOLS:
            self._log_action("execute", tool_name, "approved")
            return True
        
        if tool_name in self.DANGEROUS_OPERATIONS:
            self._log_action("execute", tool_name, "blocked")
            return False
        
        return True
    
    def _log_action(self, action: str, target: str, result: str):
        """Log security events."""
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "target": target,
            "result": result
        })

class ValidationManager:
    """Validates agent outputs and suggested actions."""
    
    def validate_action(self, action: Dict[str, Any]) -> bool:
        """Validate action before execution."""
        required_fields = {"kind", "description"}
        return all(field in action for field in required_fields)
    
    def validate_output(self, output: str, max_length: int = 10000) -> bool:
        """Validate agent output."""
        if not isinstance(output, str) or len(output) == 0:
            return False
        if len(output) > max_length:
            return False
        return True

class AuditLogger:
    """Comprehensive audit logging."""
    
    def __init__(self, log_file: str):
        self.log_file = log_file
    
    def log_interaction(self, message: str, agents: list, result: str):
        """Log interaction to audit trail."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "message_hash": hashlib.sha256(message.encode()).hexdigest()[:8],
            "agents": agents,
            "result_hash": hashlib.sha256(result.encode()).hexdigest()[:8]
        }
        return entry
