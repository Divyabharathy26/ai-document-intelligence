
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash-lite",
)


def generate_ai_response(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("Gemini API key is not configured.")

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text.strip()

   except errors.APIError as exc:
    raise RuntimeError(
        f"Gemini API request failed with status "
        f"{getattr(exc, 'code', 'unknown')}: {exc}"
    ) from exc
