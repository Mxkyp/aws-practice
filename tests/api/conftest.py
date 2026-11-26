"""HTTP tests against the deployed API on aws-emulator.

They need infra applied, code deployed and seed data loaded (`poe e2e` does
all of that). The base URL comes from API_URL, which `poe test-api` fills
from `terraform output api_invoke_url`.
"""

import json
import os
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import pytest

# The emulator serves HTTPS with its own CA, written next to its config.
CA_FILE = Path(os.environ["AWS_CONFIG_FILE"]).parent / "ca.pem"


@dataclass
class Response:
    status: int
    body: dict


@pytest.fixture(scope="session")
def get():
    base = os.environ["API_URL"].rstrip("/")
    ctx = ssl.create_default_context(cafile=CA_FILE)

    def _get(path: str) -> Response:
        try:
            with urllib.request.urlopen(base + path, context=ctx) as r:
                return Response(r.status, json.load(r))
        except urllib.error.HTTPError as e:  # 4xx/5xx still carry a JSON body
            return Response(e.code, json.load(e))

    return _get
