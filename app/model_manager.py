"""Model Manager - Downloads, validates, and manages GGUF models."""
import os
import hashlib
import requests
from pathlib import Path
from typing import Optional, List, Dict, Callable
import json
from datetime import datetime
import shutil

# Known good models with their metadata
KNOWN_MODELS = {
    "qwen2.5-7b-instruct-q5_k_m": {
        "url": "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q5_k_m-00001-of-00002.gguf",
        "size_mb": 5200,
        "sha256": None,  # Optional validation
        "description": "Qwen 2.5 7B - Recommended for general use",
        "min_ram_gb": 8
    },
    "mistral-7b-instruct-v0.2-q4_k_m": {
        "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "size_mb": 4370,
        "sha256": None,
        "description": "Mistral 7B - Fast and efficient",
        "min_ram_gb": 6
    },
    "phi-3-mini-4k-instruct-q4_k_m": {
        "url": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf",
        "size_mb": 2400,
        "sha256": None,
        "description": "Phi-3 Mini - Lightweight, good for low-RAM systems",
        "min_ram_gb": 4
    }
}


class ModelManager:
    """Manages local GGUF model downloads and validation."""
    
    def __init__(self, models_dir: Path = None):
        self.models_dir = models_dir or Path("models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.models_dir / "registry.json"
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Load model registry."""
        if self.registry_file.exists():
            try:
                return json.loads(self.registry_file.read_text())
            except Exception:
                pass
        return {"models": [], "active_model": None}
    
    def _save_registry(self):
        """Save model registry."""
        self.registry_file.write_text(json.dumps(self.registry, indent=2))
    
    def list_available_models(self) -> List[Dict]:
        """List known downloadable models."""
        return [
            {"name": name, **info}
            for name, info in KNOWN_MODELS.items()
        ]
    
    def list_local_models(self) -> List[Dict]:
        """List locally available models."""
        models = []
        for gguf_file in self.models_dir.glob("*.gguf"):
            models.append({
                "name": gguf_file.stem,
                "path": str(gguf_file),
                "size_mb": gguf_file.stat().st_size / (1024 * 1024),
                "is_active": str(gguf_file) == self.registry.get("active_model")
            })
        return models
    
    def download_model(
        self, 
        model_name: str, 
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Path:
        """Download a model from known sources."""
        if model_name not in KNOWN_MODELS:
            raise ValueError(f"Unknown model: {model_name}. Available: {list(KNOWN_MODELS.keys())}")
        
        model_info = KNOWN_MODELS[model_name]
        url = model_info["url"]
        filename = url.split("/")[-1]
        target_path = self.models_dir / filename
        
        if target_path.exists():
            if progress_callback:
                progress_callback(1.0, f"Model already exists: {filename}")
            return target_path
        
        # Download with progress
        if progress_callback:
            progress_callback(0.0, f"Starting download: {filename}")
        
        temp_path = target_path.with_suffix(".download")
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size and progress_callback:
                            progress = downloaded / total_size
                            progress_callback(progress, f"Downloading: {downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB")
            
            # Validate if sha256 available
            if model_info.get("sha256"):
                if progress_callback:
                    progress_callback(0.99, "Validating checksum...")
                
                file_hash = self._compute_sha256(temp_path)
                if file_hash != model_info["sha256"]:
                    temp_path.unlink()
                    raise ValueError("Checksum mismatch - download corrupted")
            
            # Move to final location
            shutil.move(str(temp_path), str(target_path))
            
            # Update registry
            self.registry["models"].append({
                "name": model_name,
                "path": str(target_path),
                "downloaded_at": datetime.now().isoformat()
            })
            self._save_registry()
            
            if progress_callback:
                progress_callback(1.0, f"Download complete: {filename}")
            
            return target_path
            
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise RuntimeError(f"Download failed: {e}")
    
    def _compute_sha256(self, filepath: Path) -> str:
        """Compute SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def set_active_model(self, model_path: str):
        """Set the active model for inference."""
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        self.registry["active_model"] = str(path)
        self._save_registry()
    
    def get_active_model(self) -> Optional[Path]:
        """Get the currently active model path."""
        active = self.registry.get("active_model")
        if active and Path(active).exists():
            return Path(active)
        
        # Fallback to first available model
        local_models = self.list_local_models()
        if local_models:
            return Path(local_models[0]["path"])
        
        return None
    
    def delete_model(self, model_path: str) -> bool:
        """Delete a local model."""
        path = Path(model_path)
        if path.exists() and path.parent == self.models_dir:
            path.unlink()
            
            # Update registry
            self.registry["models"] = [
                m for m in self.registry["models"] 
                if m.get("path") != str(path)
            ]
            if self.registry.get("active_model") == str(path):
                self.registry["active_model"] = None
            self._save_registry()
            
            return True
        return False
    
    def get_model_info(self, model_path: str) -> Dict:
        """Get detailed info about a model."""
        path = Path(model_path)
        if not path.exists():
            return {"error": "Model not found"}
        
        return {
            "name": path.stem,
            "path": str(path),
            "size_mb": path.stat().st_size / (1024 * 1024),
            "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            "is_active": str(path) == self.registry.get("active_model")
        }
