import os
import sys
import pytest

try:
    from pytest_socket import disable_socket, enable_socket
except Exception:  # plugin missing; tests will not block sockets
    disable_socket = lambda *a, **k: None  # type: ignore
    enable_socket = lambda *a, **k: None  # type: ignore

# Ensure LLM backend uses a placeholder in tests to avoid network calls
os.environ.setdefault("NEXUS_LLM_BACKEND", "placeholder")


@pytest.fixture(autouse=True)
def _socket_policy():
    """Default socket policy for tests.

    - On Windows, do NOT block sockets globally (Starlette TestClient relies on socketpair).
    - On POSIX (Linux/macOS), block sockets by default to keep tests hermetic.
    Individual tests can re-enable using `enable_socket()` when truly needed.
    """
    if sys.platform.startswith("win"):
        # Allow sockets on Windows to avoid event loop/socketpair issues
        yield
    else:
        disable_socket()
        try:
            yield
        finally:
            enable_socket()


@pytest.fixture()
def http_responses():
    """responses-based mock for requests library users."""
    import responses as _responses

    with _responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture()
def respx_mock():
    """respx-based mock for httpx users."""
    import respx as _respx

    with _respx.mock as mock:
        yield mock

