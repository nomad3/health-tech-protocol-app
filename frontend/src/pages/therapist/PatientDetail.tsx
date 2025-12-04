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
            {/* Treatment History */}
            <Card>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Treatment History</h2>
                <Button size="sm" variant="outline">View All History</Button>
              </div>

              {patient.treatment_plans && patient.treatment_plans.length > 0 ? (
                <div className="space-y-4">
                  {patient.treatment_plans.map((plan) => (
                    <div key={plan.id} className="border border-gray-200 rounded-xl p-4 hover:border-teal-200 transition-colors">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-bold text-gray-900">{plan.protocol_name || 'Unknown Protocol'}</h3>
                          <p className="text-sm text-gray-500">Started {new Date(plan.start_date).toLocaleDateString()}</p>
                        </div>
                        <StatusBadge status={plan.status} />
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-600 mt-3">
                        <div className="flex items-center gap-1">
                          <span>📅</span>
                          <span>Current Step: {plan.current_step || 1}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span>🔄</span>
                          <span>Progress: {plan.progress_percentage || 0}%</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
                  <span className="text-4xl mb-2 block">📋</span>
                  <p className="text-gray-500 font-medium">No active treatment plans</p>
                  <Button variant="ghost" size="sm" className="mt-2 text-teal-600">Assign Protocol</Button>
                </div>
              )}
            </Card>

            {/* Clinical Notes */}
            <Card>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Clinical Notes</h2>
                <Button size="sm" variant="gradient">+ New Note</Button>
              </div>
              <div className="space-y-4">
                <div className="bg-yellow-50 p-4 rounded-xl border border-yellow-100">
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-xs font-bold text-yellow-800 uppercase tracking-wide">Latest Note</span>
                    <span className="text-xs text-yellow-700">Today, 9:30 AM</span>
                  </div>
                  <p className="text-gray-800 text-sm leading-relaxed">
                    Patient reported improved sleep quality after the first integration session. Expressed some anxiety about the upcoming dosing session but feels prepared.
                  </p>
                </div>
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Patient Info */}
            <Card>
              <h2 className="text-lg font-bold text-gray-900 mb-4">Patient Information</h2>
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-semibold text-gray-500 uppercase">Date of Birth</label>
                  <p className="text-gray-900 font-medium">Jan 15, 1985 (39 yrs)</p>
                </div>
                <div>
                  <label className="text-xs font-semibold text-gray-500 uppercase">Phone</label>
                  <p className="text-gray-900 font-medium">+1 (555) 123-4567</p>
                </div>
                <div>
                  <label className="text-xs font-semibold text-gray-500 uppercase">Emergency Contact</label>
                  <p className="text-gray-900 font-medium">Sarah Smith (Spouse)</p>
                  <p className="text-gray-500 text-sm">+1 (555) 987-6543</p>
                </div>
              </div>
            </Card>

            {/* Quick Actions */}
            <Card>
              <h2 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <Button className="w-full justify-start" variant="outline">
                  <span className="mr-2">📝</span> Schedule Session
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  <span className="mr-2">💊</span> Prescribe Medication
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  <span className="mr-2">📧</span> Send Message
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientDetail;
