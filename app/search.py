import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "../chroma_db"

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = client.get_collection(
    name="knowledge_base"
)

while True:

    query = input("\nAsk a question: ")

    if query.lower() == "exit":
        break

    query_embedding = embedding_model.encode(
        query
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    print("\nTop Results:\n")

    for index, document in enumerate(results["documents"][0]):
        source = results["metadatas"][0][index]["source"]

        print("=" * 80)
        print(f"Source: {source}")
        print(document[:500])
        print()