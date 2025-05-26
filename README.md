# Bunchin API Proxy

![GitHub repo size](https://img.shields.io/github/repo-size/MatheusGaviota/bunchin-api-proxy?style=for-the-badge)
![GitHub language count](https://img.shields.io/github/languages/count/MatheusGaviota/bunchin-api-proxy?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/MatheusGaviota/bunchin-api-proxy?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/MatheusGaviota/bunchin-api-proxy?style=for-the-badge)
![GitHub pull requests](https://img.shields.io/github/issues-pr/MatheusGaviota/bunchin-api-proxy?style=for-the-badge)
![GitHub License](https://img.shields.io/github/license/MatheusGaviota/bunchin-api-proxy?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/MatheusGaviota/bunchin-api-proxy?style=for-the-badge)
![Open Source Love](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-red?style=for-the-badge)

Este projeto é um **proxy seguro** desenvolvido em [FastAPI](https://fastapi.tiangolo.com/) para intermediar requisições HTTP entre clientes e a API Java da plataforma Bunchin. Ele facilita o roteamento, autenticação e gerenciamento de requisições, expondo uma interface RESTful acessível e protegida.

## Funcionalidades

- **Proxy transparente** para a API Java do Bunchin.
- **Autenticação básica** automática em todas as requisições para a API Java.
- Suporte completo aos métodos HTTP: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `OPTIONS`.
- Preservação de parâmetros, corpo e cabeçalhos das requisições originais.
- Encaminhamento de todas as rotas `/api/*` para o backend Java.
- Página inicial estática com informações do serviço.

## Rotas

- `GET /`  
  Retorna a página estática de apresentação do proxy (`static/index.html`).

- `ANY /api/{path}`  
  Encaminha qualquer requisição para o endpoint correspondente na API Java, adicionando autenticação básica.

## Como funciona

1. O proxy recebe requisições em `/api`.
2. Adiciona o cabeçalho `Authorization` com autenticação básica, usando as variáveis de ambiente configuradas.
3. Encaminha a requisição para a URL da API Java definida em `PROXY_API_URL`.
4. Retorna a resposta do backend Java ao cliente, preservando status, corpo e cabeçalhos relevantes.

## Variáveis de Ambiente

Configure as seguintes variáveis de ambiente para o funcionamento correto do proxy:

- `PROXY_API_URL` — URL base da API Java (ex: `http://java-api:8080`)
- `PROXY_API_USERNAME` — Usuário para autenticação básica
- `PROXY_API_PASSWORD` — Senha para autenticação básica

Exemplo de uso em `.env`:

```
PROXY_API_URL=http://java-api:8080
PROXY_API_USERNAME=usuario
PROXY_API_PASSWORD=senha
```

## Como executar localmente

1. Instale as dependências:
   ```sh
   pip install fastapi uvicorn httpx
   ```

2. Exporte as variáveis de ambiente necessárias.

3. Inicie o servidor:
   ```sh
   uvicorn main:app --reload
   ```

4. Acesse [http://localhost:8000](http://localhost:8000) para visualizar a página inicial.

## Docker

Para rodar via Docker:

```sh
docker build -t bunchin-api-proxy .
docker run -p 8000:8000 \
  -e PROXY_API_URL=http://java-api:8080 \
  -e PROXY_API_USERNAME=usuario \
  -e PROXY_API_PASSWORD=senha \
  bunchin-api-proxy
```

## Estrutura do Projeto

```
.
├── [`main.py`](main.py )              # Código principal do proxy FastAPI
├── Dockerfile           # Dockerfile para containerização
├── static/
│   └── [`static/index.html`](static/index.html )       # Página inicial estática
└── [`README.md`](README.md )            # Este arquivo
```

## Tecnologias

![Docker](https://img.shields.io/badge/Docker-ready-blue?style=for-the-badge&logo=docker)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green?style=for-the-badge&logo=fastapi)
![Uvicorn](https://img.shields.io/badge/Uvicorn-0.29.0-005571?style=for-the-badge&logo=uvicorn)
![HTTPX](https://img.shields.io/badge/HTTPX-0.27.0-3b82f6?style=for-the-badge&logo=httpx)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [HTTPX](https://www.python-httpx.org/)
- [Tailwind CSS](https://tailwindcss.com/) (na página estática)

---

&copy; 2025 Bunchin Team. Desenvolvido com FastAPI & Tailwind CSS.
