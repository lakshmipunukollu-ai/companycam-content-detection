# Build Summary - CompanyCam Content Detection

## Project Overview

CompanyCam Content Detection is a full-stack web application for intelligent construction photo analysis. It uses a two-stage pipeline combining computer vision (YOLOv8) and LLM analysis (Claude Vision) to detect materials, damage, and equipment in job site photos. Contractors can review, correct, and track detection accuracy over time.

## Architecture

### Backend (FastAPI + PostgreSQL)
- **Framework**: FastAPI with lifespan pattern for startup/shutdown
- **ORM**: SQLAlchemy 1.4 using `session.query()` style
- **Database**: PostgreSQL with psycopg2-binary driver
- **Auth**: JWT tokens via python-jose, bcrypt password hashing via passlib
- **Detection Pipeline**: Two-stage architecture:
  - Stage 1: YOLOv8 object detection (with mock fallback)
  - Stage 2: Claude Vision API for semantic classification and damage assessment
- **Port**: 3008

### Frontend (React + TypeScript + Vite)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 8
- **Routing**: react-router-dom v7
- **HTTP Client**: Axios with JWT interceptors
- **Port**: 5008 (dev server proxies API calls to backend)

### Database Schema (7 tables)
- `users` - Authentication and roles (contractor, admin, reviewer)
- `projects` - Job site groupings
- `photos` - Uploaded images with type and status tracking
- `detections` - Bounding box detections from CV pipeline
- `classifications` - Semantic classifications from LLM
- `damage_assessments` - Damage type, severity, repair urgency
- `corrections` - User feedback on detection accuracy

## Features Implemented

### Authentication
- User registration with role selection
- JWT-based login with 24-hour token expiry
- Protected routes on both frontend and backend
- Auth context with localStorage persistence

### Project Management
- Full CRUD for projects (name, description, address, status)
- Project listing with status badges
- Owner-scoped access control

### Photo Upload & Analysis
- Drag-and-drop file upload (mobile-friendly)
- Photo type selection (roof, delivery, materials, general)
- Auto-analyze option triggers pipeline on upload
- Status tracking: pending -> analyzing -> completed/failed
- Photo grid view with thumbnails

### Annotation Viewer
- Canvas-based rendering of photos with bounding box overlays
- Color-coded detection boxes with labels and confidence scores
- Click-to-select detection highlighting
- Responsive scaling to container width

### Correction Feedback Loop
- Select any detection to submit corrections
- Correction types: label fix, delete (false positive), bbox adjustment
- Notes field for contractor explanations
- Original vs corrected values stored for ML training signal

### Project Reports
- Aggregate material summary (counts by type with units)
- Damage summary (counts by type and severity)
- Detection accuracy stats (total detections, corrections, accuracy rate)
- Visual accuracy bar chart

## API Endpoints (18 total)

| Category | Endpoints |
|----------|-----------|
| Health | GET /health |
| Auth | POST /auth/register, POST /auth/login, GET /auth/me |
| Projects | POST/GET/GET/PUT/DELETE /projects |
| Photos | POST /photos/upload, POST /photos/analyze, GET/GET/DELETE /photos |
| Corrections | POST/GET /photos/{id}/corrections |
| Reports | GET /reports/{projectId} |

## Test Suite

**60 tests, 0 failures** across 8 test files:

| File | Tests | Coverage |
|------|-------|----------|
| test_health.py | 2 | Health endpoint |
| test_jwt.py | 5 | Password hashing, token create/decode |
| test_auth.py | 9 | Register, login, me, error cases |
| test_projects.py | 11 | CRUD, auth, not found |
| test_photos.py | 12 | Upload, list, get, results, delete |
| test_corrections.py | 7 | Create, list, error cases |
| test_reports.py | 7 | Report generation, accuracy, empty |
| test_models.py | 7 | All SQLAlchemy models |

Tests use PostgreSQL with savepoint-based transaction isolation for clean test state.

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make dev` | Start backend on port 3008 |
| `make test` | Run 60 tests |
| `make seed` | Seed database with sample data |
| `make build` | Install deps and build frontend |
| `make frontend-dev` | Start frontend dev server on port 5008 |
| `make install` | Install backend Python dependencies |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| DATABASE_URL | PostgreSQL connection string |
| JWT_SECRET | Secret key for JWT signing |
| ANTHROPIC_API_KEY | Claude Vision API key |
| PORT | Backend server port (3008) |
| VITE_API_URL | Frontend API base URL |
| UPLOAD_DIR | Photo upload directory |

## Key Design Decisions

1. **Mock detector fallback**: When YOLO model is unavailable, a mock detector generates realistic construction-related bounding boxes, allowing the full pipeline to work without model files.
2. **Savepoint-based test isolation**: Tests use PostgreSQL savepoints instead of SQLite, ensuring test behavior matches production and supporting PostgreSQL-specific features (UUID, JSONB).
3. **Canvas-based annotation rendering**: Uses HTML5 Canvas for bounding box rendering instead of SVG or CSS overlays, providing better performance with many detections and enabling click-to-select functionality.
4. **Synchronous analysis**: Analysis runs synchronously for simplicity. Can be extended with background job queue for production scale.
5. **Vite proxy**: Frontend dev server proxies /api and /uploads requests to the backend, avoiding CORS issues during development.
