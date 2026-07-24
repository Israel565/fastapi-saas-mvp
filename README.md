# FastAPI SaaS MVP Template

A production-ready SaaS MVP boilerplate built with **FastAPI + SQLite + Stripe + AI**.
Deploy in minutes with Docker. Ideal starting point for 1–2 week MVP sprints.

## Features
- 🔐 **JWT Auth** — register, login, protected routes
- 🤖 **AI integration** — pluggable OpenAI or local Ollama (no API cost)
- 💳 **Stripe billing** — subscription checkout + webhook
- 🗄️ **SQLite** — zero-config single-file database
- 🐳 **Dockerized** — one-command deploy
- 🎨 **Vanilla JS frontend** — no build step required

## Quick start
```bash
pip install -r requirements.txt
cp .env.example .env   # edit values
uvicorn app.main:app --reload
# open http://localhost:8000
```

## Run with Docker
```bash
docker build -t saas-mvp .
docker run -p 8000:8000 --env-file .env saas-mvp
```

## API
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | — | Create account |
| POST | `/auth/login` | — | Get JWT token |
| GET | `/auth/me` | ✅ | Current user |
| POST | `/api/chat` | ✅ | AI chat (Ollama/OpenAI) |
| POST | `/billing/checkout` | ✅ | Stripe checkout URL |
| POST | `/billing/webhook` | — | Stripe webhook |
| GET | `/health` | — | Health check |

## Stack
Python 3.11 · FastAPI · SQLAlchemy · SQLite · Stripe · Ollama/OpenAI
