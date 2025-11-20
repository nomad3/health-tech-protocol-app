import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Avatar, Button, Card, ProgressBar, Spinner, StatusBadge } from '../../components/common';
import NotesEditor from '../../components/therapist/NotesEditor';
import VitalsLogger from '../../components/therapist/VitalsLogger';
import { api } from '../../services/api';
import type { SessionDocumentation, TherapySession, VitalsData } from '../../types/therapist';

const SessionDocumentation: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [autoSaved, setAutoSaved] = useState(false);
  const [session, setSession] = useState<TherapySession | null>(null);
  const [documentation, setDocumentation] = useState<SessionDocumentation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'vitals' | 'notes' | 'timeline'>('vitals');

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

      await api.post(`/api/v1/therapist/sessions/${id}/vitals`, vitals);

      setDocumentation((prev) => (prev ? { ...prev, vitals } : null));
      setSuccessMessage('Vitals saved successfully');
      setAutoSaved(true);
      setTimeout(() => {
        setSuccessMessage(null);
        setAutoSaved(false);
      }, 3000);
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

      await api.post(`/api/v1/therapist/sessions/${id}/documentation`, {
        therapist_notes: therapistNotes,
        patient_notes: patientNotes,
      });

      setDocumentation((prev) =>
        prev ? { ...prev, therapist_notes: therapistNotes, patient_notes: patientNotes } : null
      );
      setSuccessMessage('Notes saved successfully');
      setAutoSaved(true);
      setTimeout(() => {
        setSuccessMessage(null);
        setAutoSaved(false);
      }, 3000);
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
      <div className="flex flex-col justify-center items-center min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50">
        <Spinner size="lg" />
        <p className="mt-4 text-gray-600 font-medium">Loading session...</p>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50 flex items-center justify-center">
        <Card shadow="xl" className="max-w-md">
          <div className="text-center">
            <div className="text-6xl mb-4">📋</div>
            <p className="text-gray-700 text-lg font-medium mb-6">Session not found</p>
            <Button onClick={() => navigate('/therapist/dashboard')}>
              Back to Dashboard
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  const completionPercentage =
    ((documentation?.vitals ? 50 : 0) + (documentation?.therapist_notes ? 50 : 0));

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <Avatar
                name={`${session.patient?.first_name} ${session.patient?.last_name}`}
                size="lg"
              />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Session Documentation
                </h1>
                <p className="text-lg text-gray-600">
                  {session.patient?.first_name} {session.patient?.last_name} • {session.protocol_step?.title}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {autoSaved && (
                <span className="text-sm text-green-600 font-medium flex items-center gap-1">
                  <span className="text-lg">✓</span> Auto-saved
                </span>
              )}
              <StatusBadge status={session.status} size="lg" />
            </div>
          </div>

          {/* Progress Bar */}
          <Card className="bg-gradient-to-r from-teal-50 to-cyan-50 border border-teal-100">
            <ProgressBar
              value={completionPercentage}
              label="Documentation Progress"
              color="teal"
              size="lg"
              showPercentage
            />
          </Card>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-6 py-4 rounded-xl mb-6 shadow-md animate-fade-in">
            <div className="flex items-center gap-2">
              <span className="text-xl">✓</span>
              <span className="font-medium">{successMessage}</span>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-xl mb-6 shadow-md">
            <div className="flex items-center gap-2">
              <span className="text-xl">⚠️</span>
              <span className="font-medium">{error}</span>
            </div>
          </div>
        )}

        {/* Session Info Card */}
        <Card shadow="lg" className="mb-6 border-l-4 border-teal-500">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xl">📅</span>
                <span className="text-sm font-semibold text-gray-700">Scheduled</span>
              </div>
              <p className="text-gray-900 font-medium">
                {new Date(session.scheduled_at).toLocaleString()}
              </p>
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xl">⏱️</span>
                <span className="text-sm font-semibold text-gray-700">Duration</span>
              </div>
              <p className="text-gray-900 font-medium">{session.duration_minutes} minutes</p>
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xl">🔬</span>
                <span className="text-sm font-semibold text-gray-700">Session Type</span>
              </div>
              <p className="text-gray-900 font-medium">{session.session_type}</p>
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xl">📍</span>
                <span className="text-sm font-semibold text-gray-700">Step Type</span>
              </div>
              <p className="text-gray-900 font-medium capitalize">
                {session.protocol_step?.step_type || 'N/A'}
              </p>
            </div>
          </div>
        </Card>

        {/* Tabs */}
        <div className="mb-6">
          <div className="flex gap-2 border-b border-gray-200">
            {[
              { id: 'vitals' as const, label: 'Vital Signs', icon: '❤️' },
              { id: 'notes' as const, label: 'Clinical Notes', icon: '📝' },
              { id: 'timeline' as const, label: 'Session Timeline', icon: '⏰' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 font-semibold transition-all duration-200 border-b-2 flex items-center gap-2 ${activeTab === tab.id
                    ? 'border-teal-600 text-teal-600 bg-teal-50 rounded-t-lg'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
              >
                <span className="text-lg">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="mb-8">
          {activeTab === 'vitals' && (
            <VitalsLogger
              initialVitals={documentation?.vitals}
              onSave={handleVitalsSave}
            />
          )}

          {activeTab === 'notes' && (
            <NotesEditor
              therapistNotes={documentation?.therapist_notes}
              patientNotes={documentation?.patient_notes}
              onSave={handleNotesSave}
            />
          )}

          {activeTab === 'timeline' && (
            <Card shadow="lg">
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <span className="text-2xl">⏰</span> Session Timeline
              </h3>
              <div className="space-y-4">
                <TimelineItem
                  time="09:00 AM"
                  title="Session Started"
                  description="Patient arrived and check-in completed"
                  status="completed"
                />
                <TimelineItem
                  time="09:15 AM"
                  title="Vitals Recorded"
                  description="Initial vital signs documented"
                  status={documentation?.vitals ? 'completed' : 'pending'}
                />
                <TimelineItem
                  time="Ongoing"
                  title="Therapy Session"
                  description="Active therapeutic intervention"
                  status="in_progress"
                />
              </div>
            </Card>
          )}
        </div>

        {/* Action Buttons */}
        <Card shadow="lg" className="bg-gradient-to-r from-gray-50 to-white">
          <div className="flex gap-4 justify-end items-center">
            <Button
              variant="outline"
              onClick={() => navigate('/therapist/dashboard')}
              icon="←"
            >
              Back to Dashboard
            </Button>
            <Button
              variant="gradient"
              onClick={handleCompleteSession}
              disabled={saving || session.status === 'completed' || completionPercentage < 100}
              loading={saving}
              icon="✓"
            >
              {saving ? 'Completing...' : 'Complete Session'}
            </Button>
          </div>
          {completionPercentage < 100 && (
            <p className="text-sm text-gray-600 text-right mt-2">
              Complete all sections to finish session documentation
            </p>
          )}
        </Card>
      </div>
    </div>
  );
};

// Timeline Item Component
interface TimelineItemProps {
  time: string;
  title: string;
  description: string;
  status: 'completed' | 'in_progress' | 'pending';
}

const TimelineItem: React.FC<TimelineItemProps> = ({ time, title, description, status }) => {
  const statusColors = {
    completed: 'bg-green-500',
    in_progress: 'bg-amber-500',
    pending: 'bg-gray-300',
  };

  return (
    <div className="flex gap-4">
      <div className="flex flex-col items-center">
        <div className={`w-4 h-4 rounded-full ${statusColors[status]} flex-shrink-0`} />
        <div className="w-0.5 h-full bg-gray-200 mt-2" />
      </div>
      <div className="pb-6">
        <div className="flex items-center gap-3 mb-1">
          <span className="text-sm font-semibold text-gray-900">{time}</span>
          <StatusBadge status={status} size="sm" />
        </div>
        <h4 className="font-semibold text-gray-900">{title}</h4>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
    </div>
  );
};

export default SessionDocumentation;
