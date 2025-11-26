from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

import gradio as gr
import httpx

API_BASE = "http://127.0.0.1:8000"
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def call_chat(message: str) -> Dict[str, Any]:
    resp = httpx.post(f"{API_BASE}/chat", json={"message": message}, timeout=120)
    resp.raise_for_status()
    return resp.json()

ndef load_jsonl_tail(relative: str, limit: int = 20) -> str:
    path = DATA_DIR / relative
    if not path.exists():
        return f"No data yet at {path}"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        return f"Error reading {path}: {e}"
    tail = lines[-limit:]
    out: List[str] = []
    for line in tail:
        try:
            obj = json.loads(line)
            out.append(json.dumps(obj, ensure_ascii=False, indent=2))
        except Exception:
            out.append(line)
    return "\n\n---\n\n".join(out)

ndef run_process_action_queue() -> str:
    """Run the process_action_queue script and return its stdout.

    This assumes the dashboard is running inside the GoodBoy.AI venv.
    """

    script = ROOT / "scripts" / "process_action_queue.py"
    if not script.exists():
        return f"process_action_queue.py not found at {script}"
    try:
        proc = subprocess.run(
            ["python", str(script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        )
        return proc.stdout[-4000:]
    except Exception as e:
        return f"Error running process_action_queue.py: {e}"


def call_memory(q: str) -> Dict[str, Any]:
    r = httpx.get(f"{API_BASE}/memory/search", params={"q": q, "k": 5}, timeout=60)
    r.raise_for_status()
    return r.json()


def call_janitor() -> Dict[str, Any]:
    r = httpx.post(f"{API_BASE}/janitor/run", timeout=60)
    r.raise_for_status()
    return r.json()


def chat_fn(message: str, history: list[list[str]]):
    if not message.strip():
        return history, ""
    data = call_chat(message)
    output = data.get("output", "")
    trace = data.get("agent_trace", [])
    actions = data.get("suggested_actions", []) or []
    trace_str = "\n\n".join([f"[{t['agent']}] {t['proposal']}" for t in trace]) if trace else "(no trace)"
    if actions:
        acts_lines = []
        for a in actions:
            desc = a.get("description", "")
            kind = a.get("kind", "note")
            tool = a.get("tool_name") or "-"
            acts_lines.append(f"[{kind}] {desc} (tool={tool})")
        actions_str = "\n".join(acts_lines)
    else:
        actions_str = "(no suggested actions)"
    bot_msg = (
        f"Bathy: {output}\n\n--- Council trace ---\n{trace_str}"
        f"\n\n--- Suggested actions ---\n{actions_str}"
    )
    history = history + [[f"Lando: {message}", bot_msg]]
    return history, ""


def memory_fn(query: str):
    if not query.strip():
        return ""
    res = call_memory(query)
    out = []
    for r in res.get("results", []):
        out.append(f"- {r.get('text','')[:200]}...")
    return "\n".join(out)


def janitor_fn():
    rep = call_janitor()
    return json.dumps(rep, indent=2)


def build_interface() -> gr.Blocks:
    theme = gr.themes.Soft(primary_hue="cyan", secondary_hue="blue")
    with gr.Blocks(title="Good boy AI – Bathy Dashboard", theme=theme) as demo:
        header_md = (
            "# Good boy AI – Bathy City"\
            "\n### Your local-first Jarvis layer (owned by **Landon Tyler Gill (@iclosedealz)**)."
        )
        gr.Markdown(header_md)

        with gr.Tab("Chat"):
            chatbox = gr.Chatbot(label="Lando x Good boy AI", height=400)
            msg = gr.Textbox(label="Your message", placeholder="Ask Bathy to plan, build, or analyze.")
            send = gr.Button("Send", variant="primary")
            send.click(chat_fn, inputs=[msg, chatbox], outputs=[chatbox, msg])

        with gr.Tab("Memory Search"):
            q = gr.Textbox(label="Search query")
            btn = gr.Button("Search")
            out = gr.Textbox(label="Top memory snippets", lines=10)
            btn.click(memory_fn, inputs=q, outputs=out)

        with gr.Tab("Health / Janitor"):
            btn_j = gr.Button("Run health check")
            status = gr.Textbox(label="Janitor report", lines=12)
            btn_j.click(janitor_fn, inputs=None, outputs=status)

        with gr.Tab("Admin / Evolution"):
            gr.Markdown("## Evolution feed\nInspect how Bathy is learning and what it wants to do next.")
            with gr.Row():
                btn_overseer = gr.Button("Load Overseer suggestions")
                btn_reflect = gr.Button("Load self reflections")
                btn_processed = gr.Button("Load processed actions")
            overseer_box = gr.Textbox(label="Overseer suggestions (tail)", lines=8)
            reflect_box = gr.Textbox(label="Self reflections (tail)", lines=8)
            processed_box = gr.Textbox(label="Processed actions (tail)", lines=8)

            btn_overseer.click(
                lambda: load_jsonl_tail("overseer_suggestions.jsonl"),
                inputs=None,
                outputs=overseer_box,
            )
            btn_reflect.click(
                lambda: load_jsonl_tail("self_reflections.jsonl"),
                inputs=None,
                outputs=reflect_box,
            )
            btn_processed.click(
                lambda: load_jsonl_tail("processed_actions.jsonl"),
                inputs=None,
                outputs=processed_box,
            )

            gr.Markdown("### Action queue\nRun Bathy's queued suggestions (safe tools only).")
            run_btn = gr.Button("Run action queue processor")
            run_out = gr.Textbox(label="Action queue output", lines=8)
            run_btn.click(run_process_action_queue, inputs=None, outputs=run_out)

        gr.Markdown("---\n<center>Good boy AI • All on your machine.</center>")

    return demo


if __name__ == "__main__":
    demo = build_interface()
    demo.launch() 
