export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  address: string | null;
  owner_id: string;
  status: string;
  created_at: string;
  updated_at: string | null;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  address?: string;
}

export interface Photo {
  id: string;
  project_id: string;
  uploaded_by: string;
  filename: string;
  file_path: string;
  photo_type: string;
  status: string;
  width: number | null;
  height: number | null;
  created_at: string;
}

export interface BBox {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface Detection {
  id: string;
  label: string;
  confidence: number;
  bbox: BBox;
  stage: string;
}

export interface Classification {
  id: string;
  category: string;
  subcategory: string | null;
  description: string | null;
  severity: string | null;
  quantity_estimate: number | null;
  unit: string | null;
  confidence: number;
  requires_review: boolean;
}

export interface DamageAssessment {
  id: string;
  damage_type: string;
  severity: string;
  location_description: string | null;
  affected_area_pct: number | null;
  repair_urgency: string | null;
  notes: string | null;
}

export interface PhotoAnalysisResult {
  photo_id: string;
  status: string;
  detections: Detection[];
  classifications: Classification[];
  damage_assessments: DamageAssessment[];
  requires_human_review: boolean;
}

export interface Correction {
  id: string;
  detection_id: string | null;
  photo_id: string;
  corrected_by: string;
  original_label: string | null;
  corrected_label: string | null;
  original_bbox: BBox | null;
  corrected_bbox: BBox | null;
  correction_type: string;
  notes: string | null;
  created_at: string;
}

export interface CorrectionCreate {
  detection_id?: string;
  correction_type: string;
  corrected_label?: string;
  corrected_bbox?: { x: number; y: number; w: number; h: number };
  notes?: string;
}

export interface MaterialSummary {
  material: string;
  total_count: number;
  unit: string | null;
}

export interface DamageSummary {
  type: string;
  severity: string;
  count: number;
}

export interface CorrectionStats {
  total_detections: number;
  corrections_made: number;
  accuracy_rate: number;
}

export interface ProjectReport {
  project_id: string;
  project_name: string;
  total_photos: number;
  material_summary: MaterialSummary[];
  damage_summary: DamageSummary[];
  correction_stats: CorrectionStats;
}
