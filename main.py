import os
import numpy as np
import httpx
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

AI_PIPE_TOKEN = os.getenv("AI_PIPE_TOKEN")
EMBEDDING_API_URL =  "https://aiproxy.sanand.workers.dev/openai/v1/embeddings"  # Replace with your actual AI Pipe endpoint
MODEL_NAME = "text-embedding-3-small"  # Replace if needed

app = FastAPI()

# Enable CORS (allow all origins, methods POST and OPTIONS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimilarityRequest(BaseModel):
    docs: list[str]
    query: str

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

async def get_embedding(text: str) -> list[float]:
    headers = {
        "Authorization": f"Bearer {AI_PIPE_TOKEN}",
        "Content-Type": "application/json"
    }
    json_body = {
        "model": MODEL_NAME,
        "input": text
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(EMBEDDING_API_URL, headers=headers, json=json_body)
        response.raise_for_status()
        data = response.json()
        # Assuming response contains: {"data": [{"embedding": [...]}, ...]}
        return data["data"][0]["embedding"]

@app.post("/similarity")
async def similarity(req: SimilarityRequest):
    # Get query embedding
    query_embedding = await get_embedding(req.query)

    # Get embeddings for all docs concurrently
    doc_embeddings = await asyncio.gather(*(get_embedding(doc) for doc in req.docs))

    # Compute cosine similarities
    sims = [cosine_similarity(np.array(query_embedding), np.array(doc_emb)) for doc_emb in doc_embeddings]

    # Get indices of top 3 most similar docs
    top_indices = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)[:3]

    # Prepare the top 3 matched documents
    top_docs = [req.docs[i] for i in top_indices]

    return {"matches": top_docs}
