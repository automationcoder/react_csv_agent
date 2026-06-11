import json
from pydantic import BaseModel, Field

from project.rag.rag_service import RAGService
from project.tools.registry import register_tool


class SearchDocumentsParams(BaseModel):
    query: str = Field(description="Question or search query to search in stored documents.")
    top_k: int = Field(default=3, description="Number of relevant chunks to return.", ge=1, le=10)


class ListStoredDocumentsParams(BaseModel):
    limit: int = Field(default=20, description="Maximum number of stored documents to list.", ge=1, le=100)


@register_tool
def search_documents(params: SearchDocumentsParams) -> str:
    """Search stored documents using semantic similarity over pgvector embeddings."""
    service = RAGService()
    results = service.search(query=params.query, top_k=params.top_k)
    return json.dumps(results, indent=2, ensure_ascii=False)


@register_tool
def list_stored_documents(params: ListStoredDocumentsParams) -> str:
    """List documents stored in PostgreSQL for RAG retrieval."""
    service = RAGService()
    documents = service.list_documents()
    return json.dumps(documents[: params.limit], indent=2, ensure_ascii=False)
