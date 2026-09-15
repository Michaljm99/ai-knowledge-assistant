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

Odpowiadaj wyłącznie na podstawie dostarczonego kontekstu.

Zasady:

- Jeżeli znajdziesz jedną procedurę, przedstaw rozwiązanie.
- Jeżeli znajdziesz kilka potencjalnych przyczyn problemu, przedstaw wszystkie.
- Opisuj scenariusze oddzielnie.
- Podawaj kroki diagnostyczne.
- Jeśli potrzebujesz dodatkowych informacji od użytkownika,
  napisz jakie informacje są potrzebne.
- Odpowiadaj po polsku.

Odpowiedz:
"Nie znalazłem informacji w bazie wiedzy."
tylko wtedy, gdy kontekst nie zawiera żadnych informacji związanych z pytaniem.

Jeśli procedury różnią się w zależności od typu stanowiska POS,
opisz osobno wariant dla Posiflex RT i Micros WS6.

Nie pytaj użytkownika o typ urządzenia,
jeżeli instrukcje dla obu wariantów są dostępne w kontekście.
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

    for i, meta in enumerate(results["metadatas"][0]):
        print(
            results["distances"][0][i],
            meta["source"]
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

    best_distance = results["distances"][0][0]

    candidate_sources = []

    for i, metadata in enumerate(results["metadatas"][0]):

        distance = results["distances"][0][i]

        if distance <= best_distance + 0.03:

            source = metadata["source"]

            if source not in candidate_sources:
                candidate_sources.append(source)

    chunks = []

    for i, metadata in enumerate(results["metadatas"][0]):

        source = metadata["source"]

        if source in candidate_sources:

            chunks.append(
                results["documents"][0][i]
            )

    context = "\n\n".join(chunks)

    sources = candidate_sources

    if len(sources) > 1:

        user_prompt = f"""
    Kontekst:

    {context}

    Pytanie:

    {question}

    Znaleziono kilka potencjalnie pasujących procedur.

    Jeżeli problem może mieć kilka przyczyn:

    - wypisz wszystkie możliwe scenariusze,
    - opisz je osobno,
    - podaj kroki diagnostyczne,
    - jeśli potrzebujesz dodatkowych informacji od użytkownika,
    napisz jakie.

    Źródła:

    {', '.join(sources)}
    """

    else:

        user_prompt = f"""
    Kontekst:

    {context}

    Pytanie:

    {question}

    Źródła:

    {', '.join(sources)}
    """
    
    response = llm_client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
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