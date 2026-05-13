"""Graph client unit tests — exercise the retry/throttle paths against a mock transport."""

from __future__ import annotations

from collections.abc import AsyncIterator

import httpx
import pytest

from app.graph.client import GraphClient, GraphFatalError, GraphPermissionError


async def _token(_tenant: str) -> str:
    return "fake-token"


def _make_client(
    responses: list[httpx.Response],
    *,
    capture: list[httpx.Request] | None = None,
) -> GraphClient:
    iter_responses = iter(responses)

    def _handler(request: httpx.Request) -> httpx.Response:
        if capture is not None:
            capture.append(request)
        try:
            return next(iter_responses)
        except StopIteration as exc:
            raise AssertionError("ran out of mock responses") from exc

    transport = httpx.MockTransport(_handler)
    http = httpx.AsyncClient(transport=transport, timeout=5.0)
    return GraphClient(_token, client=http)


@pytest.mark.asyncio
async def test_get_returns_ok() -> None:
    gc = _make_client([httpx.Response(200, json={"value": [{"id": "1"}]})])
    r = await gc.request("tenant", "GET", "/users")
    assert r.status_code == 200
    assert gc.metrics.requests == 1


@pytest.mark.asyncio
async def test_429_retry_after_then_success(monkeypatch: pytest.MonkeyPatch) -> None:
    import asyncio

    sleeps: list[float] = []

    async def _no_sleep(s: float) -> None:
        sleeps.append(s)

    monkeypatch.setattr(asyncio, "sleep", _no_sleep)

    gc = _make_client(
        [
            httpx.Response(429, headers={"Retry-After": "2"}, json={}),
            httpx.Response(200, json={"value": []}),
        ]
    )
    r = await gc.request("t", "GET", "/x")
    assert r.status_code == 200
    assert gc.metrics.throttled == 1
    assert sleeps == [2.0]


@pytest.mark.asyncio
async def test_5xx_then_success(monkeypatch: pytest.MonkeyPatch) -> None:
    import asyncio

    async def _no_sleep(_s: float) -> None:
        return None

    monkeypatch.setattr(asyncio, "sleep", _no_sleep)
    gc = _make_client(
        [
            httpx.Response(503, json={}),
            httpx.Response(200, json={"value": []}),
        ]
    )
    r = await gc.request("t", "GET", "/x")
    assert r.status_code == 200
    assert gc.metrics.retries == 1


@pytest.mark.asyncio
async def test_403_raises_permission_error() -> None:
    gc = _make_client([httpx.Response(403, text="forbidden")])
    with pytest.raises(GraphPermissionError):
        await gc.request("t", "GET", "/x")


@pytest.mark.asyncio
async def test_400_raises_fatal() -> None:
    gc = _make_client([httpx.Response(400, text="bad")])
    with pytest.raises(GraphFatalError):
        await gc.request("t", "GET", "/x")


@pytest.mark.asyncio
async def test_get_all_follows_next_link() -> None:
    page2_url = "https://graph.microsoft.com/v1.0/users?$skiptoken=abc"
    gc = _make_client(
        [
            httpx.Response(
                200,
                json={
                    "value": [{"id": "1"}, {"id": "2"}],
                    "@odata.nextLink": page2_url,
                },
            ),
            httpx.Response(200, json={"value": [{"id": "3"}]}),
        ]
    )

    items: list[dict] = []
    async for item in gc.get_all("t", "/users"):
        items.append(item)
    assert [i["id"] for i in items] == ["1", "2", "3"]


_ = AsyncIterator  # silence unused
