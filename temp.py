# save as app.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

knowledge_base = {
    "What does the author affectionately call the => syntax?": {
        "answer": "fat arrow",
        "sources": "https://github.com/basarat/typescript-book/blob/master/docs/functions.md"
    },
    "Which operator converts any value into an explicit boolean?": {
        "answer": "!!",
        "sources": "https://github.com/basarat/typescript-book/blob/master/docs/boolean.md"
    }
}

@app.get("/search")
def search(q: str = Query(...)):
    result = knowledge_base.get(q)
    if result:
        return result
    return {"answer": "Sorry, I don't know the answer to that question.", "sources": ""}

# run with:
# uvicorn app:app --reload
