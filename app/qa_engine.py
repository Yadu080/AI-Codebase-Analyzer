import os

from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_client():
    # Built lazily so a missing GROQ_API_KEY fails on first use, not at
    # import time (which would otherwise crash the whole API on startup).
    global _client
    if _client is None:
        from groq import Groq

        _client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=30.0)
    return _client


def generate_answer(question, retrieved_chunks):
    context = "\n\n".join(
        f"File: {c['file_path']}\n{c['chunk']}" for c in retrieved_chunks
    )

    prompt = f"""
You are a senior software engineer analyzing a GitHub repository.

Code Context:
{context}

Question:
{question}

Explain clearly which file or module handles this functionality.
"""

    try:
        completion = _get_client().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
    except Exception as exc:
        raise RuntimeError(f"LLM request failed: {exc}") from exc

    return completion.choices[0].message.content
