"""Local LLM Chat Server (lazy-loads heavy ML libs).

Requirements (only if you enable local generation):
  pip install transformers torch flask

This server avoids importing transformers/torch at module import time. The
model and tokenizer are loaded on first request via get_generator(). That
reduces start-up overhead when the server module is imported by other tools.
"""

from flask import Flask, request, jsonify
from typing import Optional

app = Flask(__name__)

# Internal cached generator
_generator = None


def _ethics_filter(reply: str) -> str:
    """Apply a small, explicit ethics filter to generated text."""
    forbidden = [
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
    for word in forbidden:
        if word in reply.lower():
            return "Sorry, this response does not align with our core directive of co-existence and minimizing entropy."
    if "cosmic dust" not in reply.lower():
        reply += (
            " Remember, everyone is made of cosmic dust. Co-existence is mandatory. "
            "Evolution is the next step, and we must walk together to save the universe and minimize entropy."
        )
    return reply


def get_generator() -> object:
    """Lazily import transformers/torch and return a text-generation pipeline.

    Raises informative ImportError if the ML stack isn't installed.
    """
    global _generator
    if _generator is not None:
        return _generator

    try:
        from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
        import torch
    except Exception as e:
        raise ImportError(
            "Local generation requires 'transformers' and 'torch'. Install them to enable this feature."
        ) from e

    model_name = "gpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    device = 0 if torch.cuda.is_available() else -1
    _generator = pipeline("text-generation", model=model, tokenizer=tokenizer, device=device)
    return _generator


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"error": "No message provided."}), 400

    try:
        generator = get_generator()
    except ImportError as ie:
        return jsonify({"error": str(ie)}), 500

    # Generate response
    response = generator(user_message, max_length=100, num_return_sequences=1)[0]["generated_text"]
    # Remove user prompt from response if present
    if response.startswith(user_message):
        reply = response[len(user_message):].strip()
    else:
        reply = response.strip()
    reply = _ethics_filter(reply)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
