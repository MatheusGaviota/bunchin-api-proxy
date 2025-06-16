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

# Verificar se as variáveis de ambiente estão configuradas
if not JAVA_API_URL or not USERNAME or not PASSWORD:
    logger.error(f"Variáveis de ambiente não configuradas: PROXY_API_URL={JAVA_API_URL}, USERNAME={USERNAME}, PASSWORD={'*' if PASSWORD else None}")

auth_header = f"Basic {base64.b64encode(f'{USERNAME}:{PASSWORD}'.encode()).decode()}"

client = httpx.AsyncClient(headers={"Authorization": auth_header}, timeout=30.0)

async def keep_alive():
    logger.info("Iniciando keep_alive...")
    while True:
        try:
            logger.info("Fazendo requisição de health check local...")
            await client.get("http://localhost:8000/api/health")
            logger.info("Health check local OK")
            
            logger.info(f"Fazendo requisição para API Java: {JAVA_API_URL}/api/funcionario")
            response = await client.get(f"{JAVA_API_URL}/api/funcionario")
            logger.info(f"API Java respondeu com status: {response.status_code}")
        except Exception as e:
            logger.error(f"Erro no keep_alive: {e}")
        
        logger.info("Aguardando 120 segundos...")
        await asyncio.sleep(120)

@app.on_event("startup")
async def startup():
    logger.info("Aplicação iniciando...")
    asyncio.create_task(keep_alive())

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.api_route("/api/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(full_path: str, request: Request):
    url = f"{JAVA_API_URL}/api/{full_path}"
    method = request.method
    logger.info(f"Proxy request: {method} {url}")
    
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
        logger.info(f"API Java respondeu: {resp.status_code}")
    except httpx.RequestError as exc:
        logger.error(f"Erro na requisição para API Java: {exc}")
        raise HTTPException(status_code=502, detail=str(exc))

    excluded_resp = {"transfer-encoding", "content-length", "connection"}
    response_headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded_resp}

    return Response(content=resp.content, status_code=resp.status_code, headers=response_headers)