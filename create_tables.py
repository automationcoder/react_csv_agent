from sqlalchemy import text

from project.db.database import Base, engine
from project.db.models import Document, DocumentChunk


def create_tables():
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    Base.metadata.create_all(bind=engine)

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw
                ON document_chunks
                USING hnsw (embedding vector_cosine_ops)
                """
            )
        )

    print("Database tables and pgvector index created successfully.")


if __name__ == "__main__":
    create_tables()
