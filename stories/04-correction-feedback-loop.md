# Story 4: Correction Feedback Loop

## Description
As a contractor, I need to validate and correct detection results so the system improves over time.

## Acceptance Criteria
- POST /photos/{id}/corrections accepts corrections to detections
- Correction types: label change, bbox adjustment, delete false positive, add missed detection
- GET /photos/{id}/corrections returns all corrections for a photo
- Corrections stored as training signal with original vs corrected values
- Accuracy rate tracked per project

## Technical Notes
- Each correction links to original detection
- Stores both original and corrected values for ML training
- Notes field for contractor explanations
