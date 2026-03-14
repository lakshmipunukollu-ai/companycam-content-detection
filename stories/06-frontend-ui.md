# Story 6: Frontend UI

## Description
As a contractor, I need a web interface to upload photos, view detection results with bounding boxes, correct predictions, and view project reports.

## Acceptance Criteria
- PhotoUpload: drag-and-drop file upload, mobile-friendly, project/type selection
- AnnotationViewer: displays photo with bounding box overlays and labels
- CorrectionTool: edit labels, adjust bounding boxes, delete/add detections
- ProjectReport: material summary table, damage report, accuracy stats
- Login/Register pages
- Project list and detail pages
- Responsive design

## Technical Notes
- React 18 + TypeScript + Vite
- Connects to backend API on port 8000
- Canvas-based bounding box rendering in AnnotationViewer
