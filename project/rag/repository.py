from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from project.db.models import Document, DocumentChunk


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_filename(self, filename: str) -> Optional[Document]:
        return (
            self.db.query(Document)
            .filter(Document.filename == filename)
            .first()
        )

    def create_document(
        self,
        filename: str,
        content: str,
        metadata: Dict[str, Any],
    ) -> Document:
        document = Document(
            filename=filename,
            content=content,
            doc_metadata=metadata,
        )

        self.db.add(document)
        self.db.flush()
        self.db.refresh(document)

        return document

    def create_chunks(
        self,
        document_id: int,
        chunks: List[str],
        embeddings: List[List[float]],
    ) -> List[DocumentChunk]:
        saved_chunks: List[DocumentChunk] = []

        for index, chunk_text in enumerate(chunks):
            chunk = DocumentChunk(
                document_id=document_id,
                content=chunk_text,
                chunk_index=index,
                embedding=embeddings[index],
            )

            self.db.add(chunk)
            saved_chunks.append(chunk)

        self.db.flush()

        for chunk in saved_chunks:
            self.db.refresh(chunk)

        return saved_chunks

    def create_document_with_chunks(
        self,
        filename: str,
        content: str,
        metadata: Dict[str, Any],
        chunks: List[str],
        embeddings: List[List[float]],
    ) -> Document:
        existing = self.get_by_filename(filename)

        if existing:
            return existing

        document = self.create_document(
            filename=filename,
            content=content,
            metadata=metadata,
        )

        self.create_chunks(
            document_id=document.id,
            chunks=chunks,
            embeddings=embeddings,
        )

        return document

    def list_documents(self) -> List[Document]:
        return (
            self.db.query(Document)
            .order_by(Document.created_at.desc())
            .all()
        )

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        sql = text(
            """
            SELECT
                c.id AS chunk_id,
                c.document_id AS document_id,
                d.filename AS filename,
                c.content AS content,
                1 - (c.embedding <=> CAST(:query_embedding AS vector)) AS score
            FROM document_chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY c.embedding <=> CAST(:query_embedding AS vector)
            LIMIT :top_k
            """
        )

        rows = self.db.execute(
            sql,
            {
                "query_embedding": query_embedding,
                "top_k": top_k,
            },
        ).mappings().all()

        return [dict(row) for row in rows]
