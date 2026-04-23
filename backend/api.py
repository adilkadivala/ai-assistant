from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.assistant import process_user_prompt


class ChatRequest(BaseModel):
    message: str


app = FastAPI(title="Gmail + Calendar AI Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(payload: ChatRequest):
    return process_user_prompt(payload.message)
