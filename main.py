from fastapi import FastAPI, Request, Response, HTTPException
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
auth_header = f"Basic {base64.b64encode(f'{USERNAME}:{PASSWORD}'.encode()).decode()}"

client = httpx.AsyncClient(headers={"Authorization": auth_header})

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
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    excluded_resp = {"transfer-encoding", "content-length", "connection"}
    response_headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded_resp}

    return Response(content=resp.content, status_code=resp.status_code, headers=response_headers)