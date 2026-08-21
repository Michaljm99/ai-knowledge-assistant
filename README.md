# AI Knowledge Assistant

AI Knowledge Assistant is a Retrieval Augmented Generation (RAG) solution designed to provide fast and accurate answers based on internal company documentation.

The system allows employees to ask questions in natural language and receive answers generated from company knowledge stored in PDF and DOCX documents.

---

# How It Works

The system uses semantic vector search.

When a user asks a question:

1. The question is converted into a vector (embedding)
2. ChromaDB performs semantic similarity search
3. The most relevant document fragments are retrieved
4. Gemini generates an answer using the retrieved context
5. The answer and source document are returned

---

# Architecture

```text
PDF / DOCX Documents
        │
        ▼
Document Parsing
        │
        ▼
Text Chunking
        │
        ▼
Embeddings (multilingual-e5-base)
        │
        ▼
ChromaDB Vector Database
        │
        ▼
Semantic Search
        │
        ▼
Google Gemini 2.5 Flash
        │
        ▼
FastAPI
        │
        ▼
REST API
```

---

# Technology Stack

## Backend

- Python
- FastAPI

## AI

- Google Gemini 2.5 Flash
- OpenRouter

## Vector Search

- ChromaDB
- intfloat/multilingual-e5-base

## Supported Documents

- PDF
- DOCX

---

# Features

## Semantic Search

The system searches by meaning rather than exact keywords.

Examples:

```text
paragon ↔ rachunek
POS ↔ kasa
tablet ↔ iPad
```

## Context-Aware Answers

Answers are generated exclusively from company documentation.

## Source Tracking

Every answer includes the document used to generate the response.

## Administrative Reindex

Knowledge base can be rebuilt through a protected API endpoint.

## Logging

User questions and document sources are automatically logged.

---

# Project Structure

```text
AI_Knowledge_Assistant
│
├── app
│   ├── api.py
│   ├── build_database.py
│   └── services
│       ├── knowledge_service.py
│       └── reindex_service.py
│
├── documents
│
├── chroma_db
│
├── logs
│   └── questions.csv
│
├── .env
│
└── requirements.txt
```

---

# Requirements

- Python 3.11+
- OpenRouter API Key

---

# Installation

Create a virtual environment:

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Configuration

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_api_key
MODEL=google/gemini-2.5-flash
EMBEDDING_MODEL=intfloat/multilingual-e5-base
ADMIN_API_KEY=your_admin_key
```

---

# Adding Documents

Place documents inside:

```text
documents/
```

Subfolders are supported.

Example:

```text
documents/
├── IT
│   ├── POS
│   └── Printers
│
├── Operations
│
└── HR
```

---

# Building the Knowledge Base

Run:

```bash
python build_database.py
```

Example output:

```text
Indexed 347 chunks
```

---

# Running the API

Start FastAPI:

```bash
python -m uvicorn api:app --reload
```

API documentation:

```text
http://localhost:8000/docs
```

---

# API Endpoints

## Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "service": "IT AI Assistant",
  "model": "google/gemini-2.5-flash",
  "knowledge_base": "available"
}
```

---

## Ask Question

```http
POST /ask
```

Request:

```json
{
  "question": "Jak znaleźć numer seryjny iPada?"
}
```

Response:

```json
{
  "answer": "Numer seryjny iPada znajduje się w Ustawienia > Ogólne > To urządzenie.",
  "sources": [
    "Gdzie znaleźć numer seryjny iPad.docx"
  ]
}
```

---

## Reindex Knowledge Base

```http
POST /reindex
```

Headers:

```http
x-api-key: YOUR_ADMIN_API_KEY
```

Response:

```json
{
  "status": "success",
  "message": "Knowledge base rebuilt successfully"
}
```

---

# Logging

Questions are stored in:

```text
logs/questions.csv
```

Example:

```csv
timestamp;question;sources
2026-08-20T18:25:12;Jak znaleźć numer seryjny iPada?;Gdzie znaleźć numer seryjny iPad.docx
```

---

# Current Status

## Completed

✅ FastAPI API

✅ ChromaDB vector database

✅ Semantic vector search

✅ OpenRouter integration

✅ Gemini 2.5 Flash integration

✅ Knowledge base rebuild endpoint

✅ Question logging

✅ Swagger documentation

✅ Support for PDF and DOCX

✅ Subfolder document indexing

---

# Roadmap

## Phase 2

- HALO integration
- Statistics endpoint
- Usage analytics

## Phase 3

- Feedback mechanism
- Role-based access control
- Automatic document classification

---

# Author

Michal Matuszczak
