"""LLM Backend - Local GGUF model via GPT4All with robust error handling."""
import os
import json
from pathlib import Path
from typing import Optional
from functools import lru_cache
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instance (singleton)
_model = None
_config = None
_model_error = None


def get_config() -> dict:
    """Load GoodBoy config with proper defaults."""
    global _config
    if _config is not None:
        return _config
    
    config_path = Path("data/GoodBoy_config.json")
    default = {
        "engine": "local",
        "model_path": "models/",
        "cloud_api_base": "http://127.0.0.1:8000",
        "max_tokens": 512,
        "temperature": 0.6,
    }
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                _config = {**default, **loaded}
                return _config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
    
    # Save default
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)
    except Exception:
        pass
    
    _config = default
    return _config


def get_model():
    """Get or initialize the local LLM model with comprehensive error handling."""
    global _model, _model_error
    
    if _model is not None:
        return _model
    
    if _model_error:
        raise _model_error
    
    try:
        try:
            from gpt4all import GPT4All
        except ImportError as e:
            _model_error = RuntimeError(
                "gpt4all not installed. Please run: pip install gpt4all\n"
                "Or switch to cloud mode in settings."
            )
            raise _model_error
        
        config = get_config()
        model_rel = config.get("model_path", "models/")
        model_path = Path(model_rel)
        
        if not model_path.is_absolute():
            model_path = (Path.cwd() / model_rel).resolve()
        
        gguf_file = None
        
        # Search strategies
        search_paths = [
            model_path if model_path.is_file() else None,
            model_path / "*.gguf" if model_path.is_dir() else None,
            Path("models") / "*.gguf",
            Path.cwd() / "models" / "*.gguf",
        ]
        
        for search_path in search_paths:
            if search_path is None:
                continue
            
            if search_path.exists() and search_path.is_file() and search_path.suffix == ".gguf":
                gguf_file = search_path
                break
            
            if search_path.parent.exists():
                matches = list(search_path.parent.glob(search_path.name if "*" in str(search_path) else "*.gguf"))
                if matches:
                    gguf_file = matches[0]
                    break
        
        if not gguf_file or not gguf_file.exists():
            _model_error = FileNotFoundError(
                "No GGUF model found. Please:\n"
                "1. Download a model using the Model Manager in the UI\n"
                "2. Place a .gguf file in the 'models' directory\n"
                "3. Or switch to cloud mode in settings"
            )
            raise _model_error
        
        logger.info(f"Loading model: {gguf_file}")
        
        try:
            _model = GPT4All(
                model_name=gguf_file.name,
                model_path=str(gguf_file.parent),
                allow_download=False
            )
            logger.info("Model loaded successfully")
            return _model
        except Exception as e:
            _model_error = RuntimeError(f"Failed to load model {gguf_file.name}: {e}")
            raise _model_error
            
    except Exception as e:
        logger.error(f"Model initialization failed: {e}")
        _model_error = e
        raise


def generate(prompt: str, max_tokens: int = 512, temperature: float = 0.6) -> str:
    """Generate text using the local LLM with fallback."""
    try:
        model = get_model()
        with model.chat_session():
            response = model.generate(
                prompt, 
                max_tokens=max_tokens, 
                temp=temperature
            )
        return response.strip()
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return f"[LLM Error] {str(e)}\n\nPlease check your model setup or switch to cloud mode."


def generate_with_system(
    system_prompt: str,
    user_message: str,
    context: Optional[str] = None,
    max_tokens: int = 512,
    temperature: float = 0.6
) -> str:
    """Generate with system prompt and optional context."""
    parts = [system_prompt]
    if context:
        parts.append(f"\n\nContext:\n{context}")
    parts.append(f"\n\nUser: {user_message}\nAssistant:")
    
    full_prompt = "".join(parts)
    return generate(full_prompt, max_tokens, temperature)


def is_available() -> bool:
    """Check if LLM is available."""
    try:
        get_model()
        return True
    except Exception:
        return False


def get_error() -> Optional[str]:
    """Get current model error if any."""
    return str(_model_error) if _model_error else None
