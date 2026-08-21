from pathlib import Path
from pypdf import PdfReader
from docx import Document

DOCS_PATH = Path("../documents")

documents = []

for file in DOCS_PATH.glob("**/*"):
    try:
        if file.suffix.lower() == ".pdf":
            reader = PdfReader(file)

            text = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )

            documents.append({
                "filename": file.name,
                "content": text
            })

        elif file.suffix.lower() == ".docx":
            doc = Document(file)

            text = "\n".join(
                p.text for p in doc.paragraphs
            )

            documents.append({
                "filename": file.name,
                "content": text
            })

    except Exception as e:
        print(f"Error processing {file}: {e}")

print(f"Loaded {len(documents)} documents")

for doc in documents[:5]:
    print("\n----------------")
    print(doc["filename"])
    print(doc["content"][:300])