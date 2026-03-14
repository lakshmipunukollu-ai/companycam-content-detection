# CompanyCam Content Detection — Architecture

## Overview

An intelligent content detection system for construction photos using a two-stage CV+LLM pipeline. Contractors upload job site photos, the system detects objects (materials, damage, equipment) using object detection, then classifies and assesses them using Claude Vision. Contractors can validate/correct predictions, creating a training feedback loop.

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Render Deployment                 │
│                                                      │
│  ┌──────────────┐   ┌──────────────┐                │
│  │  React UI     │──▶│  FastAPI API  │               │
│  │  (Port 3000)  │   │  (Port 8000)  │               │
│  └──────────────┘   └──────┬───────┘               │
│                            │                         │
│                    ┌───────┴────────┐                │
│                    │  Detector Svc   │               │
│                    │  ┌────────────┐ │               │
│                    │  │ YOLO/DETR  │ │  Stage 1      │
│                    │  └─────┬──────┘ │               │
│                    │  ┌─────▼──────┐ │               │
│                    │  │ Claude API │ │  Stage 2      │
│                    │  └────────────┘ │               │
│                    └───────┬────────┘                │
│                            │                         │
│                    ┌───────▼────────┐                │
│                    │  PostgreSQL    │                │
│                    └────────────────┘                │
└─────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python 3.11+, FastAPI, Uvicorn      |
| ORM        | SQLAlchemy 1.4 (session.query style) |
| Database   | PostgreSQL                          |
| Migrations | Alembic                             |
| Auth       | JWT (python-jose, passlib[bcrypt])   |
| CV Model   | Ultralytics YOLOv8 (or mock)        |
| LLM        | Anthropic Claude Vision API         |
| Frontend   | React 18, TypeScript, Vite          |
| Deploy     | Render                              |

## Data Models

### User
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'contractor',  -- contractor, admin, reviewer
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Project
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    address VARCHAR(500),
    owner_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'active',  -- active, completed, archived
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Photo
```sql
CREATE TABLE photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    uploaded_by UUID REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    photo_type VARCHAR(50) DEFAULT 'general',  -- roof, delivery, materials, general
    status VARCHAR(50) DEFAULT 'pending',       -- pending, analyzing, completed, failed
    width INTEGER,
    height INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Detection
```sql
CREATE TABLE detections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    photo_id UUID REFERENCES photos(id) ON DELETE CASCADE,
    stage VARCHAR(20) NOT NULL,           -- cv, llm
    label VARCHAR(255) NOT NULL,
    confidence FLOAT NOT NULL,
    bbox_x FLOAT NOT NULL,
    bbox_y FLOAT NOT NULL,
    bbox_w FLOAT NOT NULL,
    bbox_h FLOAT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Classification
```sql
CREATE TABLE classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    photo_id UUID REFERENCES photos(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,       -- material, damage, equipment, structure
    subcategory VARCHAR(100),
    description TEXT,
    severity VARCHAR(50),                 -- low, medium, high, critical (for damage)
    quantity_estimate FLOAT,
    unit VARCHAR(50),                     -- bundles, pallets, sq_ft, etc.
    confidence FLOAT NOT NULL,
    requires_review BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Correction
```sql
CREATE TABLE corrections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    detection_id UUID REFERENCES detections(id) ON DELETE CASCADE,
    photo_id UUID REFERENCES photos(id) ON DELETE CASCADE,
    corrected_by UUID REFERENCES users(id),
    original_label VARCHAR(255),
    corrected_label VARCHAR(255),
    original_bbox JSONB,
    corrected_bbox JSONB,
    correction_type VARCHAR(50) NOT NULL,  -- label, bbox, delete, add
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### DamageAssessment
```sql
CREATE TABLE damage_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    photo_id UUID REFERENCES photos(id) ON DELETE CASCADE,
    damage_type VARCHAR(100) NOT NULL,    -- hail_impact, wind_damage, granule_loss, soft_spots
    severity VARCHAR(50) NOT NULL,        -- low, medium, high, critical
    location_description TEXT,
    affected_area_pct FLOAT,
    repair_urgency VARCHAR(50),           -- routine, soon, urgent, emergency
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API Contracts

### Auth
| Method | Endpoint        | Description         | Auth |
|--------|-----------------|---------------------|------|
| POST   | /auth/register  | Register new user   | No   |
| POST   | /auth/login     | Login, get JWT      | No   |
| GET    | /auth/me        | Get current user    | Yes  |

### Health
| Method | Endpoint | Description    | Auth |
|--------|----------|----------------|------|
| GET    | /health  | Health check   | No   |

### Photos
| Method | Endpoint                   | Description                  | Auth |
|--------|----------------------------|------------------------------|------|
| POST   | /photos/upload             | Upload photo for analysis    | Yes  |
| POST   | /photos/analyze            | Submit photo for detection   | Yes  |
| GET    | /photos/{id}               | Get photo details            | Yes  |
| GET    | /photos/{id}/results       | Structured detection results | Yes  |
| GET    | /photos                    | List photos (with filters)   | Yes  |
| DELETE | /photos/{id}               | Delete a photo               | Yes  |

### Corrections
| Method | Endpoint                       | Description            | Auth |
|--------|--------------------------------|------------------------|------|
| POST   | /photos/{id}/corrections       | Submit correction      | Yes  |
| GET    | /photos/{id}/corrections       | Get corrections        | Yes  |

### Projects
| Method | Endpoint              | Description                | Auth |
|--------|-----------------------|----------------------------|------|
| POST   | /projects             | Create project             | Yes  |
| GET    | /projects             | List projects              | Yes  |
| GET    | /projects/{id}        | Get project detail         | Yes  |
| PUT    | /projects/{id}        | Update project             | Yes  |
| DELETE | /projects/{id}        | Delete project             | Yes  |

### Reports
| Method | Endpoint                     | Description                        | Auth |
|--------|------------------------------|------------------------------------|------|
| GET    | /reports/{projectId}         | Aggregate material/damage summary  | Yes  |

## API Response Schemas

### POST /photos/analyze — Response
```json
{
  "photo_id": "uuid",
  "status": "completed",
  "detections": [
    {
      "id": "uuid",
      "label": "shingle_bundle",
      "confidence": 0.94,
      "bbox": {"x": 120, "y": 80, "w": 200, "h": 150},
      "stage": "cv"
    }
  ],
  "classifications": [
    {
      "category": "material",
      "subcategory": "roofing_shingle",
      "description": "Bundle of architectural shingles",
      "quantity_estimate": 12,
      "unit": "bundles",
      "confidence": 0.87
    }
  ],
  "damage_assessment": {
    "damage_type": "hail_impact",
    "severity": "medium",
    "affected_area_pct": 15.5,
    "repair_urgency": "soon"
  },
  "requires_human_review": true
}
```

### POST /photos/{id}/corrections — Request
```json
{
  "detection_id": "uuid",
  "correction_type": "label",
  "corrected_label": "ridge_cap_shingle",
  "corrected_bbox": {"x": 125, "y": 82, "w": 195, "h": 148},
  "notes": "This is a ridge cap, not a regular shingle bundle"
}
```

### GET /reports/{projectId} — Response
```json
{
  "project_id": "uuid",
  "project_name": "Smith Residence Roof",
  "total_photos": 24,
  "material_summary": [
    {"material": "shingle_bundle", "total_count": 48, "unit": "bundles"},
    {"material": "underlayment_roll", "total_count": 6, "unit": "rolls"}
  ],
  "damage_summary": [
    {"type": "hail_impact", "severity": "high", "count": 8},
    {"type": "wind_damage", "severity": "medium", "count": 3}
  ],
  "correction_stats": {
    "total_detections": 156,
    "corrections_made": 12,
    "accuracy_rate": 0.923
  }
}
```

## Two-Stage Detection Pipeline

### Stage 1: Object Detection (CV)
- Use YOLOv8 (ultralytics) for fast bounding box detection
- Falls back to mock detector if model not available
- Outputs: bounding boxes with object class labels and confidence scores
- Target latency: < 500ms per image

### Stage 2: Semantic Classification (LLM)
- Claude Vision API analyzes the image with detected bounding boxes as context
- Provides semantic classification, quantity estimation, damage assessment
- Uses photo_type-specific prompts (roof, delivery, materials, general)
- Flags low-confidence results for human review (threshold: 0.7)

## Correction Feedback Loop
1. Contractor views detection results in AnnotationViewer
2. Uses CorrectionTool to fix labels, adjust bounding boxes, or delete false positives
3. Corrections stored in database as training signal
4. Reports track accuracy rate over time

## Environment Variables
```
DATABASE_URL=postgresql://user:pass@localhost:5432/companycam
JWT_SECRET=your-jwt-secret-key
ANTHROPIC_API_KEY=sk-ant-...
UPLOAD_DIR=./uploads
YOLO_MODEL_PATH=./models/yolov8n.pt
CORS_ORIGINS=http://localhost:3000
```

## Directory Structure
```
companycam-content-detection/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app with lifespan
│   │   ├── config.py               # Settings from .env
│   │   ├── database.py             # SQLAlchemy engine + session
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── photo.py
│   │   │   ├── detection.py
│   │   │   ├── classification.py
│   │   │   ├── correction.py
│   │   │   └── damage_assessment.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── photos.py
│   │   │   ├── projects.py
│   │   │   ├── corrections.py
│   │   │   ├── reports.py
│   │   │   └── health.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── photo.py
│   │   │   ├── detection.py
│   │   │   ├── project.py
│   │   │   ├── correction.py
│   │   │   └── report.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── photo_service.py
│   │   │   └── report_service.py
│   │   ├── detector/
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py         # PhotoAnalysisPipeline
│   │   │   ├── object_detector.py  # YOLO/mock detector
│   │   │   ├── claude_annotator.py # Claude Vision integration
│   │   │   ├── material_estimator.py
│   │   │   ├── damage_classifier.py
│   │   │   └── prompts.py          # Detection prompts
│   │   └── auth/
│   │       ├── __init__.py
│   │       └── jwt_handler.py
│   ├── alembic/
│   │   ├── alembic.ini
│   │   └── versions/
│   ├── seed.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PhotoUpload.tsx
│   │   │   ├── AnnotationViewer.tsx
│   │   │   ├── CorrectionTool.tsx
│   │   │   └── ProjectReport.tsx
│   │   ├── pages/
│   │   ├── api/
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── Makefile
├── ARCHITECTURE.md
├── PROJECT_BRIEF.md
└── stories/
```

## Deviations from Brief
1. **Mock detector fallback**: YOLO model download may not be available in all environments, so a mock detector is included that generates realistic bounding box data. This allows the full pipeline to work without requiring model files.
2. **File-based uploads**: Photos stored locally in `./uploads` directory rather than S3, to simplify deployment. Can be swapped to S3 later.
3. **Synchronous analysis**: Initial implementation runs analysis synchronously on upload. A background job queue can be added later for production scale.
