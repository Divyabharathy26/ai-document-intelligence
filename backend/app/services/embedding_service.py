
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "gemini-embedding-2",
)


def generate_embedding(text: str) -> list[float]:
    """Convert text into a semantic embedding vector."""

    if not text or not text.strip():
        raise ValueError("Text must not be empty.")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("Gemini API key is not configured.")

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config={"output_dimensionality": 768},
        )

        if not response.embeddings:
            raise RuntimeError(
                "Gemini returned no embedding."
            )

        values = response.embeddings[0].values

        if not values:
            raise RuntimeError(
                "Gemini returned an empty embedding."
            )

        return [float(value) for value in values]

    except errors.APIError as exc:
        raise RuntimeError(
            "The embedding service could not process the request. "
            "Check model access and API quota."
        ) from exc
