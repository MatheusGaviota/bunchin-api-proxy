from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import base64
import os

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
basic_auth = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
auth_header = f"Basic {basic_auth}"

@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse("static/index.html", media_type="text/html")

@app.api_route("/api/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(full_path: str, request: Request):
    url = f"{JAVA_API_URL}/{full_path}"
    method = request.method
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    headers["Authorization"] = auth_header
    body = await request.body()

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method,
                url,
                headers=headers,
                content=body,
                params=request.query_params
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Erro ao conectar ao backend: {exc}")

    excluded_headers = {"transfer-encoding", "content-length", "connection"}
    response_headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded_headers}

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=response_headers
    )