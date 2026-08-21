import os

import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer

load_dotenv()

MODEL = os.getenv("MODEL")
API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

db_client = chromadb.PersistentClient(
    path="../chroma_db"
)

collection = db_client.get_collection(
    name="knowledge_base"
)

SYSTEM_PROMPT = """
You are an IT Knowledge Assistant.

Rules:
- Always answer in Polish.
- Use only information from context.
- If information does not exist in context say:
  'Nie znalazłem informacji w bazie wiedzy.'
- At the end add section:

Źródła:
- document_name
"""

while True:

    question = input("\nQuestion: ")

    if question.lower() == "exit":
        break

    query_embedding = embedding_model.encode(
        question
    ).tolist()

    results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
    include=[
        "documents",
        "metadatas",
        "distances"
    ]
    )
    best_distance = results["distances"][0][0]

#    print(f"\nDistance: {best_distance:.4f}")

    if best_distance > 1.2:
        print("\nNie znalazłem informacji w bazie wiedzy.")
        continue
    best_distance = results["distances"][0][0]

#   print(f"\nSimilarity score: {best_distance}")

    if best_distance > 1.2:
        print("\nNie znalazłem informacji w bazie wiedzy.")
        continue

    context = "\n\n".join(
        results["documents"][0]
    )

    sources = list({
        item["source"]
        for item in results["metadatas"][0]
    })

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""
Context:

{context}

Question:

{question}

Sources:

{', '.join(sources)}
"""
            }
        ]
    )

    print("\n" + "=" * 80)
    print(response.choices[0].message.content)
    print("=" * 80)