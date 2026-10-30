"""Knowledge management and lightweight TF-IDF retrieval-augmented generation (RAG)."""

import math
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.knowledge import CropKnowledge, KnowledgeDocument
from utils.logging_config import logger


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase terms, removing non-alphanumeric characters."""
    return re.findall(r"\b\w{2,}\b", text.lower())


class KnowledgeService:

    @staticmethod
    def get_crop_knowledge(db: Session, crop_name: str) -> Optional[CropKnowledge]:
        """Fetch verified agronomic guidelines for a specific crop."""
        return db.query(CropKnowledge).filter(
            CropKnowledge.crop_name.ilike(f"%{crop_name.strip()}%")
        ).first()

    @staticmethod
    def list_all_crops_knowledge(db: Session, search: Optional[str] = None) -> List[CropKnowledge]:
        """List all crops in the knowledge library with optional search filter."""
        query = db.query(CropKnowledge)
        if search:
            s = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    CropKnowledge.crop_name.ilike(s),
                    CropKnowledge.scientific_name.ilike(s),
                    CropKnowledge.description.ilike(s),
                )
            )
        return query.order_by(CropKnowledge.crop_name).all()

    @staticmethod
    def retrieve_relevant_documents(
        db: Session,
        query: str,
        top_k: int = 3,
        threshold: float = 0.05,
    ) -> List[Dict[str, Any]]:
        """Retrieve most relevant verified agricultural knowledge documents using TF-IDF.

        Returns list of structured document dictionaries with title, content, and source.
        """
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        docs = db.query(KnowledgeDocument).all()
        if not docs:
            return []

        num_docs = len(docs)
        # 1. Compute document token frequencies and document frequency (DF) for query terms
        doc_tokens_list = []
        df: Dict[str, int] = {t: 0 for t in query_tokens}

        for doc in docs:
            full_text = f"{doc.title} {doc.topic} {doc.content}"
            tokens = tokenize(full_text)
            token_set = set(tokens)
            doc_tokens_list.append((doc, tokens))
            for t in query_tokens:
                if t in token_set:
                    df[t] += 1

        # 2. Compute IDF for query terms
        idf: Dict[str, float] = {}
        for t, freq in df.items():
            # Standard smooth IDF formula
            idf[t] = math.log((1 + num_docs) / (1 + freq)) + 1.0

        # 3. Score each document based on TF-IDF cosine-like dot product
        scored_docs = []
        for doc, tokens in doc_tokens_list:
            if not tokens:
                continue
            total_tokens = len(tokens)
            # Count terms
            counts: Dict[str, int] = {}
            for tok in tokens:
                counts[tok] = counts.get(tok, 0) + 1

            score = 0.0
            for t in query_tokens:
                if t in counts:
                    tf = counts[t] / total_tokens
                    score += tf * idf[t]

            # Boost exact title match
            if any(t in doc.title.lower() for t in query_tokens):
                score += 0.5

            if score > threshold:
                scored_docs.append((score, doc))

        # Sort descending by score
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, doc in scored_docs[:top_k]:
            results.append({
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "source_name": doc.source_name,
                "source_url": doc.source_url,
                "topic": doc.topic,
                "score": round(score, 4),
            })

        logger.info(f"RAG query '{query[:40]}' retrieved {len(results)} documents.")
        return results
