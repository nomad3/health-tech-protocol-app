export interface Patient {
  id: number;
  user_id: number;
  first_name: string;
  last_name: string;
  email: string;
  date_of_birth: string;
  phone?: string;
  status: 'active' | 'inactive' | 'completed';
  created_at: string;
}

export interface TherapySession {
  id: number;
  treatment_plan_id: number;
  protocol_step_id: number;
  patient_id: number;
  therapist_id: number;
  scheduled_at: string;
  completed_at?: string;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  session_type: string;
  duration_minutes?: number;
  patient?: Patient;
  protocol_step?: {
    id: number;
    title: string;
    step_type: string;
  };
}

export interface SessionDocumentation {
  id: number;
  session_id: number;
  vitals?: VitalsData;
  therapist_notes?: string;
  patient_notes?: string;
  clinical_scales?: Record<string, unknown>;
  adverse_events?: AdverseEvent[];
  created_at: string;
  updated_at: string;
}

export interface VitalsData {
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  heart_rate?: number;
  temperature?: number;
  spo2?: number;
  recorded_at: string;
}

export interface AdverseEvent {
  description: string;
  severity: 'mild' | 'moderate' | 'severe';
  reported_at: string;
  resolved: boolean;
}

export interface DashboardStats {
  total_patients: number;
  active_treatments: number;
  sessions_this_week: number;
  pending_documentation: number;
}
