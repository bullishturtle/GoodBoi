"""GoodBoy.AI Desktop UI - Tkinter client that connects to Bathy API."""
import os
import json
import re
import threading
import time
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, ttk

import httpx

# Optional: Local model backend (GPT4All) for offline mode
try:
    from gpt4all import GPT4All
    HAS_GPT4ALL = True
except ImportError:
    HAS_GPT4ALL = False

# Teaching store for exit feedback
try:
    from app.teachings import get_store as get_teaching_store
except Exception:
    get_teaching_store = None

# Model manager
try:
    from app.model_manager import ModelManager, KNOWN_MODELS
    HAS_MODEL_MANAGER = True
except ImportError:
    HAS_MODEL_MANAGER = False
    KNOWN_MODELS = {}

# ---------- Paths ----------
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
MEM_DIR = ROOT / "memory"
DOCS_DIR = MEM_DIR / "docs"
CHUNKS_PATH = MEM_DIR / "chunks.jsonl"
BEHAVIOR_PATH = DATA_DIR / "Behavior_instructions.json"
CHATS_PATH = DATA_DIR / "chats_content.json"
CONFIG_PATH = DATA_DIR / "GoodBoy_config.json"
ASSETS_DIR = ROOT / "assets"
MODELS_DIR = ROOT / "models"
LOGS_DIR = ROOT / "logs"

# ---------- Visual Theme (Jarvis / GoodBoy.AI City) ----------
THEME_BG = "#050814"
THEME_PANEL = "#08101f"
THEME_ACCENT = "#32d4ff"
THEME_TEXT = "#e0f4ff"
THEME_SUCCESS = "#32ff7e"
THEME_WARNING = "#ffb832"
THEME_ERROR = "#ff5252"

# Create directories
for d in [DATA_DIR, MEM_DIR, DOCS_DIR, ASSETS_DIR, MODELS_DIR, LOGS_DIR]:
    d.mkdir(exist_ok=True)

if not CHATS_PATH.exists():
    CHATS_PATH.write_text("[]")


# ---------- Config & Behavior ----------
DEFAULT_SYSTEM = (
    "You are GoodBoy.AI: loyal, concise, and efficient. "
    "Use uploaded context first; do NOT repeat the user's words back. "
    "If info is missing, say what you need, then give next steps."
)


def load_json(path, default_obj):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        Path(path).write_text(json.dumps(default_obj, indent=2))
        return default_obj


def save_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2))


SYSTEM_PROMPT = load_json(BEHAVIOR_PATH, {"system_prompt": DEFAULT_SYSTEM}).get("system_prompt", DEFAULT_SYSTEM)
CONFIG = load_json(CONFIG_PATH, {
    "engine": "cloud",
    "model_path": "models/",
    "cloud_api_base": "http://127.0.0.1:8000",
    "max_tokens": 512,
    "temperature": 0.6,
    "user_name": "Mayor",
    "theme": "dark",
    "auto_start_server": True,
})


# ---------- Tiny RAG for offline mode ----------
STOP = set("a an the and or of to in is are was were be been being have has had do does did but not for on with as by at from that this these those it its you your me my we us our they them he she his her i am will would should could can about into over".split())


def tokenize(text):
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP]


def chunk_text(text, max_words=280, overlap=60):
    words = text.split()
    i = 0
    while i < len(words):
        yield " ".join(words[i:i + max_words])
        i += max_words - overlap if max_words > overlap else max_words


def read_txt(p): return Path(p).read_text(encoding="utf-8", errors="ignore")
def read_md(p): return read_txt(p)


def read_json_chatlike(p):
    try:
        obj = json.loads(read_txt(p))
        if isinstance(obj, list):
            out = []
            for it in obj:
                if isinstance(it, dict) and "user" in it:
                    ai = it.get("ai", it.get("assistant", ""))
                    out.append(f"User: {it['user']}\nAssistant: {ai}")
                else:
                    out.append(json.dumps(it, ensure_ascii=False))
            return "\n\n".join(out)
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except Exception:
        return read_txt(p)


def read_pdf(p):
    try:
        import pypdf
        r = pypdf.PdfReader(p)
        return "\n".join([pg.extract_text() or "" for pg in r.pages])
    except Exception as e:
        return f"[PDF read error: {e}]"


def read_docx(p):
    try:
        import docx
        d = docx.Document(p)
        return "\n".join([x.text for x in d.paragraphs])
    except Exception as e:
        return f"[DOCX read error: {e}]"


READERS = {".txt": read_txt, ".md": read_md, ".json": read_json_chatlike, ".pdf": read_pdf, ".docx": read_docx}


def add_chunks(source_path, text):
    made = 0
    with open(CHUNKS_PATH, "a", encoding="utf-8") as f:
        for idx, ch in enumerate(chunk_text(text)):
            f.write(json.dumps({"source": str(source_path), "idx": idx, "text": ch}, ensure_ascii=False) + "\n")
            made += 1
    return made


def load_chunks():
    if not CHUNKS_PATH.exists():
        return []
    out = []
    for line in CHUNKS_PATH.read_text().split("\n"):
        if line.strip():
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def retrieve(query, top_k=4):
    q = set(tokenize(query))
    chunks = load_chunks()
    scored = sorted(chunks, key=lambda r: len(q & set(tokenize(r["text"]))), reverse=True)
    return [c["text"] for c in scored[:top_k]]


# ---------- Server Management ----------
class ServerManager:
    """Manages the FastAPI backend server."""
    
    def __init__(self):
        self.process = None
        self.port = CONFIG.get("api_port", 8000)
    
    def is_running(self) -> bool:
        """Check if server is running."""
        try:
            r = httpx.get(f"http://127.0.0.1:{self.port}/health", timeout=2)
            return r.status_code == 200
        except Exception:
            return False
    
    def start(self) -> bool:
        """Start the backend server."""
        if self.is_running():
            return True
        
        try:
            # Try to start server
            server_script = ROOT / "run_server.bat"
            if server_script.exists():
                self.process = subprocess.Popen(
                    ["cmd", "/c", str(server_script)],
                    cwd=str(ROOT),
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )
            else:
                # Direct uvicorn start
                self.process = subprocess.Popen(
                    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(self.port)],
                    cwd=str(ROOT),
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )
            
            # Wait for server to start
            for _ in range(30):
                time.sleep(0.5)
                if self.is_running():
                    return True
            
            return False
            
        except Exception:
            return False
    
    def stop(self):
        """Stop the backend server."""
        if self.process:
            self.process.terminate()
            self.process = None


# ---------- Backends ----------
class LocalBackend:
    """Offline mode using local GGUF model."""
    
    def __init__(self):
        if not HAS_GPT4ALL:
            raise RuntimeError("gpt4all not installed. Run: pip install gpt4all")
        self.model = self._load()

    def _load(self):
        model_rel = CONFIG.get("model_path", "models/")
        model_path = Path(model_rel)
        
        if model_path.is_dir():
            # Find first .gguf file in directory
            gguf_files = list(model_path.glob("*.gguf"))
            if not gguf_files:
                gguf_files = list(MODELS_DIR.glob("*.gguf"))
            if gguf_files:
                model_path = gguf_files[0]
        
        if not model_path.is_absolute():
            model_path = (ROOT / model_rel).resolve()
        
        if model_path.exists() and model_path.suffix == ".gguf":
            return GPT4All(model_path.name, model_path=str(model_path.parent))
        
        # Prompt user to select model
        messagebox.showwarning("Model selection", "No GGUF model found. Please select one.")
        path = filedialog.askopenfilename(title="Select GGUF model", filetypes=[("GGUF", "*.gguf")])
        if not path:
            raise RuntimeError("No model selected.")
        
        # Save to config
        CONFIG["model_path"] = path
        save_json(CONFIG_PATH, CONFIG)
        
        return GPT4All(os.path.basename(path), model_path=os.path.dirname(path))

    def generate(self, prompt, max_tokens, temperature):
        with self.model.chat_session():
            return self.model.generate(prompt, max_tokens=max_tokens, temp=temperature).strip()


class BathyAPIBackend:
    """Cloud mode - connects to the Bathy FastAPI server."""
    
    def __init__(self, base: str):
        self.base = base.rstrip("/")

    def chat(self, message: str, mode: str = "auto") -> str:
        url = self.base + "/chat"
        try:
            r = httpx.post(url, json={"message": message, "mode": mode}, timeout=120)
            r.raise_for_status()
            data = r.json()
            return str(data.get("output", ""))
        except httpx.ConnectError:
            return "[Error] Cannot connect to Bathy server. Is it running? (run_server.bat)"
        except Exception as e:
            return f"[Error] {str(e)}"
    
    def get_status(self) -> dict:
        """Get server status."""
        try:
            r = httpx.get(self.base + "/status", timeout=5)
            return r.json()
        except Exception:
            return {"status": "offline"}
    
    def get_evolution(self) -> dict:
        """Get evolution status."""
        try:
            r = httpx.get(self.base + "/evolution", timeout=5)
            return r.json()
        except Exception:
            return {}


def get_backend():
    if CONFIG.get("engine", "cloud") == "local":
        return LocalBackend()
    return BathyAPIBackend(CONFIG["cloud_api_base"])


def build_prompt(user_msg, contexts, role="general"):
    roles = {
        "general": "You are GoodBoy.AI: answer directly, be concise, do not repeat the user's text.",
        "engineer": "You are GoodBoy.AI, senior engineer. Give practical, runnable steps.",
        "analyst": "You are GoodBoy.AI, critical reviewer. Point out gaps and risks."
    }
    ctx = "\n\n".join([f"[CTX{i+1}] {c}" for i, c in enumerate(contexts)]) if contexts else "None."
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"{roles.get(role, roles['general'])}\n\n"
        f"Context (use only if relevant):\n{ctx}\n\n"
        f"User: {user_msg}\nAssistant:"
    )


# ---------- Model Download Dialog ----------
class ModelDownloadDialog(tk.Toplevel):
    """Dialog for downloading AI models."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Model Manager")
        self.geometry("600x500")
        self.configure(bg=THEME_BG)
        self.transient(parent)
        self.grab_set()
        
        self.model_manager = ModelManager(MODELS_DIR) if HAS_MODEL_MANAGER else None
        
        # Header
        header = tk.Frame(self, bg=THEME_PANEL)
        header.pack(fill="x", padx=10, pady=10)
        tk.Label(header, text="Model Manager", font=("Segoe UI", 14, "bold"), 
                fg=THEME_ACCENT, bg=THEME_PANEL).pack(side="left")
        
        # Notebook for tabs
        style = ttk.Style()
        style.configure("Dark.TNotebook", background=THEME_BG)
        style.configure("Dark.TNotebook.Tab", background=THEME_PANEL, foreground=THEME_TEXT)
        
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Local models tab
        local_frame = tk.Frame(notebook, bg=THEME_BG)
        notebook.add(local_frame, text="Local Models")
        self._build_local_models_tab(local_frame)
        
        # Download tab
        download_frame = tk.Frame(notebook, bg=THEME_BG)
        notebook.add(download_frame, text="Download Models")
        self._build_download_tab(download_frame)
        
        # Progress area
        self.progress_frame = tk.Frame(self, bg=THEME_PANEL)
        self.progress_frame.pack(fill="x", padx=10, pady=10)
        
        self.progress_label = tk.Label(self.progress_frame, text="", fg=THEME_TEXT, bg=THEME_PANEL)
        self.progress_label.pack(side="left", padx=5)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, length=400, mode="determinate")
        self.progress_bar.pack(side="left", padx=5, fill="x", expand=True)
        
        # Close button
        tk.Button(self, text="Close", command=self.destroy, 
                 bg=THEME_PANEL, fg=THEME_TEXT).pack(pady=10)
    
    def _build_local_models_tab(self, parent):
        """Build local models list."""
        tk.Label(parent, text="Installed Models:", fg=THEME_TEXT, bg=THEME_BG,
                font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=5)
        
        # Models listbox
        list_frame = tk.Frame(parent, bg=THEME_BG)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.local_listbox = tk.Listbox(list_frame, bg=THEME_PANEL, fg=THEME_TEXT,
                                        selectbackground=THEME_ACCENT, height=10)
        self.local_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        self.local_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.local_listbox.yview)
        
        # Buttons
        btn_frame = tk.Frame(parent, bg=THEME_BG)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(btn_frame, text="Refresh", command=self._refresh_local_models,
                 bg=THEME_PANEL, fg=THEME_TEXT).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Set Active", command=self._set_active_model,
                 bg=THEME_ACCENT, fg="#000").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete", command=self._delete_model,
                 bg=THEME_ERROR, fg="#fff").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Browse...", command=self._browse_model,
                 bg=THEME_PANEL, fg=THEME_TEXT).pack(side="left", padx=5)
        
        self._refresh_local_models()
    
    def _build_download_tab(self, parent):
        """Build download models list."""
        tk.Label(parent, text="Available Models:", fg=THEME_TEXT, bg=THEME_BG,
                font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=5)
        
        # Models listbox with details
        list_frame = tk.Frame(parent, bg=THEME_BG)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.download_listbox = tk.Listbox(list_frame, bg=THEME_PANEL, fg=THEME_TEXT,
                                           selectbackground=THEME_ACCENT, height=8)
        self.download_listbox.pack(side="left", fill="both", expand=True)
        self.download_listbox.bind("<<ListboxSelect>>", self._on_download_select)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        self.download_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.download_listbox.yview)
        
        # Model details
        self.detail_label = tk.Label(parent, text="", fg=THEME_TEXT, bg=THEME_BG,
                                     justify="left", wraplength=550)
        self.detail_label.pack(anchor="w", padx=10, pady=5)
        
        # Download button
        tk.Button(parent, text="Download Selected Model", command=self._download_model,
                 bg=THEME_SUCCESS, fg="#000", font=("Segoe UI", 10, "bold")).pack(pady=10)
        
        # Populate list
        for name, info in KNOWN_MODELS.items():
            self.download_listbox.insert("end", f"{name} ({info['size_mb']}MB)")
    
    def _refresh_local_models(self):
        """Refresh local models list."""
        self.local_listbox.delete(0, "end")
        
        if self.model_manager:
            models = self.model_manager.list_local_models()
            for m in models:
                status = " [ACTIVE]" if m.get("is_active") else ""
                self.local_listbox.insert("end", f"{m['name']} ({m['size_mb']:.0f}MB){status}")
        else:
            # Fallback: scan directory
            for f in MODELS_DIR.glob("*.gguf"):
                size_mb = f.stat().st_size / (1024 * 1024)
                self.local_listbox.insert("end", f"{f.stem} ({size_mb:.0f}MB)")
    
    def _set_active_model(self):
        """Set selected model as active."""
        sel = self.local_listbox.curselection()
        if not sel:
            messagebox.showwarning("Select Model", "Please select a model first.")
            return
        
        if self.model_manager:
            models = self.model_manager.list_local_models()
            if sel[0] < len(models):
                model = models[sel[0]]
                self.model_manager.set_active_model(model["path"])
                CONFIG["model_path"] = model["path"]
                save_json(CONFIG_PATH, CONFIG)
                messagebox.showinfo("Success", f"Active model set to: {model['name']}")
                self._refresh_local_models()
    
    def _delete_model(self):
        """Delete selected model."""
        sel = self.local_listbox.curselection()
        if not sel:
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this model?"):
            if self.model_manager:
                models = self.model_manager.list_local_models()
                if sel[0] < len(models):
                    self.model_manager.delete_model(models[sel[0]]["path"])
                    self._refresh_local_models()
    
    def _browse_model(self):
        """Browse for a model file."""
        path = filedialog.askopenfilename(
            title="Select GGUF Model",
            filetypes=[("GGUF Models", "*.gguf")]
        )
        if path:
            # Copy to models directory
            import shutil
            dest = MODELS_DIR / os.path.basename(path)
            if not dest.exists():
                shutil.copy2(path, dest)
            
            CONFIG["model_path"] = str(dest)
            save_json(CONFIG_PATH, CONFIG)
            self._refresh_local_models()
            messagebox.showinfo("Success", f"Model added: {dest.name}")
    
    def _on_download_select(self, event):
        """Show details for selected model."""
        sel = self.download_listbox.curselection()
        if not sel:
            return
        
        names = list(KNOWN_MODELS.keys())
        if sel[0] < len(names):
            name = names[sel[0]]
            info = KNOWN_MODELS[name]
            self.detail_label.config(
                text=f"Description: {info['description']}\n"
                     f"Size: {info['size_mb']}MB | Min RAM: {info['min_ram_gb']}GB"
            )
    
    def _download_model(self):
        """Download selected model."""
        sel = self.download_listbox.curselection()
        if not sel:
            messagebox.showwarning("Select Model", "Please select a model to download.")
            return
        
        names = list(KNOWN_MODELS.keys())
        if sel[0] >= len(names):
            return
        
        model_name = names[sel[0]]
        
        if not self.model_manager:
            messagebox.showerror("Error", "Model manager not available.")
            return
        
        def progress_callback(progress, message):
            self.progress_bar["value"] = progress * 100
            self.progress_label.config(text=message)
            self.update_idletasks()
        
        def download_thread():
            try:
                self.model_manager.download_model(model_name, progress_callback)
                self.after(0, lambda: messagebox.showinfo("Success", f"Model downloaded: {model_name}"))
                self.after(0, self._refresh_local_models)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                self.after(0, lambda: self.progress_bar.configure(value=0))
                self.after(0, lambda: self.progress_label.config(text=""))
        
        threading.Thread(target=download_thread, daemon=True).start()


# ---------- Settings Dialog ----------
class SettingsDialog(tk.Toplevel):
    """Settings configuration dialog."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("500x400")
        self.configure(bg=THEME_BG)
        self.transient(parent)
        self.grab_set()
        
        # Header
        tk.Label(self, text="GoodBoy.AI Settings", font=("Segoe UI", 14, "bold"),
                fg=THEME_ACCENT, bg=THEME_BG).pack(pady=10)
        
        # Settings form
        form = tk.Frame(self, bg=THEME_BG)
        form.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Engine selection
        tk.Label(form, text="Engine:", fg=THEME_TEXT, bg=THEME_BG).grid(row=0, column=0, sticky="w", pady=5)
        self.engine_var = tk.StringVar(value=CONFIG.get("engine", "cloud"))
        engine_frame = tk.Frame(form, bg=THEME_BG)
        engine_frame.grid(row=0, column=1, sticky="w", pady=5)
        tk.Radiobutton(engine_frame, text="Cloud (Bathy API)", variable=self.engine_var, value="cloud",
                      bg=THEME_BG, fg=THEME_TEXT, selectcolor=THEME_PANEL).pack(side="left")
        tk.Radiobutton(engine_frame, text="Local (GPT4All)", variable=self.engine_var, value="local",
                      bg=THEME_BG, fg=THEME_TEXT, selectcolor=THEME_PANEL).pack(side="left")
        
        # API URL
        tk.Label(form, text="API URL:", fg=THEME_TEXT, bg=THEME_BG).grid(row=1, column=0, sticky="w", pady=5)
        self.api_url_entry = tk.Entry(form, bg=THEME_PANEL, fg=THEME_TEXT, width=40)
        self.api_url_entry.insert(0, CONFIG.get("cloud_api_base", "http://127.0.0.1:8000"))
        self.api_url_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        # Max tokens
        tk.Label(form, text="Max Tokens:", fg=THEME_TEXT, bg=THEME_BG).grid(row=2, column=0, sticky="w", pady=5)
        self.max_tokens_entry = tk.Entry(form, bg=THEME_PANEL, fg=THEME_TEXT, width=10)
        self.max_tokens_entry.insert(0, str(CONFIG.get("max_tokens", 512)))
        self.max_tokens_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Temperature
        tk.Label(form, text="Temperature:", fg=THEME_TEXT, bg=THEME_BG).grid(row=3, column=0, sticky="w", pady=5)
        self.temp_entry = tk.Entry(form, bg=THEME_PANEL, fg=THEME_TEXT, width=10)
        self.temp_entry.insert(0, str(CONFIG.get("temperature", 0.6)))
        self.temp_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        # User name
        tk.Label(form, text="Your Name:", fg=THEME_TEXT, bg=THEME_BG).grid(row=4, column=0, sticky="w", pady=5)
        self.name_entry = tk.Entry(form, bg=THEME_PANEL, fg=THEME_TEXT, width=20)
        self.name_entry.insert(0, CONFIG.get("user_name", "Mayor"))
        self.name_entry.grid(row=4, column=1, sticky="w", pady=5)
        
        # Auto-start server
        self.auto_start_var = tk.BooleanVar(value=CONFIG.get("auto_start_server", True))
        tk.Checkbutton(form, text="Auto-start server on launch", variable=self.auto_start_var,
                      bg=THEME_BG, fg=THEME_TEXT, selectcolor=THEME_PANEL).grid(row=5, column=0, columnspan=2, sticky="w", pady=5)
        
        # Buttons
        btn_frame = tk.Frame(self, bg=THEME_BG)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Save", command=self._save, bg=THEME_ACCENT, fg="#000",
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancel", command=self.destroy, bg=THEME_PANEL, fg=THEME_TEXT).pack(side="left", padx=10)
    
    def _save(self):
        """Save settings."""
        try:
            CONFIG["engine"] = self.engine_var.get()
            CONFIG["cloud_api_base"] = self.api_url_entry.get()
            CONFIG["max_tokens"] = int(self.max_tokens_entry.get())
            CONFIG["temperature"] = float(self.temp_entry.get())
            CONFIG["user_name"] = self.name_entry.get()
            CONFIG["auto_start_server"] = self.auto_start_var.get()
            
            save_json(CONFIG_PATH, CONFIG)
            messagebox.showinfo("Success", "Settings saved. Restart app to apply changes.")
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid value: {e}")


# ---------- Status Panel ----------
class StatusPanel(tk.Frame):
    """Panel showing system status and evolution metrics."""
    
    def __init__(self, parent, backend):
        super().__init__(parent, bg=THEME_PANEL)
        self.backend = backend
        
        # Title
        tk.Label(self, text="System Status", font=("Segoe UI", 10, "bold"),
                fg=THEME_ACCENT, bg=THEME_PANEL).pack(anchor="w", padx=5, pady=2)
        
        # Status indicators
        self.status_frame = tk.Frame(self, bg=THEME_PANEL)
        self.status_frame.pack(fill="x", padx=5, pady=2)
        
        self.server_status = tk.Label(self.status_frame, text="Server: ...", 
                                      fg=THEME_TEXT, bg=THEME_PANEL, font=("Segoe UI", 8))
        self.server_status.pack(side="left", padx=5)
        
        self.gen_label = tk.Label(self.status_frame, text="Gen: 0", 
                                  fg=THEME_TEXT, bg=THEME_PANEL, font=("Segoe UI", 8))
        self.gen_label.pack(side="left", padx=5)
        
        self.interactions_label = tk.Label(self.status_frame, text="Interactions: 0",
                                          fg=THEME_TEXT, bg=THEME_PANEL, font=("Segoe UI", 8))
        self.interactions_label.pack(side="left", padx=5)
        
        # Update periodically
        self._update_status()
    
    def _update_status(self):
        """Update status display."""
        try:
            if hasattr(self.backend, "get_status"):
                status = self.backend.get_status()
                if status.get("status") == "online":
                    self.server_status.config(text="Server: Online", fg=THEME_SUCCESS)
                else:
                    self.server_status.config(text="Server: Offline", fg=THEME_ERROR)
                
                evolution = self.backend.get_evolution() if hasattr(self.backend, "get_evolution") else {}
                self.gen_label.config(text=f"Gen: {evolution.get('generation', 0)}")
                self.interactions_label.config(text=f"Interactions: {evolution.get('total_interactions', 0)}")
        except Exception:
            self.server_status.config(text="Server: Unknown", fg=THEME_WARNING)
        
        self.after(5000, self._update_status)


# ---------- Main UI ----------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("GoodBoy.AI - Bathy City Console")
        self.root.geometry("1100x820")
        self.root.configure(bg=THEME_BG)

        # Server manager
        self.server_manager = ServerManager()

        # Teaching store for feedback
        self.teaching_store = get_teaching_store() if get_teaching_store else None
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Splash screen
        self.root.withdraw()
        splash = tk.Toplevel(self.root)
        splash.configure(bg=THEME_BG)
        splash.overrideredirect(True)
        w, h = 420, 280
        sw, sh = splash.winfo_screenwidth(), splash.winfo_screenheight()
        splash.geometry(f"{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}")

        # Logo on splash
        self._splash_logo = None
        logo_path = ASSETS_DIR / "goodboy_logo.png"
        if logo_path.exists():
            try:
                self._splash_logo = tk.PhotoImage(file=str(logo_path))
                tk.Label(splash, image=self._splash_logo, bg=THEME_BG).pack(pady=(18, 8))
            except Exception:
                pass

        tk.Label(splash, text="Making sure your AI is being a...", fg=THEME_ACCENT, bg=THEME_BG, font=("Segoe UI", 14, "bold")).pack(pady=(8, 4))
        tk.Label(splash, text="GoodBoy.AI", fg=THEME_TEXT, bg=THEME_BG, font=("Segoe UI", 12)).pack(pady=(0, 10))
        
        # Status message
        self.splash_status = tk.Label(splash, text="Initializing...", fg=THEME_TEXT, bg=THEME_BG, font=("Segoe UI", 9))
        self.splash_status.pack(pady=5)
        splash.update_idletasks()

        # Window icon
        icon_path = ASSETS_DIR / "goodboy_icon.ico"
        if icon_path.exists():
            try:
                self.root.iconbitmap(default=str(icon_path))
            except Exception:
                pass

        # Auto-start server if configured
        if CONFIG.get("auto_start_server", True) and CONFIG.get("engine") == "cloud":
            self.splash_status.config(text="Starting server...")
            splash.update_idletasks()
            self.server_manager.start()

        try:
            self.splash_status.config(text="Connecting to backend...")
            splash.update_idletasks()
            self.backend = get_backend()
            self.uses_bathy_api = hasattr(self.backend, "chat")
        except Exception as e:
            splash.destroy()
            messagebox.showerror("Startup error", str(e))
            root.destroy()
            return

        splash.destroy()
        self.root.deiconify()

        # Menu bar
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Chat", command=self.new_chat)
        file_menu.add_command(label="Upload Files", command=self.upload_files)
        file_menu.add_command(label="Save Chat", command=self.save_chat)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Model Manager", command=self.open_model_manager)
        tools_menu.add_command(label="Settings", command=self.open_settings)
        tools_menu.add_separator()
        tools_menu.add_command(label="Start Server", command=lambda: self.server_manager.start())
        tools_menu.add_command(label="Stop Server", command=lambda: self.server_manager.stop())

        # Top bar
        top = tk.Frame(root, bg=THEME_PANEL)
        top.pack(fill="x", padx=10, pady=8)

        # Logo
        self.logo_img = None
        if logo_path.exists():
            try:
                self.logo_img = tk.PhotoImage(file=str(logo_path))
                tk.Label(top, image=self.logo_img, bg=THEME_PANEL).pack(side="left", padx=4)
            except Exception:
                pass

        tk.Label(top, text="GoodBoy.AI - Bathy City Console", fg=THEME_ACCENT, bg=THEME_PANEL, font=("Segoe UI", 12, "bold")).pack(side="left", padx=8)

        # Controls
        controls = tk.Frame(top, bg=THEME_PANEL)
        controls.pack(side="right")
        tk.Button(controls, text="New Chat", command=self.new_chat, bg=THEME_PANEL, fg=THEME_TEXT).pack(side="left", padx=4)
        tk.Button(controls, text="+ Upload", command=self.upload_files, bg=THEME_PANEL, fg=THEME_TEXT).pack(side="left", padx=4)

        # Mode selector
        self.mode_var = tk.StringVar(value="auto")
        mode_frame = tk.Frame(controls, bg=THEME_PANEL)
        mode_frame.pack(side="left", padx=10)
        tk.Label(mode_frame, text="Mode:", fg=THEME_TEXT, bg=THEME_PANEL).pack(side="left")
        for mode in ["auto", "reflex", "council", "strategic"]:
            tk.Radiobutton(mode_frame, text=mode.capitalize(), variable=self.mode_var, value=mode, bg=THEME_PANEL, fg=THEME_TEXT, selectcolor=THEME_BG).pack(side="left")

        tk.Button(controls, text="Save Chat", command=self.save_chat, bg=THEME_PANEL, fg=THEME_TEXT).pack(side="left", padx=4)
        
        engine = CONFIG.get("engine", "cloud").upper()
        tk.Label(controls, text=f"Engine: {engine}", bg=THEME_PANEL, fg=THEME_TEXT).pack(side="left", padx=4)

        # Main content area with status panel
        content = tk.Frame(root, bg=THEME_BG)
        content.pack(fill="both", expand=True, padx=10, pady=6)
        
        # Status panel (right side)
        if self.uses_bathy_api:
            self.status_panel = StatusPanel(content, self.backend)
            self.status_panel.pack(side="right", fill="y", padx=(10, 0))

        # Chat area
        self.chat = scrolledtext.ScrolledText(content, wrap="word", height=28, bg=THEME_BG, fg=THEME_TEXT, insertbackground=THEME_ACCENT, font=("Consolas", 10))
        self.chat.pack(side="left", fill="both", expand=True)
        self.chat.config(state="normal")
        self.chat.insert("end", f"[Bathy] GoodBoy.AI online. Welcome, {CONFIG.get('user_name', 'Mayor')}!\n")
        self.chat.insert("end", "[Bathy] Upload blueprints or tell me what to do.\n\n")
        self.chat.config(state="disabled")
        
        # Configure text tags for colors
        self.chat.tag_configure("user", foreground=THEME_ACCENT)
        self.chat.tag_configure("assistant", foreground=THEME_TEXT)
        self.chat.tag_configure("system", foreground=THEME_WARNING)
        self.chat.tag_configure("error", foreground=THEME_ERROR)

        # Input area
        bottom = tk.Frame(root, bg=THEME_PANEL)
        bottom.pack(fill="x", padx=10, pady=10)
        self.entry = tk.Entry(bottom, bg="#0b1728", fg=THEME_TEXT, insertbackground=THEME_ACCENT, font=("Segoe UI", 11))
        self.entry.pack(side="left", fill="x", expand=True, padx=5, ipady=5)
        self.entry.bind("<Return>", lambda e: self.on_send())
        self.entry.focus_set()
        
        tk.Button(bottom, text="Send", command=self.on_send, bg=THEME_ACCENT, fg="#000000", font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)

        self.turns = []

    def append(self, who, text, tag=None):
        self.chat.config(state="normal")
        if tag:
            self.chat.insert("end", f"{who}: ", tag)
            self.chat.insert("end", f"{text}\n\n")
        else:
            self.chat.insert("end", f"{who}: {text}\n\n")
        self.chat.see("end")
        self.chat.config(state="disabled")

    def new_chat(self):
        self.chat.config(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.insert("end", "[Bathy] New chat started.\n\n", "system")
        self.chat.config(state="disabled")
        self.turns = []

    def upload_files(self):
        paths = filedialog.askopenfilenames(
            title="Upload files",
            filetypes=[("Supported", "*.txt *.md *.json *.pdf *.docx"), ("All", "*.*")]
        )
        if not paths:
            return
        
        total = 0
        for p in paths:
            ext = os.path.splitext(p)[1].lower()
            reader = READERS.get(ext)
            if not reader:
                messagebox.showwarning("Skip", f"Unsupported: {os.path.basename(p)}")
                continue
            
            # Copy to memory/docs
            dest = DOCS_DIR / os.path.basename(p)
            try:
                if Path(p).resolve() != dest.resolve():
                    dest.write_bytes(Path(p).read_bytes())
            except Exception as e:
                messagebox.showwarning("Copy error", f"{p}: {e}")
            
            text = reader(p)
            total += add_chunks(dest, text)
        
        self.append("System", f"Ingested {len(paths)} file(s). Added {total} chunk(s).", "system")

    def save_chat(self):
        try:
            existing = json.loads(CHATS_PATH.read_text())
        except Exception:
            existing = []
        existing.append(self.turns)
        CHATS_PATH.write_text(json.dumps(existing, indent=2, ensure_ascii=False))
        self.append("System", "Chat saved.", "system")
    
    def open_model_manager(self):
        ModelDownloadDialog(self.root)
    
    def open_settings(self):
        SettingsDialog(self.root)

    def on_close(self):
        try:
            feedback = simpledialog.askstring(
                "Before we close",
                "Anything I could do better next time?\n\n(Optional - stored locally so Bathy can improve)",
                parent=self.root
            )
            if feedback and self.teaching_store:
                try:
                    self.teaching_store.add_lesson(
                        topic="desktop-ui-feedback",
                        instruction=feedback,
                        tags=["feedback", "session_end"]
                    )
                except Exception:
                    pass
        except Exception:
            pass
        
        # Stop server if we started it
        self.server_manager.stop()
        self.root.destroy()

    def on_send(self):
        msg = self.entry.get().strip()
        if not msg:
            return
        self.entry.delete(0, "end")
        self.append("You", msg, "user")
        self.turns.append({"user": msg})
        threading.Thread(target=self._answer, args=(msg,), daemon=True).start()

    def _answer(self, msg):
        try:
            if self.uses_bathy_api:
                # Use Bathy API with selected mode
                mode = self.mode_var.get()
                out = self.backend.chat(msg, mode=mode)
            else:
                # Local mode with RAG
                ctx = retrieve(msg, top_k=4)
                prompt = build_prompt(msg, ctx, "general")
                out = self.backend.generate(prompt, CONFIG["max_tokens"], CONFIG["temperature"])
            
            self.append("GoodBoy.AI", out, "assistant")
            self.turns[-1]["ai"] = out
        except Exception as e:
            self.append("Error", str(e), "error")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
