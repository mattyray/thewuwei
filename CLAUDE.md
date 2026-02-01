# WuWei - Project Context

A conversational daily practice app. You talk to it, it handles everything — logging meditation, saving gratitude lists, journaling, creating todos, noticing patterns, and reflecting back with a Taoist therapeutic lens.

## Project Overview

**Name:** WuWei (The Wu Wei)  
**Domain:** thewuwei.com  
**Creator:** Matt Raynor  
**Purpose:** Personal daily practice tool that replaces a Trello board workflow

### The Concept

The chat IS the app. Users talk naturally:
- "Did my meditation" → Logged
- "Grateful for: good sleep, my caregivers, coffee" → Saved to gratitude list
- "Let me journal about today..." → Captured, AI reflects back
- "Remind me to call the doctor tomorrow" → Todo created
- "What have I been stressed about lately?" → Patterns retrieved from history

Dashboard exists for visual overview, but conversation is the primary interface.

---

## Tech Stack

### Backend
- **Framework:** Django 5, Django REST Framework
- **Streaming:** Django Channels (WebSocket for AI response streaming)
- **Database:** PostgreSQL 16 + pgvector extension
- **Task Queue:** Celery + Celery Beat (Redis broker)
- **Auth:** Django sessions, email/password + Google OAuth

### AI/ML
- **LLM:** Claude API (Anthropic) via langchain-anthropic
- **Agent Framework:** LangGraph (for tool orchestration)
- **Observability:** LangSmith (tracing, prompt monitoring)
- **Embeddings:** OpenAI text-embedding-ada-002
- **Vector Store:** pgvector

### Frontend
- **Framework:** Next.js 15, React 19, TypeScript
- **Styling:** Tailwind CSS
- **State:** TanStack Query
- **PWA:** next-pwa for installability

### Infrastructure
- **Development:** Docker, Docker Compose
- **Backend Hosting:** Railway
- **Frontend Hosting:** Netlify
- **Email:** Resend

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Next.js PWA   │────▶│  Django API     │
└─────────────────┘     └────────┬────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
┌──────────────┐    ┌─────────────────────┐    ┌──────────────┐
│  PostgreSQL  │    │  LangGraph Agent    │    │    Celery    │
│  + pgvector  │◀───│  (Claude + RAG)     │    │    Beat      │
└──────────────┘    └─────────────────────┘    └──────────────┘
                             │
                             ▼
                    ┌──────────────┐
                    │  LangSmith   │
                    │  (tracing)   │
                    └──────────────┘
```

---

## Project Structure

```
thewuwei/
├── CLAUDE.md                 # This file
├── SPEC.md                   # Detailed feature specification
├── docker-compose.yml        # Development environment
├── .env.example              # Environment variables template
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/               # Django settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py           # Channels support
│   │   └── celery.py
│   │
│   ├── apps/
│   │   ├── users/            # Auth, user model
│   │   ├── journal/          # Entries, gratitude, meditation
│   │   ├── todos/            # Todo items
│   │   ├── mantras/          # Mantras/reminders
│   │   ├── chat/             # Chat interface, WebSocket consumer
│   │   └── agent/            # LangGraph agent, tools, prompts
│   │
│   └── tests/                # pytest tests
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── src/
│   │   ├── app/              # Next.js app router
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── types/
│   └── public/
│
├── scripts/
│   ├── import_trello.py      # Import existing Trello data
│   └── generate_embeddings.py
│
└── docs/
    └── blog-post.md          # Technical writeup for portfolio
```

---

## Development Commands

```bash
# Start development environment
docker-compose up -d

# Run Django commands
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py shell

# Run tests (TDD - run these frequently)
docker-compose exec backend pytest
docker-compose exec backend pytest --cov=apps --cov-report=html
docker-compose exec frontend npm test

# Import Trello data
docker-compose exec backend python scripts/import_trello.py /path/to/trello.json

# View logs
docker-compose logs -f backend
docker-compose logs -f celery
```

---

## Environment Variables

```bash
# Django
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://postgres:postgres@db:5432/wuwei

# Redis
REDIS_URL=redis://redis:6379/0

# AI
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=wuwei

# Auth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Email
RESEND_API_KEY=

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## Development Patterns

### TDD Workflow
1. Write failing test first
2. Write minimum code to pass
3. Refactor
4. Commit after each passing test

### Git Workflow
- Commit after each working change
- Descriptive commit messages
- User runs git commands manually (don't auto-push)

### Code Style
- Backend: Black, isort, flake8
- Frontend: ESLint, Prettier
- Type hints everywhere (Python + TypeScript)

### Testing Levels
- **Unit tests:** Models, services, agent tools
- **Integration tests:** API endpoints, WebSocket consumers
- **E2E tests:** Playwright for critical user flows

---

## Key Files Reference

When working on specific features, reference these files:

| Feature | Key Files |
|---------|-----------|
| Agent logic | `backend/apps/agent/graph.py`, `backend/apps/agent/tools.py` |
| Chat WebSocket | `backend/apps/chat/consumers.py` |
| Journal models | `backend/apps/journal/models.py` |
| RAG retrieval | `backend/apps/agent/retrieval.py` |
| Frontend chat | `frontend/src/components/Chat.tsx` |
| Dashboard | `frontend/src/app/page.tsx` |

---

## Multi-tenancy

Simple user-scoped queries. Every model with user data has a `user` ForeignKey.

```python
# Always filter by user
entries = JournalEntry.objects.filter(user=request.user)

# Embeddings also scoped
similar = Entry.objects.filter(user=request.user).order_by(
    CosineDistance('embedding', query_embedding)
)[:5]
```

---

## Rate Limiting

- **Simple commands** (log meditation, create todo): Unlimited
- **AI reflections + pattern analysis**: 3/day for free users
- **Superuser/owner**: Unlimited
- **Users can add their own API key** for unlimited usage

---

## Data Import

The project includes importing existing Trello data:
- 363 journal entries
- 293 gratitude lists  
- 57 mantras

Import script parses Trello JSON export and populates the database with proper user association and embeddings.

---

## Portfolio Goals

This project demonstrates:
- ✅ LangGraph with real tool use (agentic AI)
- ✅ LangSmith (observability, tracing)
- ✅ Production RAG (pgvector, semantic retrieval)
- ✅ Django Channels (WebSocket streaming)
- ✅ Celery Beat (scheduled tasks)
- ✅ Multi-tenant SaaS architecture
- ✅ TDD (documented process)
- ✅ Docker (containerized development)
- ✅ PWA (installable web app)
