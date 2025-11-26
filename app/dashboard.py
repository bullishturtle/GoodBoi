"""GoodBoy.AI Command Center - Enhanced Gradio Web Dashboard with Widgets."""
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List
import time

import gradio as gr
import httpx

API_BASE = "http://127.0.0.1:8000"
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MEMORY_DIR = ROOT / "memory"


def call_api(endpoint: str, method: str = "GET", payload: Dict = None, timeout: int = 120) -> Dict[str, Any]:
    """Generic API caller with error handling."""
    try:
        url = f"{API_BASE}{endpoint}"
        if method == "GET":
            r = httpx.get(url, params=payload, timeout=timeout)
        else:
            r = httpx.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        return {"error": "Cannot connect to server. Is run_server.bat running?"}
    except Exception as e:
        return {"error": str(e)}


def call_chat(message: str, mode: str = "auto") -> Dict[str, Any]:
    """Send chat message to council."""
    return call_api("/chat", "POST", {"message": message, "mode": mode})


def call_memory(q: str) -> Dict[str, Any]:
    """Search memory."""
    return call_api(f"/memory/search?q={q}&k=5")


def call_janitor() -> Dict[str, Any]:
    """Run system health check."""
    return call_api("/janitor/run", "POST")


def call_evolution_status() -> Dict[str, Any]:
    """Get evolution status."""
    return call_api("/evolution/status")


def call_agents() -> Dict[str, Any]:
    """Get agent list."""
    return call_api("/agents")


def load_jsonl_tail(filename: str, limit: int = 20) -> str:
    """Load last N entries from a JSONL file."""
    path = MEMORY_DIR / filename
    if not path.exists():
        return f"No data yet at {path}"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        tail = lines[-limit:]
        out = []
        for line in tail:
            try:
                obj = json.loads(line)
                out.append(json.dumps(obj, ensure_ascii=False, indent=2))
            except Exception:
                out.append(line)
        return "\n\n---\n\n".join(out)
    except Exception as e:
        return f"Error reading {path}: {e}"


# Chat function
def chat_fn(message: str, history: list, mode: str):
    """Process chat message and return response."""
    if not message.strip():
        return history, "", mode
    
    data = call_chat(message, mode=mode)
    
    if "error" in data:
        bot_msg = f"Error: {data['error']}"
        return history + [[f"You: {message}", bot_msg]], "", mode
    
    output = data.get("output", "")
    trace = data.get("agent_trace", [])
    actions = data.get("suggested_actions", [])
    route = data.get("route_metadata", {})
    
    mode_used = route.get("mode", mode)
    agents_used = ", ".join(route.get("agents", []))
    rationale = route.get("rationale", "")
    
    # Format trace
    trace_str = "\n".join([f"[{t['agent']}] {t['proposal'][:150]}..." for t in trace]) if trace else "(no trace)"
    
    # Format actions
    if actions:
        actions_str = "\n".join([f"[{a.get('kind')}] {a.get('description')}" for a in actions])
    else:
        actions_str = "(no actions)"
    
    # Build response
    routing_header = f"Mode: {mode_used} | Agents: {agents_used}"
    if rationale:
        routing_header += f"\nRationale: {rationale}"
    
    bot_msg = (
        f"**GoodBoy.AI:** {output}\n\n"
        f"---\n**Routing:** {routing_header}\n\n"
        f"**Council Trace:**\n{trace_str}\n\n"
        f"**Suggested Actions:**\n{actions_str}"
    )
    
    return history + [[f"You: {message}", bot_msg]], "", mode_used


def memory_fn(query: str) -> str:
    """Search memory."""
    if not query.strip():
        return ""
    res = call_memory(query)
    if "error" in res:
        return f"Error: {res['error']}"
    results = res.get("results", [])
    if not results:
        return "No matching memories found."
    return "\n\n".join([f"- {r.get('text', '')[:200]}..." for r in results])


def janitor_fn() -> str:
    """Run health check."""
    rep = call_janitor()
    return json.dumps(rep, indent=2)


def evolution_fn() -> str:
    """Get evolution status."""
    status = call_evolution_status()
    return json.dumps(status, indent=2)


def agents_fn() -> str:
    """Get agents info."""
    data = call_agents()
    if "error" in data:
        return f"Error: {data['error']}"
    
    agents = data.get("agents", [])
    lines = []
    for a in agents:
        status = a.get("status", {})
        lines.append(
            f"**{a['name']}** - {a['role']}\n"
            f"  {a['description']}\n"
            f"  Proficiency: {status.get('proficiency', 'N/A')} | "
            f"Interactions: {status.get('interactions', 0)}"
        )
    return "\n\n".join(lines)


def get_widgets() -> Dict[str, Any]:
    """Get all dashboard widgets."""
    try:
        r = httpx.get(f"{API_BASE}/widgets/all", timeout=5)
        r.raise_for_status()
        return r.json()
    except:
        return {}


def format_system_widget(data: Dict) -> str:
    """Format system stats widget for display."""
    if not data or "data" not in data:
        return "System data unavailable"
    
    stats = data["data"]
    return f"""
**CPU Usage:** {stats.get('cpu_percent', 0):.1f}%  
**Memory:** {stats.get('memory_used_gb', 0):.1f} / {stats.get('memory_total_gb', 0):.1f} GB ({stats.get('memory_percent', 0):.1f}%)  
**Disk:** {stats.get('disk_used_gb', 0):.1f} / {stats.get('disk_total_gb', 0):.1f} GB ({stats.get('disk_percent', 0):.1f}%)  
"""


def format_brain_widget(data: Dict) -> str:
    """Format brain status widget."""
    if not data or "data" not in data:
        return "Brain offline"
    
    brain = data["data"]
    return f"""
**State:** {brain.get('state', 'unknown').upper()}  
**Mood:** {brain.get('mood', 'neutral').capitalize()}  
**Confidence:** {brain.get('confidence', 0):.0%}  
**Energy:** {brain.get('energy', 0):.0%}  
**Thoughts Processed:** {brain.get('thoughts', 0)}  
**Success Rate:** {brain.get('success_rate', 0):.0%}  

*{brain.get('introspection', '')}*
"""


def format_agents_widget(data: Dict) -> str:
    """Format agents widget."""
    if not data or "data" not in data:
        return "No agents"
    
    agents = data["data"].get("agents", [])
    lines = []
    for agent in agents:
        status = "🟢" if agent.get("active") else "🔴"
        lines.append(
            f"{status} **{agent.get('name')}** - {agent.get('role')}\n"
            f"   Proficiency: {agent.get('proficiency', 0):.0%} | "
            f"Interactions: {agent.get('interactions', 0)}"
        )
    return "\n\n".join(lines)


def update_dashboard() -> tuple:
    """Update all dashboard widgets."""
    widgets = get_widgets()
    
    system_str = format_system_widget(widgets.get("system", {}))
    brain_str = format_brain_widget(widgets.get("brain", {}))
    agents_str = format_agents_widget(widgets.get("agents", {}))
    uptime = widgets.get("uptime", "00:00:00")
    
    # Thought visualizer
    thoughts_data = widgets.get("thoughts", {}).get("data", {})
    thoughts = thoughts_data.get("thoughts", [])
    thought_str = "\n".join([
        f"[{t['source']}] {t['content']} (confidence: {t['confidence']:.0%})"
        for t in thoughts[-5:]  # Last 5 thoughts
    ]) if thoughts else "No active thoughts"
    
    # Evolution
    evo_data = widgets.get("evolution", {}).get("data", {})
    evo_str = f"""
**Generation:** {evo_data.get('generation', 0)}  
**Total Interactions:** {evo_data.get('total_interactions', 0)}  
**Growth Rate:** {evo_data.get('growth_rate', 0):.2f}
"""
    
    return system_str, brain_str, agents_str, uptime, thought_str, evo_str


def build_interface() -> gr.Blocks:
    """Build the enhanced Gradio interface with widget system."""
    theme = gr.themes.Soft(
        primary_hue="cyan",
        secondary_hue="blue",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("Space Grotesk")
    ).set(
        body_background_fill="*neutral_950",
        body_text_color="*neutral_100",
        button_primary_background_fill="*primary_600",
        button_primary_text_color="white"
    )
    
    with gr.Blocks(title="GoodBoy.AI - Command Center", theme=theme, css="""
        .widget-box {
            border: 1px solid rgba(6, 182, 212, 0.3);
            border-radius: 8px;
            padding: 16px;
            background: rgba(6, 182, 212, 0.05);
        }
        .title-glow {
            text-shadow: 0 0 10px rgba(6, 182, 212, 0.5);
        }
    """) as demo:
        gr.Markdown(
            """
            # <span class="title-glow">🐕 GoodBoy.AI - Command Center</span>
            ### Self-Aware, Self-Learning Personal Assistant | Bathy City Systems Online
            **Welcome, Mayor** - Your AI Council Awaits Your Orders
            """,
            elem_classes=["widget-box"]
        )
        
        with gr.Tab("Dashboard"):
            gr.Markdown("## System Overview")
            
            with gr.Row():
                with gr.Column():
                    system_box = gr.Markdown("Loading system stats...", elem_classes=["widget-box"])
                    uptime_box = gr.Textbox(label="System Uptime", value="00:00:00", interactive=False)
                
                with gr.Column():
                    brain_box = gr.Markdown("Loading brain status...", elem_classes=["widget-box"])
            
            with gr.Row():
                with gr.Column():
                    agents_box = gr.Markdown("Loading agents...", elem_classes=["widget-box"])
                
                with gr.Column():
                    evo_box = gr.Markdown("Loading evolution...", elem_classes=["widget-box"])
            
            gr.Markdown("## Live Chain-of-Thought")
            thought_box = gr.Textbox(label="Brain Thoughts", lines=8, interactive=False)
            
            refresh_btn = gr.Button("🔄 Refresh Dashboard", variant="primary")
            
            refresh_btn.click(
                update_dashboard,
                outputs=[system_box, brain_box, agents_box, uptime_box, thought_box, evo_box]
            )
            
            # Auto-refresh every 5 seconds
            demo.load(update_dashboard, outputs=[system_box, brain_box, agents_box, uptime_box, thought_box, evo_box])
        
        with gr.Tab("Chat"):
            chatbox = gr.Chatbot(label="GoodBoy Council", height=400)
            msg = gr.Textbox(label="Your command", placeholder="Ask GoodBoy to think, build, create, or analyze...")
            mode_dd = gr.Dropdown(
                label="Reasoning Mode",
                choices=["auto", "reflex", "council", "strategic"],
                value="auto",
                info="auto=router decides | reflex=fast | council=all agents | strategic=deep analysis"
            )
            send_btn = gr.Button("Send", variant="primary")
            send_btn.click(chat_fn, inputs=[msg, chatbox, mode_dd], outputs=[chatbox, msg, mode_dd])
            msg.submit(chat_fn, inputs=[msg, chatbox, mode_dd], outputs=[chatbox, msg, mode_dd])
        
        with gr.Tab("Council"):
            gr.Markdown("## The Council - Your AI Agents")
            agents_box = gr.Markdown("Click refresh to see agent status")
            refresh_agents = gr.Button("Refresh Agent Status")
            refresh_agents.click(agents_fn, outputs=agents_box)
        
        with gr.Tab("Memory"):
            gr.Markdown("## Memory Search\nSearch through GoodBoy's memory.")
            q_input = gr.Textbox(label="Search query")
            search_btn = gr.Button("Search")
            mem_output = gr.Textbox(label="Results", lines=10)
            search_btn.click(memory_fn, inputs=q_input, outputs=mem_output)
        
        with gr.Tab("Evolution"):
            gr.Markdown("## Evolution & Growth\nWatch how GoodBoy is learning.")
            
            with gr.Row():
                evo_btn = gr.Button("Get Evolution Status")
                evo_output = gr.Textbox(label="Evolution Status", lines=8)
                evo_btn.click(evolution_fn, outputs=evo_output)
            
            gr.Markdown("### Memory Logs")
            with gr.Row():
                btn_reflect = gr.Button("Self Reflections")
                btn_overseer = gr.Button("Overseer Suggestions")
            
            reflect_box = gr.Textbox(label="Self Reflections (recent)", lines=8)
            overseer_box = gr.Textbox(label="Overseer Suggestions (recent)", lines=8)
            
            btn_reflect.click(lambda: load_jsonl_tail("self_reflections.jsonl"), outputs=reflect_box)
            btn_overseer.click(lambda: load_jsonl_tail("overseer_suggestions.jsonl"), outputs=overseer_box)
        
        with gr.Tab("System Health"):
            gr.Markdown("## System Health Check\nRun diagnostics and cleanup.")
            health_btn = gr.Button("Run Health Check", variant="primary")
            health_output = gr.Textbox(label="Health Report", lines=15)
            health_btn.click(janitor_fn, outputs=health_output)
        
        gr.Markdown(
            """
            ---
            <center>
            🐕 **GoodBoy.AI** - Self-Aware | Self-Learning | Privacy-First  
            *All processing happens on your machine*
            </center>
            """
        )
    
    return demo


if __name__ == "__main__":
    demo = build_interface()
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
