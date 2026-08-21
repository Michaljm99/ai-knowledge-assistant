import os
import csv

from datetime import datetime
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer


load_dotenv()

MODEL = os.getenv("MODEL")
API_KEY = os.getenv("OPENROUTER_API_KEY")

BASE_DIR = Path(__file__).resolve().parent.parent.parent


LOG_FILE = BASE_DIR / "logs" / "questions.csv"

LOG_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

llm_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL"
)

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


db_client = chromadb.PersistentClient(
    path="../chroma_db"
)

def get_collection():
    return db_client.get_collection(
        name="knowledge_base"
    )

SYSTEM_PROMPT = """
Jesteś asystentem IT.

Odpowiadaj wyłącznie na podstawie przekazanego kontekstu.

Jeżeli kontekst zawiera odpowiedź:
udziel odpowiedzi.

Jeżeli nie:
odpowiedz dokładnie:
Nie znalazłem informacji w bazie wiedzy.

Odpowiadaj po polsku.
"""


def log_question(question, sources):

    file_exists = LOG_FILE.exists()

    with open(
        LOG_FILE,
        mode="a",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(
            file,
            delimiter=";"
        )

        if not file_exists:
            writer.writerow([
                "timestamp",
                "question",
                "sources"
            ])

        writer.writerow([
            datetime.now().isoformat(),
            question,
            "; ".join(sources)
        ])


def ask_knowledge_base(question: str):

    query_embedding = embedding_model.encode(
        f"query: {question}"
    ).tolist()

    collection = get_collection()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=10,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    if (
        not results["documents"]
        or not results["documents"][0]
    ):
        return {
            "answer": "Nie znaleziono informacji w bazie wiedzy.",
            "sources": []
        }

    best_distance = results["distances"][0][0]

    if best_distance > 0.8:

        log_question(
            question=question,
            sources=[]
        )

        return {
            "answer": "Nie znalazłem informacji w bazie wiedzy.",
            "sources": []
        }

    best_source = results["metadatas"][0][0]["source"]

    chunks = []

    for i, metadata in enumerate(results["metadatas"][0]):

        if metadata["source"] == best_source:
            chunks.append(
                results["documents"][0][i]
            )

    context = "\n\n".join(chunks)

    sources = [best_source]

    response = llm_client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""
Kontekst:

{context}

Pytanie:

{question}

Źródło:

{best_source}
"""
            }
        ]
    )

    answer = response.choices[0].message.content

    log_question(
        question=question,
        sources=sources
    )

    return {
        "answer": answer,
        "sources": sources
    }