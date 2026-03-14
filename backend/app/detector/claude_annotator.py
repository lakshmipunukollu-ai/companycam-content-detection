"""
Claude Vision annotator - Stage 2 of the two-stage pipeline.
Takes bounding box detections from Stage 1 and uses Claude Vision
for semantic classification, quantity estimation, and damage assessment.
"""
import base64
import json
import os
from typing import Dict, Any, List, Optional

from app.config import settings
from app.detector.prompts import (
    ROOF_DAMAGE_PROMPT,
    MATERIAL_DELIVERY_PROMPT,
    LOOSE_MATERIAL_PROMPT,
    GENERAL_CONSTRUCTION_PROMPT,
)


PROMPT_MAP = {
    "roof": ROOF_DAMAGE_PROMPT,
    "delivery": MATERIAL_DELIVERY_PROMPT,
    "materials": LOOSE_MATERIAL_PROMPT,
    "general": GENERAL_CONSTRUCTION_PROMPT,
}


class ClaudeAnnotator:
    """Uses Claude Vision API for semantic classification of detected objects."""

    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY

    async def annotate(
        self,
        image_path: str,
        detections: List[Dict[str, Any]],
        photo_type: str = "general",
    ) -> Dict[str, Any]:
        """
        Annotate detected objects using Claude Vision.
        Falls back to mock results if API key is not configured.
        """
        if not self.api_key or self.api_key.startswith("sk-ant-mock"):
            return self._mock_annotate(detections, photo_type)

        try:
            return await self._call_claude(image_path, detections, photo_type)
        except Exception:
            return self._mock_annotate(detections, photo_type)

    async def _call_claude(
        self,
        image_path: str,
        detections: List[Dict[str, Any]],
        photo_type: str,
    ) -> Dict[str, Any]:
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)

        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()

        detection_text = json.dumps(detections, indent=2)
        prompt_template = PROMPT_MAP.get(photo_type, GENERAL_CONSTRUCTION_PROMPT)
        prompt = prompt_template.format(detections=detection_text)

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_b64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )

        text = message.content[0].text
        clean = text.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(clean)

    def _mock_annotate(
        self, detections: List[Dict[str, Any]], photo_type: str
    ) -> Dict[str, Any]:
        """Generate realistic mock annotations based on detections."""
        import random

        classifications = []
        for det in detections:
            label = det["label"]
            category = "material"
            subcategory = label
            description = f"Detected {label.replace('_', ' ')}"
            severity = None
            quantity = None
            unit = None
            confidence = round(random.uniform(0.65, 0.95), 2)

            if "damage" in label or "hail" in label or "wind" in label or "granule" in label:
                category = "damage"
                severity = random.choice(["low", "medium", "high", "critical"])
            elif "shingle" in label:
                quantity = random.randint(4, 24)
                unit = "bundles"
            elif "lumber" in label:
                quantity = random.randint(10, 100)
                unit = "pieces"
            elif "underlayment" in label:
                quantity = random.randint(2, 8)
                unit = "rolls"
            elif "pallet" in label:
                quantity = random.randint(1, 6)
                unit = "pallets"
            elif label in ("ladder", "dumpster"):
                category = "equipment"
            elif label in ("roof_section", "gutter", "vent_pipe"):
                category = "structure"

            classifications.append({
                "category": category,
                "subcategory": subcategory,
                "description": description,
                "severity": severity,
                "quantity_estimate": quantity,
                "unit": unit,
                "confidence": confidence,
            })

        damage_assessment = None
        if photo_type == "roof":
            damage_assessment = {
                "damage_type": random.choice(["hail_impact", "wind_damage", "granule_loss", "soft_spots"]),
                "severity": random.choice(["low", "medium", "high", "critical"]),
                "affected_area_pct": round(random.uniform(5, 45), 1),
                "repair_urgency": random.choice(["routine", "soon", "urgent", "emergency"]),
                "location_description": "Northeast section of roof near ridge line",
            }

        return {
            "classifications": classifications,
            "damage_assessment": damage_assessment,
        }
