from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import base64
import os
import asyncio
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JAVA_API_URL = os.getenv("PROXY_API_URL")
USERNAME = os.getenv("PROXY_API_USERNAME")
PASSWORD = os.getenv("PROXY_API_PASSWORD")
auth_header = f"Basic {base64.b64encode(f'{USERNAME}:{PASSWORD}'.encode()).decode()}"

# Configurar timeouts e limites de conexão
timeout = httpx.Timeout(30.0, connect=10.0)
limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
client = httpx.AsyncClient(
    headers={"Authorization": auth_header},
    timeout=timeout,
    limits=limits
)

async def keep_alive():
    while True:
        try:
            await client.get("http://localhost:8000/api/health")
            await client.get(f"{JAVA_API_URL}/funcionario")
        except Exception as e:
            logger.warning(f"Keep-alive failed: {e}")
        await asyncio.sleep(120)

@app.on_event("startup")
async def startup():
    asyncio.create_task(keep_alive())

@app.on_event("shutdown")
async def shutdown():
    await client.aclose()

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.api_route("/api/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(full_path: str, request: Request):
    url = f"{JAVA_API_URL}/{full_path}"
    method = request.method
    excluded = {"host", "content-length", "connection"}
    headers = {k: v for k, v in request.headers.items() if k.lower() not in excluded}
    headers["Authorization"] = auth_header

    try:
        resp = await client.request(
            method=method,
            url=url,
            headers=headers,
            content=await request.body(),
            params=request.query_params
        )
        
        logger.info(f"{method} {url} -> {resp.status_code}")
        
    except httpx.TimeoutException:
        logger.error(f"Timeout for {method} {url}")
        raise HTTPException(status_code=504, detail="Gateway timeout")
    except httpx.ConnectError as exc:
        logger.error(f"Connection error for {method} {url}: {exc}")
        raise HTTPException(status_code=502, detail="Connection failed to upstream server")
    except httpx.RequestError as exc:
        logger.error(f"Request error for {method} {url}: {exc}")
        raise HTTPException(status_code=502, detail=f"Upstream error: {str(exc)}")

    excluded_resp = {"transfer-encoding", "content-length", "connection"}
    response_headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded_resp}

    return Response(content=resp.content, status_code=resp.status_code, headers=response_headers)