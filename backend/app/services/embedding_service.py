
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "gemini-embedding-2",
)

BATCH_SIZE = 16


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple texts in batches."""

    if not texts:
        raise ValueError("At least one text is required.")

    if any(not text or not text.strip() for text in texts):
        raise ValueError("Texts must not be empty.")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("Gemini API key is not configured.")

    client = genai.Client(api_key=api_key)
    all_embeddings: list[list[float]] = []

    try:
        for start in range(0, len(texts), BATCH_SIZE):
            batch = texts[start:start + BATCH_SIZE]

            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=batch,
                config={"output_dimensionality": 768},
            )

            if (
                not response.embeddings
                or len(response.embeddings) != len(batch)
            ):
                raise RuntimeError(
                    "Gemini returned an unexpected number of embeddings."
                )

            for item in response.embeddings:
                if not item.values:
                    raise RuntimeError(
                        "Gemini returned an empty embedding."
                    )

                all_embeddings.append(
                    [float(value) for value in item.values]
                )

    except errors.APIError as exc:
        raise RuntimeError(
            "The embedding service could not process the request. "
            "Check model access and API quota."
        ) from exc

    return all_embeddings


def generate_embedding(text: str) -> list[float]:
    """Generate an embedding for a single text."""

    return generate_embeddings([text])[0]
