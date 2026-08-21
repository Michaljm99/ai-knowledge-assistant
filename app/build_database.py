from pathlib import Path
import os
import re
import chromadb
from docx import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from datetime import datetime

# Configuration
DOCUMENTS_PATH = Path("../documents")
CHROMA_PATH = "../chroma_db"

# Embedding model
load_dotenv()
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL"
)
#print(EMBEDDING_MODEL)
embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


# ChromaDB
client = chromadb.PersistentClient(path=CHROMA_PATH)

try:
    client.delete_collection("knowledge_base")
except Exception:
    pass

collection = client.get_or_create_collection(
    name="knowledge_base"
)

# Text splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=300
)

def extract_date_from_filename(filename: str):

    match = re.search(
        r"(\d{4}-\d{2}-\d{2})",
        filename
    )

    if match:
        return match.group(1)

    return None

chunk_id = 0

for file in DOCUMENTS_PATH.glob("**/*"):

    try:

        if file.suffix.lower() == ".pdf":

            reader = PdfReader(file)

            text = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )

        elif file.suffix.lower() == ".docx":

            doc = Document(file)

            text = "\n".join(
                paragraph.text
                for paragraph in doc.paragraphs
            )

        else:
            continue

        chunks = splitter.split_text(text)

        for chunk in chunks:

            embedding = embedding_model.encode(
                f"passage: {chunk}"
            ).tolist()

            collection.add(
                ids=[str(chunk_id)],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[
                    {
                        "source": file.name,
                    }
                ]
            )

            chunk_id += 1

    except Exception as e:
        print(f"Error processing {file.name}: {e}")

print(f"Indexed {chunk_id} chunks")