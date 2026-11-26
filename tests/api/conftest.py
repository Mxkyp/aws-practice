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
    body: dict | None  # None for an empty body (204)


def _response(status: int, raw: bytes) -> Response:
    return Response(status, json.loads(raw) if raw else None)


@pytest.fixture(scope="session")
def request_api():
    base = os.environ["API_URL"].rstrip("/")
    ctx = ssl.create_default_context(cafile=CA_FILE)

    def _request(method: str, path: str) -> Response:
        req = urllib.request.Request(base + path, method=method)
        try:
            with urllib.request.urlopen(req, context=ctx) as r:
                return _response(r.status, r.read())
        except urllib.error.HTTPError as e:  # 4xx/5xx still carry a JSON body
            return _response(e.code, e.read())

    return _request


@pytest.fixture(scope="session")
def get(request_api):
    return lambda path: request_api("GET", path)


@pytest.fixture(scope="session")
def delete(request_api):
    return lambda path: request_api("DELETE", path)


@pytest.fixture(scope="session")
def table():
    """The DynamoDB table itself, for tests that set up their own items.

    boto3 reads the emulator's endpoint_url and ca_bundle from AWS_CONFIG_FILE.
    """
    import boto3

    return boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
