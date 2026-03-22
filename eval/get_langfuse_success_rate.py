import os
from pathlib import Path

from dotenv import load_dotenv
from langfuse import Langfuse

LANGFUSE_MAX_PAGE_SIZE = 100
DEFAULT_TRACE_LIMIT = 1000
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_PATH = PROJECT_ROOT / ".env"


def load_client() -> Langfuse:
    load_dotenv(dotenv_path=DEFAULT_ENV_PATH)

    base_url = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL")
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")

    if not public_key or not secret_key:
        raise ValueError("Missing LANGFUSE_PUBLIC_KEY or LANGFUSE_SECRET_KEY")

    if not base_url:
        raise ValueError("Missing LANGFUSE_HOST or LANGFUSE_BASE_URL")

    return Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        base_url=base_url,
        host=base_url,
        tracing_enabled=False,
    )


def list_traces(client: Langfuse, limit: int = DEFAULT_TRACE_LIMIT):
    remaining = limit
    current_page = 1
    all_traces = []

    while remaining > 0:
        page_limit = min(remaining, LANGFUSE_MAX_PAGE_SIZE)
        response = client.api.trace.list(
            page=current_page,
            limit=page_limit,
            order_by="timestamp.desc",
        )

        batch = response.data
        all_traces.extend(batch)
        remaining -= len(batch)

        if len(batch) < page_limit:
            break

        current_page += 1

    return all_traces


def is_successful(trace) -> bool:
    output = getattr(trace, "output", None)

    if isinstance(output, dict):
        valid = output.get("valid")
        if isinstance(valid, bool):
            return valid

    return False


def compute_success_rate(traces) -> float:
    if not traces:
        return 0.0

    successful_traces = sum(1 for trace in traces if is_successful(trace))
    return successful_traces / len(traces)


def main():
    client = load_client()
    traces = list_traces(client)
    success_rate = compute_success_rate(traces)
    print(f"Success rate: {float(success_rate)}")


if __name__ == "__main__":
    main()
