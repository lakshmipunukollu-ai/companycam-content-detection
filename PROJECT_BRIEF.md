# PROJECT BRIEF
# (Extracted from MASTER_PROJECT_PLAYBOOK.md — your section only)

## SENIOR ENGINEER DECISIONS — READ FIRST

Before any code is written, here are the opinionated decisions made across all 9 projects
and why. An agent should never second-guess these unless given new information.

### Stack choices made
| Project | Backend | Frontend | DB | Deploy | Rationale |
|---------|---------|---------|-----|--------|-----------|
| FSP Scheduler | TypeScript + Node.js | React + TypeScript | PostgreSQL (multi-tenant) | Azure Container Apps | TS chosen over C# — same Azure ecosystem, better AI library support, faster iteration |
| Replicated | Python + FastAPI | Next.js 14 | PostgreSQL + S3 | Docker | Python wins for LLM tooling; Next.js for real-time streaming UI |
| ServiceCore | Node.js + Express | Angular (required) | PostgreSQL | Railway | Angular required — clean REST API behind it |
| Zapier | Python + FastAPI | None (API only + optional React dashboard) | PostgreSQL + Redis | Railway | Redis for event queue durability; Python for DX-first API |
| ST6 | Java 21 + Spring Boot | TypeScript micro-frontend (React) | PostgreSQL | Docker | Java required — Spring Boot is the senior choice; React micro-frontend mounts into PA host |
| ZeroPath | Python + FastAPI | React + TypeScript | PostgreSQL | Render | Python for LLM scanning logic; React for triage dashboard |
| Medbridge | Python + FastAPI + LangGraph | None (webhook-driven) | PostgreSQL | Railway | LangGraph is the correct tool for state-machine AI agents |
| CompanyCam | Python + FastAPI | React + TypeScript | PostgreSQL | Render | Python for CV/ML inference; React for annotation UI |
| Upstream | Django + DRF | React + TypeScript | PostgreSQL | Render | Django for rapid e-commerce scaffolding; built-in admin is a bonus |

### The 4 shared modules — build these FIRST
These are the highest ROI pieces of work. Build them once, copy-scaffold into every project.

1. `shared/llm_client.py` — Claude API wrapper with retry, streaming, structured output parsing
2. `shared/auth/` — JWT auth + role-based guards (Python + TypeScript versions)
3. `shared/state_machine.py` — Generic FSM: states, transitions, guards, event log
4. `shared/queue/` — Job queue pattern: enqueue, dequeue, ack, retry (Redis + Postgres fallback)

### Build order (wave system)
**Wave 0 (Day 1):** Build shared modules. All other waves depend on these.
**Wave 1 (Days 2-3):** Zapier + ZeroPath — establish LLM pipeline + REST API patterns
**Wave 2 (Days 4-5):** Medbridge + Replicated — LLM pipeline variants, more complex AI
**Wave 3 (Days 6-8):** FSP + ST6 — complex business logic, approval flows
**Wave 4 (Days 9-11):** ServiceCore + Upstream + CompanyCam — isolated stacks, finish strong

---

## PROJECT 8: COMPANYCAM — INTELLIGENT CONTENT DETECTION
**Company:** CompanyCam | **Stack:** Python + FastAPI + React + TypeScript + PostgreSQL

### Company mission to impress
CompanyCam helps contractors document job sites through photos. They're building ML pipelines
for computer vision. What will impress them: real object detection (not just Claude describing
photos), structured output that can feed downstream workflows, and a UI where contractors can
validate and correct predictions (closing the training feedback loop).

### Architecture
```
Render
├── api (Python + FastAPI)
│   ├── POST /photos/analyze         — submit photo for detection
│   ├── GET  /photos/:id/results     — structured detection results
│   ├── POST /photos/:id/corrections — human correction (training signal)
│   └── GET  /reports/:projectId     — aggregate material counts, damage summary
├── detector (Python)
│   ├── ObjectDetector              — YOLO or DETR for fast inference
│   ├── ClaudeAnnotator             — Claude Vision for classification + description
│   ├── MaterialEstimator           — volume estimation from bounding boxes
│   └── DamageClassifier           — roof damage type + severity
└── ui (React + TypeScript)
    ├── PhotoUpload                  — drag-and-drop, mobile-friendly
    ├── AnnotationViewer             — bounding boxes + labels on photo
    ├── CorrectionTool              — contractor validates/fixes detections
    └── ProjectReport               — material summary, damage report
```

### The two-stage detection pipeline — CV + LLM working together
```python
class PhotoAnalysisPipeline:
    """
    Senior insight: Don't use LLM for everything.
    Use specialized CV models for speed/accuracy, LLM for semantic classification.
    
    Stage 1: YOLO/DETR → bounding boxes + object classes (fast, cheap)
    Stage 2: Claude Vision → semantic classification + quantity estimation + damage assessment
    
    This is how production CV systems work. It will impress their ML team.
    """
    
    async def analyze(self, image_path: str, context: PhotoContext) -> DetectionResult:
        # Stage 1: Fast object detection
        detections = await self.object_detector.detect(image_path)
        # Returns: [{"class": "shingle", "bbox": [x,y,w,h], "confidence": 0.94}, ...]
        
        # Stage 2: Claude Vision for semantic understanding
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()
        
        claude_result = await self.claude_client.analyze_image(
            image_b64=image_b64,
            detections=detections,
            context=context,
            prompt=self._build_prompt(context.photo_type)
        )
        
        return DetectionResult(
            detections=detections,
            classifications=claude_result.classifications,
            damage_assessment=claude_result.damage_assessment,
            material_counts=claude_result.material_counts,
            confidence_scores=claude_result.confidence_scores,
            requires_human_review=self._needs_review(claude_result),
        )
    
    def _build_prompt(self, photo_type: str) -> str:
        prompts = {
            "roof": ROOF_DAMAGE_PROMPT,
            "delivery": MATERIAL_DELIVERY_PROMPT,
            "materials": LOOSE_MATERIAL_PROMPT,
        }
        return prompts.get(photo_type, GENERAL_CONSTRUCTION_PROMPT)
```

### CLAUDE.md for CompanyCam agent
```
You are a senior Python ML engineer building an intelligent content detection system for CompanyCam.

COMPANY MISSION: Help contractors document and understand job sites through photos.
Contractors need accurate, fast answers: what's damaged, what was delivered, how much material.

TWO-STAGE PIPELINE (do not simplify this):
1. Object detection (YOLO or similar) → bounding boxes + classes
2. Claude Vision → semantic classification, quantity estimation, damage severity

This mirrors how production CV systems work. Use real object detection, not just Claude describing photos.

KEY DETECTION TYPES:
- Roof damage: hail impact, wind damage, shingle granule loss, soft spots → severity + location
- Material delivery: count bundles/pallets, identify material type, flag quantity discrepancies
- Loose materials: volume estimation, material type, prompt for human confirmation on estimates

CORRECTION LOOP: Every human correction should be stored. This is training signal.
The UI must make it effortless for contractors to validate/fix predictions.

NEVER: Use Claude Vision alone without structured object detection first
ALWAYS: Include confidence scores, flag low-confidence for human review, store corrections
```

---


## SHARED MODULES — BUILD THESE IN WAVE 0

### shared/llm_client.py
```python
"""
Shared Claude API client. Used by: Replicated, ZeroPath, Medbridge, CompanyCam, FSP, Upstream.
Copy this file into each Python project that needs it.
"""
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
import json

client = anthropic.Anthropic()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def complete(
    prompt: str,
    system: str = "",
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 4096,
    as_json: bool = False,
) -> str | dict:
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    text = message.content[0].text
    if as_json:
        # Strip markdown fences if present
        clean = text.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(clean)
    return text

async def analyze_image(
    image_b64: str,
    prompt: str,
    system: str = "",
    model: str = "claude-sonnet-4-20250514",
) -> dict:
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
                {"type": "text", "text": prompt},
            ],
        }],
    )
    return json.loads(message.content[0].text)
```

### shared/auth.py (Python version)
```python
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(user_id: str, role: str) -> str:
    return jwt.encode(
        {"sub": user_id, "role": role, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)},
        SECRET_KEY, algorithm=ALGORITHM
    )

def require_role(*roles: str):
    def dependency(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("role") not in roles:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    return dependency

# Usage: @router.get("/admin", dependencies=[Depends(require_role("admin", "manager"))])
```

### shared/state_machine.py
```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Callable
from datetime import datetime

S = TypeVar('S')  # State type
E = TypeVar('E')  # Event type

@dataclass
class Transition(Generic[S, E]):
    from_state: S
    event: E
    to_state: S
    guard: Callable | None = None  # optional condition function

class StateMachine(Generic[S, E]):
    def __init__(self, initial: S, transitions: list[Transition]):
        self.state = initial
        self._transitions = {(t.from_state, t.event): t for t in transitions}
        self._log: list[dict] = []

    def transition(self, event: E, context: dict = None) -> S:
        key = (self.state, event)
        t = self._transitions.get(key)
        if not t:
            raise ValueError(f"Invalid transition: {self.state} + {event}")
        if t.guard and not t.guard(context or {}):
            raise ValueError(f"Guard failed: {self.state} + {event}")
        prev = self.state
        self.state = t.to_state
        self._log.append({"from": prev, "event": event, "to": self.state, "at": datetime.utcnow().isoformat()})
        return self.state

    @property
    def history(self) -> list[dict]:
        return self._log.copy()
```

---
