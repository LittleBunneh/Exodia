
# EDI API Server using local LLM
from fastapi import FastAPI
from pydantic import BaseModel
from edi_minimal_llm import generate

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 128

@app.post("/chat")
def chat(request: ChatRequest):
    response = generate(request.prompt, max_new_tokens=request.max_new_tokens)
    return {"response": response}