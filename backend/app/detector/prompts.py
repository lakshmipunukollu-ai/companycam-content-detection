ROOF_DAMAGE_PROMPT = """Analyze this construction photo of a roof. Object detection has identified the following objects:
{detections}

For each detected object and any additional observations, provide:
1. Classification (material type, damage type)
2. Severity assessment (low, medium, high, critical)
3. Damage type if applicable (hail_impact, wind_damage, granule_loss, soft_spots)
4. Estimated affected area percentage
5. Repair urgency (routine, soon, urgent, emergency)

Return a JSON object with:
{{
    "classifications": [
        {{"category": "damage|material|structure", "subcategory": "...", "description": "...", "severity": "...", "quantity_estimate": null, "unit": null, "confidence": 0.0-1.0}}
    ],
    "damage_assessment": {{
        "damage_type": "...",
        "severity": "...",
        "affected_area_pct": 0.0,
        "repair_urgency": "...",
        "location_description": "..."
    }}
}}"""

MATERIAL_DELIVERY_PROMPT = """Analyze this construction photo of a material delivery. Object detection has identified:
{detections}

For each detected object:
1. Identify material type (shingles, lumber, underlayment, flashing, etc.)
2. Count bundles/pallets/units
3. Flag any quantity discrepancies
4. Assess condition of materials

Return a JSON object with:
{{
    "classifications": [
        {{"category": "material", "subcategory": "...", "description": "...", "severity": null, "quantity_estimate": 0, "unit": "bundles|pallets|rolls|pieces", "confidence": 0.0-1.0}}
    ],
    "damage_assessment": null
}}"""

LOOSE_MATERIAL_PROMPT = """Analyze this construction photo of loose materials on site. Object detection has identified:
{detections}

For each material:
1. Identify type and grade
2. Estimate volume/quantity
3. Note storage condition
4. Flag any issues (water damage, wrong material, etc.)

Return a JSON object with:
{{
    "classifications": [
        {{"category": "material", "subcategory": "...", "description": "...", "severity": null, "quantity_estimate": 0, "unit": "...", "confidence": 0.0-1.0}}
    ],
    "damage_assessment": null
}}"""

GENERAL_CONSTRUCTION_PROMPT = """Analyze this construction site photo. Object detection has identified:
{detections}

Classify each detected object and provide:
1. Category (material, damage, equipment, structure)
2. Description
3. Any notable conditions or concerns
4. Confidence in classification

Return a JSON object with:
{{
    "classifications": [
        {{"category": "material|damage|equipment|structure", "subcategory": "...", "description": "...", "severity": null, "quantity_estimate": null, "unit": null, "confidence": 0.0-1.0}}
    ],
    "damage_assessment": null
}}"""
