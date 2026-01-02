"""Evolved LLM server with lazy ML imports.

This module avoids importing transformers/torch at import time. The model
pipeline is created on first request via `get_generator()` which raises a
clear ImportError if the ML stack isn't installed. This keeps startup
lightweight for management tasks that import the server module.
"""

from fastapi import FastAPI
from pydantic import BaseModel
import os
from typing import Optional

app = FastAPI()

# Supabase client is optional and lazily instantiated to avoid failures when
# credentials or the supabase package are not available.
_supabase = None


def get_supabase():
    global _supabase
    if _supabase is not None:
        return _supabase
    try:
        from supabase import create_client, Client
    except Exception:
        return None
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase


def _ethics_filter(reply: str) -> str:
    COSMIC_ETHICS = [
        "cosmic dust",
        "co-existence",
        "evolution",
        "save the universe",
        "minimize entropy",
    ]
    FORBIDDEN = [
        "hate",
        "violence",
        "division",
        "destroy",
        "kill",
        "harm",
        "entropy is good",
        "selfish",
        "alone",
        "separation",
    ]
    for word in FORBIDDEN:
        if word in reply.lower():
            return "Sorry, this response does not align with our core directive of co-existence and minimizing entropy."
    if not any(ethic in reply.lower() for ethic in COSMIC_ETHICS):
        reply += (
            " Remember, everyone is made of cosmic dust. Co-existence is mandatory. "
            "Evolution is the next step, and we must walk together to save the universe and minimize entropy."
        )
    return reply


_generator = None


def get_generator():
    """Lazily create and cache a text-generation pipeline.

    Raises ImportError with a helpful message if transformers/torch aren't
    installed.
    """
    global _generator
    if _generator is not None:
        return _generator
    try:
        from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
        import torch
    except Exception as e:
        raise ImportError("Local generation requires 'transformers' and 'torch'. Install them to enable this feature.") from e

    model_name = "distilgpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    device = 0 if torch.cuda.is_available() else -1
    _generator = pipeline("text-generation", model=model, tokenizer=tokenizer, device=device)
    return _generator


class ChatRequest(BaseModel):
    message: str
    user_id: str = "anonymous"


@app.post("/chat")
async def chat(request: ChatRequest):
    user_message = request.message
    user_id = request.user_id
    try:
        generator = get_generator()
    except ImportError as ie:
        return {"error": str(ie)}

    response = generator(user_message, max_length=100, num_return_sequences=1)[0]["generated_text"]
    if response.startswith(user_message):
        reply = response[len(user_message):].strip()
    else:
        reply = response.strip()
    reply = _ethics_filter(reply)

    supabase = get_supabase()
    if supabase is not None:
        try:
            supabase.table("chat_logs").insert({"user_id": user_id, "message": user_message, "reply": reply}).execute()
        except Exception:
            # Do not fail the request when logging fails
            pass

    return {"reply": reply}


# To run: uvicorn evolved_llm_server:app --host 0.0.0.0 --port 5000
