"""
Search Tool — Knowledge retrieval for agents.

Provides semantic-style search over a local knowledge base.
In production, this would connect to a vector store or search index.
For demo purposes, uses TF-IDF similarity over a document collection.
"""

import math
from collections import Counter
from dataclasses import dataclass
from .tool_registry import ToolDefinition


@dataclass
class SearchResult:
    """A single search result."""
    doc_id: str
    title: str
    content: str
    score: float

    def to_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "snippet": self.content[:200],
            "score": round(self.score, 4)
        }


class KnowledgeBase:
    """
    Simple TF-IDF knowledge base for demo purposes.

    In production, replace with a vector store (e.g., Azure AI Search,
    FAISS, Chroma) for embedding-based semantic retrieval.
    """

    def __init__(self):
        self._documents: dict[str, dict] = {}
        self._idf: dict[str, float] = {}
        self._tfidf: dict[str, dict[str, float]] = {}
        self._dirty = True

    def add_document(self, doc_id: str, title: str, content: str) -> None:
        """Add a document to the knowledge base."""
        self._documents[doc_id] = {"title": title, "content": content}
        self._dirty = True

    def _tokenize(self, text: str) -> list[str]:
        """Simple whitespace + lowercase tokenizer."""
        return [w.strip(".,!?;:\"'()[]{}").lower()
                for w in text.split() if len(w.strip(".,!?;:\"'()[]{}")) > 2]

    def _build_index(self) -> None:
        """Build TF-IDF index over all documents."""
        if not self._dirty:
            return

        n_docs = len(self._documents)
        doc_freq: Counter = Counter()

        # Compute term frequencies per document
        tf_per_doc = {}
        for doc_id, doc in self._documents.items():
            tokens = self._tokenize(doc["content"] + " " + doc["title"])
            tf = Counter(tokens)
            max_tf = max(tf.values()) if tf else 1
            tf_per_doc[doc_id] = {t: c / max_tf for t, c in tf.items()}
            doc_freq.update(set(tokens))

        # Compute IDF
        self._idf = {
            term: math.log(n_docs / (1 + freq))
            for term, freq in doc_freq.items()
        }

        # Compute TF-IDF vectors
        self._tfidf = {
            doc_id: {
                term: tf_val * self._idf.get(term, 0)
                for term, tf_val in tf.items()
            }
            for doc_id, tf in tf_per_doc.items()
        }

        self._dirty = False

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Search the knowledge base with a text query."""
        self._build_index()

        query_tokens = self._tokenize(query)
        query_tf = Counter(query_tokens)
        max_qtf = max(query_tf.values()) if query_tf else 1
        query_vec = {
            t: (c / max_qtf) * self._idf.get(t, 0)
            for t, c in query_tf.items()
        }

        scores = []
        for doc_id, doc_vec in self._tfidf.items():
            # Cosine similarity
            dot = sum(query_vec.get(t, 0) * doc_vec.get(t, 0)
                      for t in set(query_vec) | set(doc_vec))
            mag_q = math.sqrt(sum(v ** 2 for v in query_vec.values())) or 1
            mag_d = math.sqrt(sum(v ** 2 for v in doc_vec.values())) or 1
            score = dot / (mag_q * mag_d)
            scores.append((doc_id, score))

        scores.sort(key=lambda x: x[1], reverse=True)

        return [
            SearchResult(
                doc_id=doc_id,
                title=self._documents[doc_id]["title"],
                content=self._documents[doc_id]["content"],
                score=score
            )
            for doc_id, score in scores[:top_k]
            if score > 0
        ]


def create_search_tools(knowledge_base: KnowledgeBase | None = None) -> list[ToolDefinition]:
    """Create search tools backed by a knowledge base."""
    kb = knowledge_base or KnowledgeBase()

    def search(query: str, top_k: int = 5) -> list[dict]:
        """Search the knowledge base."""
        results = kb.search(query, top_k)
        return [r.to_dict() for r in results]

    def add_document(doc_id: str, title: str, content: str) -> str:
        """Add a document to the knowledge base."""
        kb.add_document(doc_id, title, content)
        return f"Added document '{doc_id}': {title}"

    return [
        ToolDefinition(
            name="search_knowledge",
            description="Search the knowledge base for relevant information",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "top_k": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            },
            handler=search
        ),
        ToolDefinition(
            name="add_knowledge",
            description="Add a document to the knowledge base",
            input_schema={
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string"},
                    "title": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["doc_id", "title", "content"]
            },
            handler=add_document
        ),
    ]
