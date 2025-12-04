export const TherapyType = {
  PSILOCYBIN: 'psilocybin',
  MDMA: 'mdma',
  KETAMINE: 'ketamine',
  LSD: 'lsd',
  IBOGAINE: 'ibogaine',
  TESTOSTERONE: 'testosterone',
  ESTROGEN: 'estrogen',
  GROWTH_HORMONE: 'growth_hormone',
  PEPTIDES: 'peptides',
  CHEMOTHERAPY: 'chemotherapy',
  IMMUNOTHERAPY: 'immunotherapy',
  RADIATION: 'radiation',
  STEM_CELL: 'stem_cell',
  PLATELET_RICH_PLASMA: 'platelet_rich_plasma',
  EXOSOME: 'exosome',
  GENE_THERAPY: 'gene_therapy',
  CRISPR: 'crispr',
  CAR_T: 'car_t',
  LONGEVITY: 'longevity',
  OTHER: 'other',
} as const;

export type TherapyType = (typeof TherapyType)[keyof typeof TherapyType];

export const EvidenceLevel = {
  FDA_APPROVED: 'fda_approved',
  PHASE_3: 'phase_3_trial',
  PHASE_2: 'phase_2_trial',
  PHASE_1: 'phase_1_trial',
  PRECLINICAL: 'preclinical',
  CLINICAL_PRACTICE: 'clinical_practice',
} as const;

export type EvidenceLevel = (typeof EvidenceLevel)[keyof typeof EvidenceLevel];

export const StepType = {
  SCREENING: 'screening',
  PREPARATION: 'preparation',
  DOSING: 'dosing',
  INTEGRATION: 'integration',
  DECISION_POINT: 'decision_point',
  FOLLOWUP: 'followup',
} as const;

export type StepType = (typeof StepType)[keyof typeof StepType];

export interface SafetyCheck {
  id: number;
  protocol_step_id: number;
  check_type: string;
  condition: Record<string, unknown>;
  severity: 'blocking' | 'warning' | 'info';
  override_allowed: boolean;
  override_requirements?: Record<string, unknown>;
  evidence_source?: string;
  created_at: string;
}

export interface ProtocolStep {
  id: number;
  protocol_id: number;
  sequence_order: number;
  step_type: StepType;
  title: string;
  description?: string;
  duration_minutes?: number;
  required_roles?: string[];
  documentation_template_id?: number;
  evaluation_rules?: Record<string, unknown>;
  branch_outcomes?: Record<string, unknown>;
  clinical_scales?: string[];
  vitals_monitoring?: Record<string, unknown>;
  safety_checks?: SafetyCheck[];
  created_at: string;
}

export interface Protocol {
  id: number;
  name: string;
  version: string;
  status: 'draft' | 'active' | 'archived';
  therapy_type: TherapyType;
  condition_treated: string;
  evidence_level: EvidenceLevel;
  overview?: string;
  duration_weeks?: number;
  total_sessions?: number;
  evidence_sources?: Array<{ title: string; url: string; type: string }>;
  created_by: number;
  created_at: string;
  updated_at: string;
  steps?: ProtocolStep[];
}

export interface ProtocolFilters {
  therapy_type?: TherapyType;
  condition?: string;
  evidence_level?: EvidenceLevel;
  status?: 'draft' | 'active' | 'archived';
  search?: string;
}

export interface ProtocolListResponse {
  items: Protocol[];
  total: number;
  page: number;
  size: number;
}
