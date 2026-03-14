# Story 3: Photo Upload & Analysis Pipeline

## Description
As a contractor, I need to upload construction photos and have them automatically analyzed for objects, materials, and damage.

## Acceptance Criteria
- POST /photos/upload accepts image file + project_id + photo_type
- Photo saved to uploads directory
- POST /photos/analyze triggers two-stage pipeline
- Stage 1: Object detection (YOLO or mock) returns bounding boxes
- Stage 2: Claude Vision classifies objects, estimates quantities, assesses damage
- GET /photos/{id}/results returns all detections, classifications, damage assessments
- Low-confidence results flagged for human review (threshold: 0.7)
- Photo status tracked: pending -> analyzing -> completed/failed

## Technical Notes
- Mock detector generates realistic construction-related detections
- Claude Vision prompt varies by photo_type (roof, delivery, materials, general)
- Results stored in detections, classifications, damage_assessments tables
