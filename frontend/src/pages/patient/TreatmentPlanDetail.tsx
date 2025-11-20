import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button, Card, ProgressBar, Spinner, StatusBadge } from '../../components/common';
import { api } from '../../services/api';

interface TreatmentPlan {
  id: number;
  protocol_id: number;
  protocol_name: string;
  protocol_description?: string;
  status: string;
  start_date: string;
  estimated_completion?: string;
  therapist_name?: string;
  current_step?: number;
  total_steps?: number;
  progress_percentage?: number;
  sessions?: Session[];
  notes?: string;
}

interface Session {
  id: number;
  session_number: number;
  scheduled_at?: string;
  completed_at?: string;
  status: string;
  step_title?: string;
  notes?: string;
}

const TreatmentPlanDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [plan, setPlan] = useState<TreatmentPlan | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTreatmentPlan();
  }, [id]);

  const fetchTreatmentPlan = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get<TreatmentPlan>(`/api/v1/patients/treatment-plans/${id}`);
      setPlan(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load treatment plan');
      console.error('Treatment plan error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50">
        <Spinner size="lg" />
        <p className="mt-4 text-gray-600 font-medium">Loading treatment plan...</p>
      </div>
    );
  }

  if (error || !plan) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50 py-12">
        <div className="max-w-4xl mx-auto px-4">
          <Card>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">⚠️</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to Load Treatment Plan</h2>
              <p className="text-gray-600 mb-6">{error || 'Treatment plan not found'}</p>
              <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  const progressPercentage = plan.progress_percentage ||
    (plan.current_step && plan.total_steps ? (plan.current_step / plan.total_steps) * 100 : 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/dashboard')}
            className="mb-4"
          >
            ← Back to Dashboard
          </Button>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">{plan.protocol_name}</h1>
              <p className="text-lg text-gray-600">Treatment Plan Details</p>
            </div>
            <StatusBadge status={plan.status} size="lg" />
          </div>
        </div>

        {/* Progress Overview */}
        <Card className="mb-6" gradient>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Progress Overview</h2>
            <span className="text-3xl font-bold bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">
              {Math.round(progressPercentage)}%
            </span>
          </div>
          <ProgressBar value={progressPercentage} size="lg" />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center gap-2 text-gray-600 text-sm mb-1">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Started
              </div>
              <p className="text-lg font-semibold text-gray-900">
                {new Date(plan.start_date).toLocaleDateString()}
              </p>
            </div>

            {plan.estimated_completion && (
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="flex items-center gap-2 text-gray-600 text-sm mb-1">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Est. Completion
                </div>
                <p className="text-lg font-semibold text-gray-900">
                  {new Date(plan.estimated_completion).toLocaleDateString()}
                </p>
              </div>
            )}

            {plan.therapist_name && (
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="flex items-center gap-2 text-gray-600 text-sm mb-1">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  Therapist
                </div>
                <p className="text-lg font-semibold text-gray-900">{plan.therapist_name}</p>
              </div>
            )}
          </div>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sessions Timeline */}
          <div className="lg:col-span-2">
            <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span className="text-3xl">📋</span> Sessions
            </h2>

            {!plan.sessions || plan.sessions.length === 0 ? (
              <Card>
                <div className="text-center py-12">
                  <div className="text-5xl mb-4">📅</div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">No Sessions Yet</h3>
                  <p className="text-gray-600">Your therapist will schedule sessions for your treatment plan.</p>
                </div>
              </Card>
            ) : (
              <div className="space-y-4">
                {plan.sessions.map((session) => (
                  <Card
                    key={session.id}
                    hover
                    className={`border-l-4 ${session.status === 'completed'
                        ? 'border-green-500'
                        : session.status === 'scheduled'
                          ? 'border-blue-500'
                          : 'border-gray-300'
                      }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="text-2xl font-bold text-gray-900">
                            Session {session.session_number}
                          </span>
                          <StatusBadge status={session.status} size="sm" />
                        </div>

                        {session.step_title && (
                          <p className="text-gray-700 font-medium mb-2">{session.step_title}</p>
                        )}

                        <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                          {session.scheduled_at && (
                            <div className="flex items-center gap-1">
                              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                              {new Date(session.scheduled_at).toLocaleString()}
                            </div>
                          )}
                          {session.completed_at && (
                            <div className="flex items-center gap-1 text-green-600">
                              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              Completed {new Date(session.completed_at).toLocaleDateString()}
                            </div>
                          )}
                        </div>

                        {session.notes && (
                          <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                            <p className="text-sm text-gray-700">{session.notes}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Protocol Info */}
            <Card>
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <span className="text-xl">ℹ️</span> Protocol Information
              </h3>
              {plan.protocol_description && (
                <p className="text-gray-700 text-sm leading-relaxed mb-4">
                  {plan.protocol_description}
                </p>
              )}
              {plan.total_steps && (
                <div className="flex items-center justify-between py-2 border-t border-gray-100">
                  <span className="text-sm text-gray-600">Total Steps</span>
                  <span className="font-semibold text-gray-900">{plan.total_steps}</span>
                </div>
              )}
              {plan.current_step && (
                <div className="flex items-center justify-between py-2 border-t border-gray-100">
                  <span className="text-sm text-gray-600">Current Step</span>
                  <span className="font-semibold text-teal-600">{plan.current_step}</span>
                </div>
              )}
            </Card>

            {/* Notes */}
            {plan.notes && (
              <Card gradient>
                <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <span className="text-xl">📝</span> Notes
                </h3>
                <p className="text-gray-700 text-sm leading-relaxed">{plan.notes}</p>
              </Card>
            )}

            {/* Actions */}
            <Card>
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <span className="text-xl">⚡</span> Quick Actions
              </h3>
              <div className="space-y-2">
                <Button
                  variant="gradient"
                  className="w-full"
                  onClick={() => navigate(`/protocols/${plan.protocol_id}`)}
                >
                  View Protocol Details
                </Button>
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => navigate('/dashboard')}
                >
                  Back to Dashboard
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TreatmentPlanDetail;
