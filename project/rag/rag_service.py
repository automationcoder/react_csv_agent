from pathlib import Path
from typing import Any, Dict, List

from project.db.transaction import transaction
from project.rag.chunker import TextChunker
from project.rag.embeddings import get_embedding_service
from project.rag.loaders import DocumentLoader
from project.rag.repository import DocumentRepository
from project.rag.schemas import ExtractionResult


class RAGService:
    def __init__(self):
        self.loader = DocumentLoader()
        self.chunker = TextChunker(chunk_size=800, chunk_overlap=100)
        self.embedding_service = get_embedding_service()

    def process_document(self, file_path: str) -> ExtractionResult:
        try:
            path = Path(file_path)
            content = self.loader.load(file_path)

            chunks = self.chunker.split_text(content)

            if not chunks:
                return ExtractionResult(
                    success=False,
                    filename=path.name,
                    error="Document has no extractable text.",
                )

            embeddings = self.embedding_service.embed_texts(chunks)

            metadata: Dict[str, Any] = {
                "source_file": path.name,
                "extension": path.suffix.lower(),
                "chunk_count": len(chunks),
            }

            with transaction() as db:
                repo = DocumentRepository(db)

                document = repo.create_document_with_chunks(
                    filename=path.name,
                    content=content,
                    metadata=metadata,
                    chunks=chunks,
                    embeddings=embeddings,
                )

                return ExtractionResult(
                    success=True,
                    document_id=document.id,
                    filename=document.filename,
                    metadata=metadata,
                )

        except Exception as exc:
            return ExtractionResult(
                success=False,
                filename=file_path,
                error=str(exc),
            )

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        query_embedding = self.embedding_service.embed_text(query)

        with transaction() as db:
            repo = DocumentRepository(db)

            return repo.similarity_search(
                query_embedding=query_embedding,
                top_k=top_k,
            )

    def list_documents(self) -> List[Dict[str, Any]]:
        with transaction() as db:
            repo = DocumentRepository(db)
            documents = repo.list_documents()

            return [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "metadata": doc.doc_metadata,
                    "created_at": str(doc.created_at),
                }
                for doc in documents
            ]
