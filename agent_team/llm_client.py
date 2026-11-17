
import os
import re
import time
import threading

from dotenv import load_dotenv
from groq import Groq, RateLimitError


# --------------------------------------------------
# 1. LOAD CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

API_KEY = os.getenv("GROQ_API_KEY")

AGENT_MODEL = os.getenv(
    "GROQ_AGENT_MODEL",
    os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
)

CODEGEN_MODEL = os.getenv(
    "GROQ_CODEGEN_MODEL",
    AGENT_MODEL
)


def get_token_limit(env_name: str, default: str) -> int:
    try:
        value = int(os.getenv(env_name, default))
    except ValueError as exc:
        raise RuntimeError(
            f"{env_name} must be an integer."
        ) from exc

    if value < 1:
        raise RuntimeError(
            f"{env_name} must be greater than zero."
        )

    return value


AGENT_MAX_COMPLETION_TOKENS = get_token_limit(
    "GROQ_AGENT_MAX_COMPLETION_TOKENS",
    "5000"
)

CODEGEN_MAX_COMPLETION_TOKENS = get_token_limit(
    "GROQ_CODEGEN_MAX_COMPLETION_TOKENS",
    "800"
)

MIN_REQUEST_INTERVAL = float(
    os.getenv("GROQ_MIN_REQUEST_INTERVAL", "2")
)

MAX_RETRIES = get_token_limit(
    "GROQ_MAX_RETRIES",
    "3"
)


if not API_KEY:
    raise RuntimeError("GROQ_API_KEY is missing from .env.")


client = Groq(
    api_key=API_KEY,
    max_retries=0,
)


# --------------------------------------------------
# 2. LLM ERRORS
# --------------------------------------------------

class LLMResponseError(RuntimeError):
    """Raised when an LLM response is unusable."""


# --------------------------------------------------
# 3. REQUEST PACING
# --------------------------------------------------

_request_lock = threading.Lock()
_last_request_time = 0.0


def wait_for_request_slot():
    """
    Space requests to avoid bursts.

    This controls request frequency, not token quotas.
    """

    global _last_request_time

    with _request_lock:

        now = time.monotonic()

        elapsed = now - _last_request_time

        wait_time = MIN_REQUEST_INTERVAL - elapsed

        if wait_time > 0:
            print(
                f"Request pacing: waiting "
                f"{wait_time:.1f} seconds..."
            )
            time.sleep(wait_time)

        _last_request_time = time.monotonic()


# --------------------------------------------------
# 4. RATE LIMIT RETRY HANDLING
# --------------------------------------------------

def get_retry_delay(error, attempt: int) -> float:
    """
    Extract a retry delay from Groq response headers.

    Falls back to exponential backoff.
    """

    response = getattr(error, "response", None)

    if response is not None:
        headers = response.headers

        retry_after = headers.get("retry-after")

        if retry_after:
            try:
                return max(1.0, float(retry_after))
            except ValueError:
                pass

        reset_tokens = headers.get(
            "x-ratelimit-reset-tokens"
        )

        if reset_tokens:
            match = re.fullmatch(
                r"(?:(\d+)m)?(?:(\d+(?:\.\d+)?)s)?",
                reset_tokens.strip()
            )

            if match:
                minutes = float(match.group(1) or 0)
                seconds = float(match.group(2) or 0)

                delay = minutes * 60 + seconds

                if delay > 0:
                    return delay

    return min(2 ** attempt, 30)


# --------------------------------------------------
# 5. CENTRALIZED LLM REQUEST
# --------------------------------------------------

def ask_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = AGENT_MODEL,
    max_completion_tokens: int = AGENT_MAX_COMPLETION_TOKENS,
) -> str:
    """
    Send a request to Groq with centralized
    request pacing and temporary rate-limit retries.
    """

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    for attempt in range(MAX_RETRIES + 1):

        wait_for_request_slot()

        try:

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                max_completion_tokens=max_completion_tokens,
            )

            break

        except RateLimitError as exc:

            if attempt >= MAX_RETRIES:
                raise LLMResponseError(
                    f"{model} exceeded its Groq rate limit "
                    f"after {MAX_RETRIES} retries. "
                    "Check the model's available quota."
                ) from exc

            delay = get_retry_delay(exc, attempt)

            print(
                f"\nGroq rate limit reached for {model}."
            )
            print(
                f"Retrying in {delay:.1f} seconds "
                f"(attempt {attempt + 1}/{MAX_RETRIES})..."
            )

            time.sleep(delay)

    if not response.choices:
        raise LLMResponseError(
            f"{model} returned no response choices."
        )

    choice = response.choices[0]

    content = choice.message.content or ""
    finish_reason = choice.finish_reason

    print(f"\nLLM model: {model}")
    print(f"LLM finish reason: {finish_reason}")

    if response.usage:

        print(
            "LLM token usage:",
            f"prompt={response.usage.prompt_tokens},",
            f"completion={response.usage.completion_tokens},",
            f"total={response.usage.total_tokens}",
        )

    if finish_reason == "length":
        raise LLMResponseError(
            f"{model} reached its completion-token limit "
            f"({max_completion_tokens}). "
            "The response is incomplete. "
            "Reduce the generation task size."
        )

    if not content.strip():
        raise LLMResponseError(
            f"{model} returned an empty response."
        )

    return content.strip()


# --------------------------------------------------
# 6. CONFIGURATION CHECK
# --------------------------------------------------

if __name__ == "__main__":

    print("Developer Model:", AGENT_MODEL)
    print(
        "Developer Token Limit:",
        AGENT_MAX_COMPLETION_TOKENS
    )

    print("Code Generation Model:", CODEGEN_MODEL)
    print(
        "Code Generation Token Limit:",
        CODEGEN_MAX_COMPLETION_TOKENS
    )

    print(
        "Minimum Request Interval:",
        MIN_REQUEST_INTERVAL
    )

    print("Maximum Retries:", MAX_RETRIES)
