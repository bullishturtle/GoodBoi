from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .config import ROOT, load_config

try:
    import chromadb
    from chromadb.utils import embedding_functions
except Exception:  # pragma: no cover
    chromadb = None  # type: ignore
    embedding_functions = None  # type: ignore


MEM_DIR = ROOT / "data" / "memory"
MEM_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR = MEM_DIR / "chroma"
CHUNKS_FALLBACK = ROOT / "memory" / "chunks.jsonl"


class MemoryBackend:
    """Embeddings-based memory over chats/docs with keyword fallback.

    - Primary: ChromaDB with sentence-transformers embeddings.
    - Fallback: keyword search over memory/chunks.jsonl (existing RAG).
    """

    def __init__(self) -> None:
        self.cfg = load_config()
        self.client = None
        self.collection = None
        self.embedder = None
        if chromadb is not None and embedding_functions is not None:
            try:
                self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
                self.embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
                self.collection = self.client.get_or_create_collection(
                    name="goodboy_memory", embedding_function=self.embedder
                )
            except Exception:
                self.client = None
                self.collection = None

    # --- Ingestion ---

    def ingest_items(self, items: List[Dict[str, Any]]) -> int:
        """Ingest items into embeddings memory.

        Each item: {"id": str, "text": str, "meta": {..}}.
        """
        if not self.collection:
            return 0
        if not items:
            return 0
        ids = [it["id"] for it in items]
        texts = [it["text"] for it in items]
        metadatas = [it.get("meta", {}) for it in items]
        self.collection.add(ids=ids, documents=texts, metadatas=metadatas)
        return len(items)

    # --- Query ---

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        if self.collection is not None:
            try:
                res = self.collection.query(query_texts=[query], n_results=k)
                out: List[Dict[str, Any]] = []
                for i in range(len(res.get("ids", [[]])[0])):
                    out.append(
                        {
                            "id": res["ids"][0][i],
                            "text": res["documents"][0][i],
                            "meta": res["metadatas"][0][i],
                        }
                    )
                return out
            except Exception:
                pass
        # Fallback: keyword over chunks.jsonl
        return self._fallback_search(query, k=k)

    def _fallback_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        if not CHUNKS_FALLBACK.exists():
            return []
        q = set(w.lower() for w in query.split())
        rows: List[Dict[str, Any]] = []
        with CHUNKS_FALLBACK.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                text = obj.get("text", "")
                tokens = set(w.lower() for w in text.split())
                score = len(q & tokens)
                rows.append({"score": score, "id": f"fallback-{obj.get('source','')}-{obj.get('idx',0)}", "text": text, "meta": obj})
        rows.sort(key=lambda r: r["score"], reverse=True)
        return rows[:k]
