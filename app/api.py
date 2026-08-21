import os

from fastapi import Header, HTTPException
from dotenv import load_dotenv
from pathlib import Path
from services.reindex_service import rebuild_knowledge_base
from fastapi import FastAPI
from pydantic import BaseModel
from services.knowledge_service import (
    ask_knowledge_base,
    MODEL,
    get_collection
)

load_dotenv()

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

app = FastAPI(
    title="IT AI Assistant API"
)


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/health")
def health():

    try:

        get_collection().count()

        return {
            "status": "ok",
            "service": "IT AI Assistant",
            "model": MODEL,
            "knowledge_base": "available"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


@app.post("/ask", response_model=QuestionResponse)
def ask(request: QuestionRequest):

    result = ask_knowledge_base(
        request.question
    )

    return QuestionResponse(
        answer=result["answer"],
        sources=result["sources"]
    )

@app.post("/reindex")
def reindex(
    x_api_key: str = Header(default="")
):

    if x_api_key != ADMIN_API_KEY:

        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    return rebuild_knowledge_base()