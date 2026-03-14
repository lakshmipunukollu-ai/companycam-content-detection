"""
Object detector module.
Uses YOLO if available, otherwise falls back to a mock detector
that generates realistic construction-related detections.
"""
import random
from typing import List, Dict, Any


CONSTRUCTION_OBJECTS = [
    {"label": "shingle_bundle", "category": "material"},
    {"label": "lumber_stack", "category": "material"},
    {"label": "underlayment_roll", "category": "material"},
    {"label": "flashing", "category": "material"},
    {"label": "nail_box", "category": "material"},
    {"label": "roof_section", "category": "structure"},
    {"label": "gutter", "category": "structure"},
    {"label": "vent_pipe", "category": "structure"},
    {"label": "damaged_shingle", "category": "damage"},
    {"label": "hail_dent", "category": "damage"},
    {"label": "wind_lifted_shingle", "category": "damage"},
    {"label": "granule_loss_area", "category": "damage"},
    {"label": "pallet", "category": "material"},
    {"label": "ladder", "category": "equipment"},
    {"label": "dumpster", "category": "equipment"},
    {"label": "tarp", "category": "material"},
]

PHOTO_TYPE_OBJECTS = {
    "roof": ["roof_section", "damaged_shingle", "hail_dent", "wind_lifted_shingle",
             "granule_loss_area", "vent_pipe", "flashing", "gutter"],
    "delivery": ["shingle_bundle", "lumber_stack", "underlayment_roll", "pallet",
                 "nail_box", "tarp"],
    "materials": ["shingle_bundle", "lumber_stack", "underlayment_roll", "flashing",
                  "nail_box", "tarp", "pallet"],
    "general": [obj["label"] for obj in CONSTRUCTION_OBJECTS],
}


class MockObjectDetector:
    """Mock detector that generates realistic construction detections."""

    def detect(self, image_path: str, photo_type: str = "general") -> List[Dict[str, Any]]:
        available_labels = PHOTO_TYPE_OBJECTS.get(photo_type, PHOTO_TYPE_OBJECTS["general"])
        num_detections = random.randint(2, 6)
        detections = []

        for _ in range(num_detections):
            label = random.choice(available_labels)
            x = random.uniform(10, 400)
            y = random.uniform(10, 300)
            w = random.uniform(50, 250)
            h = random.uniform(40, 200)
            confidence = random.uniform(0.55, 0.99)

            detections.append({
                "label": label,
                "confidence": round(confidence, 3),
                "bbox": {"x": round(x, 1), "y": round(y, 1),
                         "w": round(w, 1), "h": round(h, 1)},
            })

        return detections


class ObjectDetector:
    """
    Object detector that tries YOLO first, falls back to mock.
    Stage 1 of the two-stage pipeline.
    """

    def __init__(self, model_path: str = None):
        self.model = None
        self.mock_detector = MockObjectDetector()

        if model_path:
            try:
                from ultralytics import YOLO
                self.model = YOLO(model_path)
            except (ImportError, Exception):
                pass  # Fall back to mock

    def detect(self, image_path: str, photo_type: str = "general") -> List[Dict[str, Any]]:
        if self.model:
            return self._detect_yolo(image_path)
        return self.mock_detector.detect(image_path, photo_type)

    def _detect_yolo(self, image_path: str) -> List[Dict[str, Any]]:
        results = self.model(image_path, verbose=False)
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append({
                    "label": result.names[int(box.cls[0])],
                    "confidence": round(float(box.conf[0]), 3),
                    "bbox": {
                        "x": round(x1, 1),
                        "y": round(y1, 1),
                        "w": round(x2 - x1, 1),
                        "h": round(y2 - y1, 1),
                    },
                })
        return detections
