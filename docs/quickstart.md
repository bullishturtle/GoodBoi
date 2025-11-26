# GoodBoy.AI Quickstart

Welcome to **GoodBoy.AI City – Bathy**, your local-first Jarvis-style assistant.
Everything runs on your machine using local models; no external AI services are
required.

---

## 1. First-time setup (Windows)

1. Open **PowerShell**.
2. Go to the project folder:
   ```powershell
   cd C:\GoodBoy.AI
   ```
3. Run the setup script (this creates a virtualenv, installs packages, and runs tests):
   ```powershell
   .\setup.ps1
   ```

If you want to skip tests during setup:

```powershell
.\setup.ps1 -SkipTests
```

---

## 2. Launch the desktop app (Bathy Council Console)

After setup, you can launch the desktop UI:

1. In File Explorer, open `C:\GoodBoy.AI`.
2. Double-click **`GoodBoy_launcher.bat`**.
3. The window titled **"GoodBoy.AI City – Bathy Council Console"** will appear.

From here you can:

- Type messages at the bottom and press **Enter** or click **Send**.
- Click **+ Upload** to ingest files (PDF, DOCX, JSON, TXT, MD) into memory.
- Toggle **President + Cabinet** to let multiple advisor personas weigh in.
- Click **Save Chat** to save the current conversation into `data/chats_content.json`.

When you close the window, Bathy may ask:

> "Anything I could do better next time?"

This feedback is optional but helps it adapt to your preferences over time.

---

## 3. Launch the API server and web dashboard

If you prefer a browser-based interface:

1. Start the API server:
   ```bat
   run_server.bat
   ```
2. In another terminal or by double-clicking:
   ```bat
   run_dashboard.bat
   ```
3. A Gradio dashboard will open in your browser with tabs for:
   - **Chat** – talk to Bathy and see council traces + suggested actions.
   - **Memory Search** – search long-term memory.
   - **Health / Janitor** – run a quick system health check.
   - **Admin / Evolution** – inspect Overseer suggestions, self-reflections, and processed actions, and run the action queue processor.

---

## 4. Teaching Bathy explicitly

You can teach Bathy new preferences or domain knowledge.

### 4.1 Via HTTP `/teach`

Send a POST request to `http://127.0.0.1:8000/teach` with JSON like:

```json
{
  "topic": "How I like my business plans",
  "instruction": "Always include market risks, cash runway, and top 3 experiments.",
  "tags": ["business", "preferences"]
}
```

Lessons are stored in `data/teachings.jsonl` and added to vector memory.

### 4.2 Via desktop exit feedback

When closing the desktop app and prompted,
write a short sentence about what GoodBoy.AI could do better next time.
This is stored as a teaching under the hood.

---

## 5. Letting Bathy reflect and evolve

Over time you can run helper scripts (from PowerShell in the project root):

```powershell
# Ask the Engineer agent to reflect on recent activity
venv\Scripts\python scripts\self_reflect.py

# Ask the Overseer agent for system-wide improvement ideas
venv\Scripts\python scripts\overseer_review.py

# Process Bathy's queued suggestions (safe tools, notes, automation ideas)
venv\Scripts\python scripts\process_action_queue.py
```

These scripts write to `data/self_reflections.jsonl`,
`data/overseer_suggestions.jsonl`, and `data/processed_actions.jsonl`, which
are visible from the **Admin / Evolution** tab in the dashboard.

---

## 6. Safety and autonomy

Key safety controls live in `data/GoodBoy_config.json`:

- `"safety_mode"` – one of:
  - `"read-only"` – tools that change files are blocked.
  - `"interactive"` – destructive tools require explicit consent tokens.
  - `"autonomous"` – destructive tools can run, but only when an
    `autonomy_token.txt` file exists in the `data/` folder.
- `"allowed_tools"` – list of tool names Bathy is allowed to use.
- `"automation.auto_apply_actions_for_safe_tools"` (from defaults in code) –
  when enabled, the action queue processor may auto-run safe tools that Bathy
  suggests.

You remain in full control: nothing runs outside these rules, and everything is
logged under the `logs/` folder.

---

## 7. Resetting local learning (optional)

If you want to clear local learning artifacts and start fresh, you can use the
factory reset script (see `scripts/factory_reset.py` after it is created) which
archives teaching and reflection logs into a timestamped folder.

---

You are now ready to explore GoodBoy.AI City. Start small (questions, file
summaries), then gradually let Bathy propose and execute automations as you
become comfortable with its behavior.