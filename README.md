
# ReAct CSV + RAG Document Analyst Agent

## Project Overview

This project implements a local AI agent using the ReAct (Reasoning + Acting) pattern, local LLM inference through Ollama, CSV analysis tools, and a Retrieval Augmented Generation (RAG) pipeline using PostgreSQL and pgvector.

The solution extends a ReAct CSV Agent by adding document ingestion, embedding generation, vector storage, semantic retrieval, and document question answering.

---

# Features

The agent can:

* Use a local LLM through Ollama
* Execute tools through a Tool Registry
* Inspect local CSV files
* Aggregate CSV data
* Load TXT, PDF, and DOCX documents
* Split documents into chunks
* Generate embeddings using Sentence Transformers
* Store embeddings in PostgreSQL with pgvector
* Perform semantic similarity search
* Answer questions using retrieved document content

---

# Architecture

```text
User
 ↓
ReAct Agent
 ↓
Prompt Registry
 ↓
Local LLM (Ollama)
 ↓
Tool Registry
 ↓
Tools
 ├── CSV Tools
 └── RAG Tools
       ↓
       RAG Service
       ↓
       Document Loader
       ↓
       Text Chunker
       ↓
       Embedding Service
       ↓
       PostgreSQL + pgvector
```

---

# Design Patterns

## Registry Pattern

Used to register and discover tools dynamically.

File:

```text
project/tools/registry.py
```

Stores all available tools inside:

```python
TOOL_REGISTRY
```

---

## Decorator Pattern

Tools are automatically registered using decorators.

Example:

```python
@register_tool
def search_documents(params):
    ...
```

---

## Factory Pattern

Used to instantiate different LLM providers.

File:

```text
project/llm/providers.py
```

Supported providers:

* Local Ollama
* OpenAI
* Google Gemini
* Anthropic Claude

---

## Singleton Pattern

Used for shared embedding service initialization.

Example:

```python
@lru_cache(maxsize=1)
def get_embedding_service():
    ...
```

---

# Project Structure

```text
react_csv_agent/
│
├── main.py
├── create_tables.py
├── ingest_documents.py
├── docker-compose.yml
├── requirements.txt
├── README.md
│
└── project/
    │
    ├── agent.py
    │
    ├── db/
    │   ├── database.py
    │   ├── models.py
    │   └── transaction.py
    │
    ├── llm/
    │   └── providers.py
    │
    ├── prompts/
    │   ├── registry.py
    │   └── react_system.yaml
    │
    ├── rag/
    │   ├── schemas.py
    │   ├── loaders.py
    │   ├── chunker.py
    │   ├── embeddings.py
    │   ├── repository.py
    │   └── rag_service.py
    │
    ├── tools/
    │   ├── registry.py
    │   ├── tool_wrapper.py
    │   ├── basic_tools.py
    │   └── rag_tools.py
    │
    └── data/
        ├── sales.csv
        └── documents/
```

---

# Requirements

Recommended Python version:

```text
Python 3.10+
```

Supported:

```text
Python 3.9+
```

Required packages:

```text
requests
pydantic
pyyaml
jinja2
pandas
sqlalchemy
psycopg2-binary
pgvector
python-dotenv
sentence-transformers
pypdf
python-docx
```

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

---

# Virtual Environment Setup

Create virtual environment:

```bash
python3 -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

Verify:

```bash
which python3
```

Expected:

```text
.../react_csv_agent/.venv/bin/python3
```

---

# Ollama Setup

Install Ollama.

Verify:

```bash
curl http://localhost:11434/api/version
```

Pull model:

```bash
ollama pull llama3.1:8b
```

Run model:

```bash
ollama run llama3.1:8b
```

Configure agent:

```bash
export LOCAL_MODEL=llama3.1:8b
```

---

# Docker Setup

Verify Docker:

```bash
docker --version
docker compose version
```

The project uses:

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: document_analyst_db
    restart: unless-stopped
    environment:
      POSTGRES_USER: analyst
      POSTGRES_PASSWORD: analyst
      POSTGRES_DB: document_analyst
    ports:
      - "5432:5432"
```

Start PostgreSQL:

```bash
docker compose up -d
```

Verify:

```bash
docker ps
```

Expected container:

```text
document_analyst_db
```

---

# PostgreSQL + pgvector Setup

Connect:

```bash
docker exec -it document_analyst_db psql -U analyst -d document_analyst
```

Enable extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Verify:

```sql
SELECT extname FROM pg_extension;
```

Exit:

```sql
\q
```

---

# Create Database Tables

Run:

```bash
python3 create_tables.py
```

Expected:

```text
Database tables and pgvector index created successfully.
```

Verify tables:

```bash
docker exec -it document_analyst_db psql -U analyst -d document_analyst
```

Then:

```sql
\dt
```

Expected:

```text
documents
document_chunks
```

---

# Document Storage Model

## documents

Stores:

```text
id
filename
content
metadata
created_at
```

## document_chunks

Stores:

```text
id
document_id
content
chunk_index
embedding
```

Embeddings use:

```text
Vector(384)
```

---

# RAG Components

## DocumentLoader

File:

```text
project/rag/loaders.py
```

Supported formats:

* TXT
* PDF
* DOCX

---

## TextChunker

File:

```text
project/rag/chunker.py
```

Default settings:

```python
chunk_size = 800
chunk_overlap = 100
```

---

## EmbeddingService

File:

```text
project/rag/embeddings.py
```

Model:

```text
paraphrase-multilingual-MiniLM-L12-v2
```

Vector size:

```text
384 dimensions
```

---

## DocumentRepository

Responsibilities:

* Create documents
* Create chunks
* Store embeddings
* List documents
* Similarity search

---

## RAGService

Main methods:

```python
process_document(path)
search(query)
list_documents()
```

---

# Document Ingestion

Store documents in:

```text
project/data/documents/
```

Examples:

```bash
echo "Contractul se poate rezilia cu preaviz de 30 de zile." > project/data/documents/contract.txt

echo "Supplier: Mega Image. Invoice amount: 1250 EUR." > project/data/documents/invoice.txt

echo "Customers may request refunds within 14 days." > project/data/documents/policy.txt
```

Run ingestion:

```bash
python3 ingest_documents.py
```

Expected:

```text
Found 3 document(s).
SUCCESS ...
Ingestion completed.
```

---

# CSV Tools

File:

```text
project/tools/basic_tools.py
```

Available tools:

```text
calculator
list_data_files
read_file
read_csv
aggregate_csv
```

Example prompts:

```text
What files do I have uploaded locally?

Describe project/data/sales.csv

Group by region and sum quantity from project/data/sales.csv

How many products were sold in each region?
```

---

# RAG Tools

File:

```text
project/tools/rag_tools.py
```

Available tools:

```text
list_stored_documents
search_documents
```

Example prompts:

```text
What documents are stored?

Search in my documents: who is the supplier?

Search in my documents: what is the refund policy?

Search in my documents: what does the contract say about termination?
```

---

# Running the Agent

From project root:

```bash
source .venv/bin/activate

export LOCAL_MODEL=llama3.1:8b

python3 main.py
```

Expected:

```text
ReAct CSV Agent started. Type 'exit' to stop.
```

---

# Example RAG Workflow

1. Place documents in:

```text
project/data/documents
```

2. Run:

```bash
python3 ingest_documents.py
```

3. Start agent:

```bash
python3 main.py
```

4. Ask:

```text
What documents are stored?
```

5. Ask:

```text
Search in my documents: what is the termination notice?
```

6. Agent performs:

```text
search_documents
↓
pgvector similarity search
↓
retrieved chunks
↓
LLM answer
```

---

# Full Setup From Scratch

```bash
git clone <repository>

cd react_csv_agent

python3 -m venv .venv

source .venv/bin/activate

python3 -m pip install -r requirements.txt

docker compose up -d

python3 create_tables.py

python3 ingest_documents.py

export LOCAL_MODEL=llama3.1:8b

python3 main.py
```

---

# Useful Commands

Check Ollama:

```bash
curl http://localhost:11434/api/version
```

Check containers:

```bash
docker ps
```

Check database:

```bash
docker exec -it document_analyst_db psql -U analyst -d document_analyst
```

List documents:

```sql
SELECT id, filename FROM documents;
```

List chunks:

```sql
SELECT id, document_id, chunk_index FROM document_chunks;
```

Exit:

```sql
\q
```

---

# Technologies Used

* Python
* Ollama
* Llama 3.1
* PostgreSQL
* pgvector
* SQLAlchemy
* Sentence Transformers
* Pydantic
* Docker
* Jinja2
* Pandas

---

# Project Goal

The goal of this project is to demonstrate a complete local AI agent architecture combining:

* ReAct reasoning
* Tool calling
* CSV analytics
* RAG pipelines
* Vector databases
* Semantic search
* Local LLM inference

without relying on external cloud services.
