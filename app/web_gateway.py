"""External Gateways - Web browsing and API interactions."""
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path
from urllib.parse import urlparse, urljoin
import re

class WebGateway:
    """Handles web interactions for GoodBoy.AI."""
    
    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path("data/web_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "GoodBoy.AI/1.0 (Personal Assistant)"
        })
    
    def fetch_url(self, url: str, use_cache: bool = True) -> Dict:
        """Fetch content from a URL."""
        cache_key = self._url_to_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        # Check cache
        if use_cache and cache_file.exists():
            try:
                cached = json.loads(cache_file.read_text())
                cache_time = datetime.fromisoformat(cached["fetched_at"])
                # Cache valid for 1 hour
                if (datetime.now() - cache_time).seconds < 3600:
                    return cached
            except Exception:
                pass
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            result = {
                "url": url,
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", ""),
                "content": response.text[:50000],  # Limit content size
                "fetched_at": datetime.now().isoformat(),
                "success": True
            }
            
            # Cache result
            cache_file.write_text(json.dumps(result))
            
            return result
            
        except Exception as e:
            return {
                "url": url,
                "success": False,
                "error": str(e),
                "fetched_at": datetime.now().isoformat()
            }
    
    def _url_to_cache_key(self, url: str) -> str:
        """Convert URL to a safe cache filename."""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:16]
    
    def extract_text(self, html: str) -> str:
        """Extract readable text from HTML."""
        # Simple text extraction (no BeautifulSoup dependency)
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def search_web(self, query: str) -> Dict:
        """Perform a web search (placeholder - needs API key)."""
        # This would integrate with a search API
        return {
            "query": query,
            "results": [],
            "message": "Web search requires API configuration. Add search API key in settings.",
            "timestamp": datetime.now().isoformat()
        }
    
    def check_url_safety(self, url: str) -> Dict:
        """Basic URL safety check."""
        parsed = urlparse(url)
        
        # Basic checks
        is_https = parsed.scheme == "https"
        is_known_domain = parsed.netloc in [
            "github.com", "stackoverflow.com", "python.org",
            "docs.python.org", "pypi.org", "wikipedia.org"
        ]
        
        return {
            "url": url,
            "is_https": is_https,
            "is_known_safe": is_known_domain,
            "recommendation": "safe" if (is_https or is_known_domain) else "caution"
        }


class APIGateway:
    """Manages external API integrations."""
    
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path("data/api_integrations.json")
        self.integrations = self._load_integrations()
    
    def _load_integrations(self) -> Dict:
        """Load API integrations config."""
        if self.config_path.exists():
            try:
                return json.loads(self.config_path.read_text())
            except Exception:
                pass
        return {"apis": {}}
    
    def _save_integrations(self):
        """Save API integrations config."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(self.integrations, indent=2))
    
    def register_api(self, name: str, base_url: str, api_key: Optional[str] = None, headers: Optional[Dict] = None):
        """Register a new API integration."""
        self.integrations["apis"][name] = {
            "base_url": base_url,
            "api_key": api_key,
            "headers": headers or {},
            "registered_at": datetime.now().isoformat()
        }
        self._save_integrations()
    
    def call_api(self, api_name: str, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Call a registered API."""
        if api_name not in self.integrations["apis"]:
            return {"success": False, "error": f"API not registered: {api_name}"}
        
        api = self.integrations["apis"][api_name]
        url = urljoin(api["base_url"], endpoint)
        
        headers = api.get("headers", {}).copy()
        if api.get("api_key"):
            headers["Authorization"] = f"Bearer {api['api_key']}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_apis(self) -> List[str]:
        """List registered APIs."""
        return list(self.integrations["apis"].keys())
