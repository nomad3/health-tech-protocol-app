import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Avatar, Button, Card, Spinner, StatusBadge } from '../../components/common';
import { api } from '../../services/api';
import type { Patient, TreatmentPlan } from '../../types/therapist';

interface PatientDetail extends Patient {
  treatment_plans?: TreatmentPlan[];
}

const PatientDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [patient, setPatient] = useState<PatientDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPatientDetails();
  }, [id]);

  const fetchPatientDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Implement this endpoint in backend
      // For now, we might fail or need to mock if backend doesn't have it
      const response = await api.get<PatientDetail>(`/api/v1/therapist/patients/${id}`);
      setPatient(response.data);
    } catch (err: any) {
      console.error('Patient detail error:', err);
      // Fallback for now if endpoint doesn't exist, try to find in list
      try {
        const listRes = await api.get<Patient[]>('/api/v1/therapist/patients');
        const found = listRes.data.find(p => p.id === Number(id));
        if (found) {
          setPatient(found);
          setError(null);
        } else {
          setError('Patient not found');
        }
      } catch (fallbackErr) {
        setError('Failed to load patient details');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50">
        <Spinner size="lg" />
        <p className="mt-4 text-gray-600 font-medium">Loading patient details...</p>
      </div>
    );
  }

  if (error || !patient) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50 py-12">
        <div className="max-w-4xl mx-auto px-4">
          <Card>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">⚠️</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to Load Patient</h2>
              <p className="text-gray-600 mb-6">{error || 'Patient not found'}</p>
              <Button onClick={() => navigate('/therapist/dashboard')}>Back to Dashboard</Button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/therapist/dashboard')}
            className="mb-4"
          >
            ← Back to Dashboard
          </Button>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <Avatar
                name={`${patient.first_name} ${patient.last_name}`}
                size="lg"
              />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  {patient.first_name} {patient.last_name}
                </h1>
                <p className="text-gray-600">{patient.email}</p>
              </div>
            </div>
            <StatusBadge status={patient.status} size="lg" />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <h2 className="text-xl font-bold text-gray-900 mb-4">Treatment History</h2>
              <p className="text-gray-500 italic">No treatment history available.</p>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <Card>
              <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
              <div className="space-y-2">
                <Button className="w-full" variant="outline">Edit Profile</Button>
                <Button className="w-full" variant="outline">Assign Protocol</Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientDetail;
