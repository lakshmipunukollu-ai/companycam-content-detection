# Story 5: Project Reports

## Description
As a contractor, I need aggregate reports per project showing material counts, damage summaries, and detection accuracy.

## Acceptance Criteria
- GET /reports/{projectId} returns comprehensive project report
- Material summary: aggregate counts by material type
- Damage summary: counts by damage type and severity
- Correction stats: total detections, corrections made, accuracy rate
- Total photo count for project

## Technical Notes
- Aggregates data across all photos in a project
- Accuracy rate = 1 - (corrections / total_detections)
