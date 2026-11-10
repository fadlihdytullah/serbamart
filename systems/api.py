import json
import os
import random
import time
from collections import deque
from datetime import date
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse

DATA = Path(os.environ.get("SERBAMART_DATA", "data"))
API_KEY = os.environ.get("SERBAMART_API_KEY", "serbamart-dev-key")
RATE_LIMIT = int(os.environ.get("SERBAMART_RATE_LIMIT", "60"))
FLAKY = float(os.environ.get("SERBAMART_FLAKY", "0"))

app = FastAPI(
    title="Serbamart Online Store API",
    version="1.0.0",
    description=(
        "Orders from the Serbamart web shop, built by the Serbamart dev team. "
        "Send your key in the `X-API-Key` header. "
        f"Each key may send {RATE_LIMIT} requests per minute; over that the API answers 429 with `Retry-After`. "
        "`created_at` is UTC."
    ),
)

recent: dict[str, deque] = {}


@app.middleware("http")
async def guard(request: Request, call_next):
    if request.url.path in ("/docs", "/openapi.json", "/health"):
        return await call_next(request)
    if request.headers.get("x-api-key") != API_KEY:
        return JSONResponse({"detail": "Missing or wrong X-API-Key."}, status_code=401)
    now = time.monotonic()
    hits = recent.setdefault(API_KEY, deque())
    while hits and now - hits[0] > 60:
        hits.popleft()
    if len(hits) >= RATE_LIMIT:
        retry = int(60 - (now - hits[0])) + 1
        return JSONResponse({"detail": "Too many requests."}, status_code=429, headers={"Retry-After": str(retry)})
    hits.append(now)
    if FLAKY and random.random() < FLAKY:
        return JSONResponse({"detail": "Service temporarily unavailable."}, status_code=503)
    return await call_next(request)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/orders")
def orders(
    order_date: Annotated[date, Query(alias="date", description="Order day in Jakarta time (WIB), YYYY-MM-DD.")],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=500)] = 100,
    x_api_key: Annotated[str | None, Header(description="Your API key.")] = None,
):
    file = DATA / "online" / "orders" / f"{order_date}.jsonl"
    rows = [json.loads(line) for line in file.read_text().splitlines()] if file.exists() else []
    start = (page - 1) * page_size
    has_next = start + page_size < len(rows)
    return {
        "data": rows[start:start + page_size],
        "page": page,
        "page_size": page_size,
        "total": len(rows),
        "next_page": page + 1 if has_next else None,
    }


@app.get("/orders/{order_id}")
def order(order_id: str, x_api_key: Annotated[str | None, Header(description="Your API key.")] = None):
    parts = order_id.split("-")
    try:
        day = date(int(parts[1][:4]), int(parts[1][4:6]), int(parts[1][6:]))
    except (IndexError, ValueError):
        raise HTTPException(404, "Order not found.")
    file = DATA / "online" / "orders" / f"{day}.jsonl"
    for line in file.read_text().splitlines() if file.exists() else []:
        row = json.loads(line)
        if row["order_id"] == order_id:
            return row
    raise HTTPException(404, "Order not found.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "8000")))
