import type { DashboardStats, Patient, PatientDetailResponse, TherapySession } from '../types/therapist';
import { api } from './api';

export const therapistService = {
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/api/v1/therapist/dashboard');
    return response.data;
  },

  getPatients: async (): Promise<Patient[]> => {
    const response = await api.get('/api/v1/therapist/patients');
    return response.data;
  },

  getPatientDetails: async (id: number): Promise<PatientDetailResponse> => {
    const response = await api.get<PatientDetailResponse>(`/api/v1/therapist/patients/${id}`);
    return response.data;
  },

  getTodaySessions: async (): Promise<TherapySession[]> => {
    const response = await api.get('/api/v1/therapist/sessions/today');
    return response.data;
  },
};
