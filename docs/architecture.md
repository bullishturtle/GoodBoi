# GoodBoy.AI City – Bathy Council Architecture

## High-level Concept

GoodBoy.AI is Lando's personal AI system, designed as a tiny autonomous city inside the machine.

- **Bathy** – president/mayor of the city, a refined butler-dog persona.
- **Council of advisors** – writer, ops, research, security (first wave), later more.
- **Districts** – chat, tools, memory, security, and construction (code evolution).

The tone and vibe are inspired by a classy, pampered dog butler: loyal, calm, and
laser-focused on Lando's goals. Underneath, it's a single unified AI (one brain) that
thinks like multiple specialized advisors, making it sharper and more reliable than any
single-prompt approach.

## Components

### 1. Models & Config

- Local GGUF models in `models/`:
  - Qwen2.5-7B-Instruct (main Bathy brain, sharded GGUF).
  - TinyLlama 1.1B (fallback/fast testing brain as `goodboy_small.gguf`).
- `data/GoodBoy_config.json` selects the active model and safety mode.

A shared `app/config.py` reads this config so both API and desktop UI can be
aligned.

### 2. Model Backend

- `app/models_backend.py` wraps GPT4All to load the chosen GGUF model.
- All agents call through this backend, so swapping models is centralized.

### 3. Bathy President & Advisors

- Package: `app/agents/`
  - `base.py` – base class and dataclasses for agent configs and proposals.
  - `president.py` – defines:
    - `WriterAgent` – creative/communication.
    - `OpsAgent` – planning, workflows, file/task organization.
    - `ResearchAgent` – analysis and comparisons.
    - `SecurityAgent` – risk and safety awareness.
    - `BathyPresident` – orchestrator that:
      - Holds the advisor registry.
      - For each user message, gathers proposals from advisors.
      - Synthesizes a final answer in Bathy's voice.

Bathy currently uses a simple heuristic (writer+ops blend or longest proposal),
with a clear path to upgrade into a second model pass for smarter synthesis.

### 4. FastAPI Bathy Core

- `app/main.py` exposes:
  - `GET /` – health, engine, model path, safety mode, and agent list.
  - `GET /agents` – lists advisor agents (name, role, description).
  - `POST /chat` – routes a message through Bathy:
    - Optional `agent_selector` to talk to a single advisor.
    - By default, Bathy runs the full council and returns:
      - `output` – Bathy's final message.
      - `used_model` – path to the GGUF file in use.
      - `agent_trace` – list of each advisor's proposal (agent, role, proposal).

This matches the blueprint of a multi-agent council where the mayor makes the
final call but the owner can still inspect what each advisor said.

### 5. Desktop Console (GoodBoy.AI City – Bathy Council)

- `GoodBoy_ui.py` provides a Tkinter-based desktop app that:
  - Uses the same `data/GoodBoy_config.json` and paths as the server.
  - Ingests documents into a simple local memory (`memory/chunks.jsonl`).
  - Allows "President + Cabinet" multi-answer mode using prompt variants.
  - Is themed with a dark navy + neon blue Jarvis style.
  - Supports branding assets from `assets/`:
    - `goodboy_icon.ico` – window icon.
    - `goodboy_logo.png` – header logo.

The console text and visual theme are aligned with the idea of Bathy as a
classy butler-dog running a high-tech control room.

### 6. Tests

- `tests/test_chat_basic.py` verifies:
  - `/` responds and includes an agent list.
  - `/agents` lists the writer agent at minimum.
  - `/chat` returns non-empty output and at least one agent trace item.

This ensures the Bathy council path stays wired correctly as the system grows.

## Next Layers to Build

To fully reach the original blueprint, the following layers are planned next:

1. **Tools + Clerk** – safe wrappers for file operations, commands, browser,
   and email, with ACL + consent and an action log.
2. **Memory 2.0** – embeddings-based memory (Chroma/FAISS) with `/memory/search`
   and ingestion of historical chats/docs.
3. **Janitor agent** – health checks, config validation, and recovery guidance.
4. **Web UI** – Jarvis-style dashboard with chat pane, agent trace, action
   queue, consent panel, and system health cards.
5. **Audit and autonomy flows** – safety modes, consent tokens, and reversible
   operations with `/audit` endpoints.

This document will be expanded as those layers are implemented.