
import os
import re

from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI
from google import genai

load_dotenv()


def quick_answer(question: str, passages: list[dict]) -> str:
    """Extract a basic answer locally as the final fallback."""

    if not passages:
        return "I couldn't find relevant information in this PDF."

    stop_words = {
        "what", "when", "where", "which", "who", "why", "how",
        "the", "is", "are", "was", "were", "a", "an", "and",
        "or", "of", "to", "in", "on", "for", "with", "does",
        "do", "can", "could", "explain", "tell", "me", "about",
        "please", "describe", "define", "give", "show"
    }

    def words(text):
        return set(re.findall(r"\b[a-zA-Z0-9]+\b", text.lower()))

    question_words = words(question) - stop_words
    candidates = []

    for passage in passages:
        sentences = re.split(
            r"(?<=[.!?])\s+",
            passage.get("text", "").strip()
        )

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_words = words(sentence)
            overlap = len(question_words & sentence_words)

            relevance = (
                overlap / len(question_words)
                if question_words else 0
            )

            candidates.append({
                "text": sentence,
                "page": passage.get("page", "?"),
                "overlap": overlap,
                "relevance": relevance,
                "passage_score": passage.get("score", 0),
            })

    candidates.sort(
        key=lambda item: (
            item["relevance"],
            item["passage_score"],
        ),
        reverse=True
    )

    selected = [
        item for item in candidates
        if item["overlap"] > 0
    ][:3]

    if selected:
        return "\n\n".join(
            f"{item['text']} (Page {item['page']})"
            for item in selected
        )

    best = passages[0]
    return (
        "The local fallback could not determine an exact answer. "
        f"Here is the closest retrieved passage (page {best.get('page', '?')}):\n\n"
        f"{best.get('text', '')}"
    )


def _build_prompt(question: str, passages: list[dict]) -> str:
    """Build a question-answering prompt from retrieved PDF passages."""

    context = "\n\n".join(
        f"[Page {item.get('page', '?')}] {item.get('text', '')}"
        for item in passages[:4]
    )

    return f"""Answer the user's question using the PDF passages below.

Instructions:
- Answer the exact question directly and clearly.
- Understand the meaning of the question; do not just match keywords.
- Use only information supported by the passages.
- Do not invent facts or claim information the PDF does not contain.
- Include page references when possible.
- If the passages do not contain the answer, say so.
- Use a concise answer unless more explanation is needed.

PDF passages:
{context}

Question: {question}

Answer:"""


def _error_summary(provider: str, exc: Exception, api_key: str) -> str:
    """Return a short diagnostic without exposing the API key."""

    message = str(exc)
    if api_key:
        message = message.replace(api_key, "[hidden]")

    # Keep diagnostics short.
    message = " ".join(message.split())[:220]
    return f"{provider}: {type(exc).__name__}: {message}"


def answer_question(
    question: str,
    passages: list[dict]
) -> str:
    """
    Try Groq, then OpenAI, then Gemini.
    Use the local PDF answer only if all providers fail.
    """

    if not passages:
        return "I couldn't find relevant information in this PDF."

    prompt = _build_prompt(question, passages)
    failures = []

    # 1. GROQ — primary provider
    api_key = os.getenv("GROQ_API_KEY")

    if api_key:
        try:
            client = Groq(
                api_key=api_key,
                timeout=20.0,
                max_retries=0,
            )

            response = client.chat.completions.create(
                model=os.getenv(
                    "GROQ_MODEL",
                    "openai/gpt-oss-20b"
                ),
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precise PDF question-answering "
                            "assistant. Ground every answer in the "
                            "provided document passages."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
            )

            answer = response.choices[0].message.content

            if answer and answer.strip():
                return f"{answer.strip()}\n\n— Answered by Groq"

            failures.append("Groq returned an empty answer.")

        except Exception as exc:
            failures.append(_error_summary("Groq", exc, api_key))
    else:
        failures.append("Groq skipped: GROQ_API_KEY is missing.")

    # 2. OPENAI — first fallback
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        try:
            client = OpenAI(
                api_key=api_key,
                timeout=20.0,
                max_retries=0,
            )

            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precise PDF question-answering "
                            "assistant. Ground every answer in the "
                            "provided document passages."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
            )

            answer = response.choices[0].message.content

            if answer and answer.strip():
                return f"{answer.strip()}\n\n— Answered by OpenAI"

            failures.append("OpenAI returned an empty answer.")

        except Exception as exc:
            failures.append(_error_summary("OpenAI", exc, api_key))
    else:
        failures.append("OpenAI skipped: OPENAI_API_KEY is missing.")

    # 3. GEMINI — second fallback
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            client = genai.Client(
                api_key=api_key,
                http_options={"timeout": 20000},
            )

            response = client.models.generate_content(
                model=os.getenv(
                    "GEMINI_MODEL",
                    "gemini-2.5-flash"
                ),
                contents=prompt,
                config={"max_output_tokens": 500},
            )

            answer = response.text

            if answer and answer.strip():
                return f"{answer.strip()}\n\n— Answered by Gemini"

            failures.append("Gemini returned an empty answer.")

        except Exception as exc:
            failures.append(_error_summary("Gemini", exc, api_key))
    else:
        failures.append("Gemini skipped: GEMINI_API_KEY is missing.")

    # 4. FINAL FALLBACK — local extraction
    local_result = quick_answer(question, passages)

    return (
        f"{local_result}\n\n"
        "---\n"
        "**Local fallback used:** All AI providers failed.\n\n"
        "**Provider diagnostics:**\n"
        + "\n".join(f"- {failure}" for failure in failures)
    )
