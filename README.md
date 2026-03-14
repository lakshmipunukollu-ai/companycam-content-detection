# CompanyCam Content Detection

An intelligent content detection system for construction photos using a two-stage CV+LLM pipeline. Contractors upload job site photos, the system detects objects (materials, damage, equipment) using object detection, then classifies and assesses them using Claude Vision. Contractors can validate and correct predictions, creating a training feedback loop.

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 1.4, PostgreSQL, Alembic
- **Frontend**: React 18, TypeScript, Vite
- **Auth**: JWT (python-jose, passlib/bcrypt)
- **CV Pipeline**: YOLOv8 (with mock fallback) + Anthropic Claude Vision API
- **Testing**: pytest with PostgreSQL savepoint isolation

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL running locally

### Setup

```bash
# Clone the repo
git clone https://github.com/lakshmipunukollu-ai/companycam-content-detection.git
cd companycam-content-detection

# Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
make install

# Install frontend dependencies
make frontend-install

# Copy and configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL, JWT_SECRET, ANTHROPIC_API_KEY

# Seed the database with sample data
make seed

# Build the frontend
make build
```

### Running

```bash
# Start the backend API server (port 3008)
make dev

# In another terminal, start the frontend dev server (port 5008)
make frontend-dev
```

### Testing

```bash
make test
```

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /health | Health check | No |
| POST | /auth/register | Register user | No |
| POST | /auth/login | Login | No |
| GET | /auth/me | Current user | Yes |
| POST | /projects | Create project | Yes |
| GET | /projects | List projects | Yes |
| GET | /projects/{id} | Get project | Yes |
| PUT | /projects/{id} | Update project | Yes |
| DELETE | /projects/{id} | Delete project | Yes |
| POST | /photos/upload | Upload photo | Yes |
| POST | /photos/analyze | Run analysis | Yes |
| GET | /photos/{id} | Get photo | Yes |
| GET | /photos/{id}/results | Get results | Yes |
| GET | /photos | List photos | Yes |
| DELETE | /photos/{id} | Delete photo | Yes |
| POST | /photos/{id}/corrections | Submit correction | Yes |
| GET | /photos/{id}/corrections | Get corrections | Yes |
| GET | /reports/{projectId} | Project report | Yes |

## Project Structure

```
companycam-content-detection/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app with lifespan
│   │   ├── config.py            # Settings from .env
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models/              # SQLAlchemy models
│   │   ├── routers/             # API route handlers
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── detector/            # CV+LLM pipeline
│   │   └── auth/                # JWT authentication
│   ├── tests/                   # Test suite (60 tests)
│   ├── seed.py                  # Database seeder
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── api/                 # API client functions
│   │   ├── context/             # Auth context
│   │   └── types/               # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── Makefile
└── ARCHITECTURE.md
```

## Seed Users

After running `make seed`, these accounts are available:

| Email | Password | Role |
|-------|----------|------|
| admin@companycam.com | admin123 | admin |
| contractor@companycam.com | contractor123 | contractor |
| reviewer@companycam.com | reviewer123 | reviewer |
