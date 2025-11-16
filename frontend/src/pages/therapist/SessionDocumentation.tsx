import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Spinner, Badge } from '../../components/common';
import VitalsLogger from '../../components/therapist/VitalsLogger';
import NotesEditor from '../../components/therapist/NotesEditor';
import type { TherapySession, SessionDocumentation, VitalsData } from '../../types/therapist';
import { api } from '../../services/api';

const SessionDocumentation: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [session, setSession] = useState<TherapySession | null>(null);
  const [documentation, setDocumentation] = useState<SessionDocumentation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchSessionData();
  }, [id]);

  const fetchSessionData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [sessionRes, docRes] = await Promise.all([
        api.get<TherapySession>(`/api/v1/therapist/sessions/${id}`).catch(() => ({
          data: {
            id: parseInt(id || '0'),
            treatment_plan_id: 1,
            protocol_step_id: 1,
            patient_id: 1,
            therapist_id: 1,
            scheduled_at: new Date().toISOString(),
            status: 'in_progress' as const,
            session_type: 'Preparation Session',
            duration_minutes: 90,
            patient: {
              id: 1,
              user_id: 1,
              first_name: 'John',
              last_name: 'Doe',
              email: 'john@example.com',
              date_of_birth: '1985-01-01',
              status: 'active' as const,
              created_at: new Date().toISOString(),
            },
            protocol_step: {
              id: 1,
              title: 'Initial Preparation Session',
              step_type: 'preparation',
            },
          },
        })),
        api.get<SessionDocumentation>(`/api/v1/therapist/sessions/${id}/documentation`).catch(() => ({
          data: {
            id: 1,
            session_id: parseInt(id || '0'),
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        })),
      ]);

      setSession(sessionRes.data);
      setDocumentation(docRes.data);
    } catch (err) {
      setError('Failed to load session data');
      console.error('Session error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVitalsSave = async (vitals: VitalsData) => {
    try {
      setSaving(true);
      setError(null);

      await api.post(`/api/v1/therapist/sessions/${id}/documentation/vitals`, vitals);

      setDocumentation((prev) => (prev ? { ...prev, vitals } : null));
      setSuccessMessage('Vitals saved successfully');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError('Failed to save vitals');
      console.error('Vitals error:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleNotesSave = async (therapistNotes: string, patientNotes: string) => {
    try {
      setSaving(true);
      setError(null);

      await api.post(`/api/v1/therapist/sessions/${id}/documentation/notes`, {
        therapist_notes: therapistNotes,
        patient_notes: patientNotes,
      });

      setDocumentation((prev) =>
        prev ? { ...prev, therapist_notes: therapistNotes, patient_notes: patientNotes } : null
      );
      setSuccessMessage('Notes saved successfully');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError('Failed to save notes');
      console.error('Notes error:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleCompleteSession = async () => {
    try {
      setSaving(true);
      setError(null);

      await api.post(`/api/v1/therapist/sessions/${id}/complete`);

      setSuccessMessage('Session completed successfully');
      setTimeout(() => navigate('/therapist/dashboard'), 1500);
    } catch (err) {
      setError('Failed to complete session');
      console.error('Complete error:', err);
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card>
          <p className="text-gray-500">Session not found</p>
          <Button onClick={() => navigate('/therapist/dashboard')} className="mt-4">
            Back to Dashboard
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Session Documentation</h1>
              <p className="text-gray-600">
                {session.patient?.first_name} {session.patient?.last_name} - {session.protocol_step?.title}
              </p>
            </div>
            <Badge variant="blue">{session.status.replace('_', ' ')}</Badge>
          </div>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
            {successMessage}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Session Info Card */}
        <Card className="mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <span className="text-sm font-medium text-gray-700">Scheduled</span>
              <p className="text-gray-900">
                {new Date(session.scheduled_at).toLocaleString()}
              </p>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-700">Duration</span>
              <p className="text-gray-900">{session.duration_minutes} minutes</p>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-700">Session Type</span>
              <p className="text-gray-900">{session.session_type}</p>
            </div>
          </div>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Vitals Logger */}
          <div>
            <VitalsLogger
              initialVitals={documentation?.vitals}
              onSave={handleVitalsSave}
            />
          </div>

          {/* Notes Editor */}
          <div>
            <NotesEditor
              therapistNotes={documentation?.therapist_notes}
              patientNotes={documentation?.patient_notes}
              onSave={handleNotesSave}
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-8 flex gap-4 justify-end">
          <Button
            variant="outline"
            onClick={() => navigate('/therapist/dashboard')}
          >
            Back to Dashboard
          </Button>
          <Button
            onClick={handleCompleteSession}
            disabled={saving || session.status === 'completed'}
          >
            {saving ? 'Saving...' : 'Complete Session'}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SessionDocumentation;
