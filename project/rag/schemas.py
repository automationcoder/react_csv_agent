from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    title: Optional[str] = None
    document_type: Optional[str] = None
    author: Optional[str] = None
    source_file: Optional[str] = None


class ChunkData(BaseModel):
    chunk_index: int
    content: str
    embedding: List[float]


class SearchResult(BaseModel):
    document_id: int
    chunk_id: int
    score: float
    content: str


class ExtractionResult(BaseModel):
    success: bool
    document_id: Optional[int] = None
    filename: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)