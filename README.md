
# ReAct CSV + RAG Document Analyst Agent


#homework 3

# Homework 3 – Multi-Agent Data Reader with Typed State, Routing, Retry and RAG Integration

## Overview

Homework 3 extends the Data Reader and RAG system developed in Homework 2 into a multi-agent architecture inspired by LangGraph concepts.

The solution introduces:

* Typed shared state
* Node-based execution
* Supervisor agent
* Routing logic
* Retry and fallback mechanisms
* Multi-agent collaboration
* Integration with PostgreSQL + pgvector RAG search
* Local LLM execution through Ollama

The goal is to demonstrate how multiple specialized agents can collaborate using a shared state while maintaining a robust workflow capable of recovering from failures.

---

## Architecture

The system is composed of four agents:

### Supervisor Agent

Responsibilities:

* Receives the user request
* Decides which agent should execute next
* Routes the workflow using commands
* Controls the execution flow

### Retriever Agent

Responsibilities:

* Executes semantic search against PostgreSQL + pgvector
* Uses the existing RAG Service from Homework 2
* Retrieves the most relevant document chunks
* Stores results in the shared state

### Analyst Agent

Responsibilities:

* Reads retrieved document chunks
* Produces the final answer
* Updates the shared state with the response

### Fallback Agent

Responsibilities:

* Handles unexpected failures
* Implements retry logic
* Redirects execution when possible
* Returns controlled error messages if recovery fails

---

## Typed Shared State

The entire workflow shares a strongly typed state object containing:

* User question
* Current agent
* Conversation messages
* Retrieved document chunks
* Final answer
* Error information
* Retry count
* Metadata

Using a typed state guarantees consistency between all agents participating in the workflow.

---

## Technologies Used

* Python 3.9+
* Ollama
* Llama 3.1
* PostgreSQL
* pgvector
* SQLAlchemy
* Sentence Transformers
* Docker
* Pydantic

---

## Project Structure

```text
react_csv_agent/

├── project/
│   ├── graph_agent/
│   │   ├── state.py
│   │   ├── commands.py
│   │   ├── routing.py
│   │   ├── nodes.py
│   │   └── data_reader_graph.py
│   │
│   ├── rag/
│   │   ├── rag_service.py
│   │   ├── repository.py
│   │   ├── embeddings.py
│   │   ├── chunker.py
│   │   └── loaders.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   ├── transaction.py
│   │   └── models.py
│   │
│   ├── llm/
│   │   └── providers.py
│   │
│   └── tools/
│
├── project/data/documents/
│
├── docker-compose.yml
├── create_tables.py
├── ingest_documents.py
├── homework3_demo.py
├── main.py
└── requirements.txt
```

---

## Prerequisites

### 1. Docker Installed

Verify:

```bash
docker --version
docker compose version
```

### 2. Virtual Environment Activated

```bash
source .venv/bin/activate
```

Verify:

```bash
which python3
```

Expected output:

```text
.../react_csv_agent/.venv/bin/python3
```

### 3. Ollama Container Running

Verify:

```bash
docker ps
```

Expected container:

```text
local-ollama
```

### 4. PostgreSQL + pgvector Container Running

Verify:

```bash
docker ps
```

Expected container:

```text
document_analyst_db
```

---

## Initial Setup

### Start Docker Services

```bash
docker compose up -d
```

Verify:

```bash
docker ps
```

You should see:

```text
document_analyst_db
local-ollama
```

---

### Create Database Tables

Run once:

```bash
python3 create_tables.py
```

Expected:

```text
Database tables and pgvector index created successfully.
```

---

### Ingest Documents

Place documents inside:

```text
project/data/documents/
```

Then run:

```bash
python3 ingest_documents.py
```

Expected:

```text
Found X document(s)
SUCCESS | id=...
Ingestion completed.
```

The process:

1. Loads documents
2. Splits documents into chunks
3. Creates embeddings
4. Stores chunks in PostgreSQL
5. Creates vector representations for semantic search

---

## Running Homework 3

Execute:

```bash
python3 homework3_demo.py
```

Example question:

```text
Search in my documents: what is the termination notice?
```

Workflow:

1. Supervisor receives request
2. Supervisor routes to Retriever
3. Retriever performs semantic search
4. Retrieved chunks are stored in state
5. Analyst generates final answer
6. Answer returned to user

---

## Example Execution

Input:

```text
Search in my documents: what is the termination notice?
```

Retrieved document:

```text
Contractul se poate rezilia cu preaviz de 30 de zile.
```

Output:

```text
The contract states that it can be terminated with a 30-day notice.
```

---

## Error Handling

The solution implements a fallback strategy:

1. Detect execution failure
2. Increment retry counter
3. Retry retrieval once
4. If failure persists:

   * Generate controlled error
   * End workflow gracefully

This prevents workflow crashes and demonstrates resilient orchestration.

---

## Learning Objectives Demonstrated

This homework demonstrates:

* Typed State Management
* Multi-Agent Architecture
* Shared State Communication
* Supervisor Pattern
* Routing Logic
* Node-Based Execution
* Retry Mechanisms
* Fallback Handling
* RAG Integration
* Semantic Search
* Vector Databases
* PostgreSQL + pgvector
* Local LLM Execution
* AI Workflow Orchestration

---

## Conclusion

Homework 3 transforms the single-agent RAG Data Reader into a robust multi-agent system. The implementation demonstrates how specialized agents can collaborate through a typed shared state, while routing, retry mechanisms, and fallback handling provide a reliable foundation for more advanced orchestration workflows in future assignments.


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
