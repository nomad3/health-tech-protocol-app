import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Badge, Button, Card, Spinner } from '../../components/common';
import { api } from '../../services/api';
import type { Protocol, ProtocolStep, StepType } from '../../types/protocol';

const stepTypeIcons: Record<StepType, string> = {
  screening: '🔍',
  preparation: '📋',
  dosing: '💊',
  integration: '🧘',
  decision_point: '🔀',
  followup: '📞',
};

const stepTypeLabels: Record<StepType, string> = {
  screening: 'Screening',
  preparation: 'Preparation',
  dosing: 'Dosing Session',
  integration: 'Integration',
  decision_point: 'Decision Point',
  followup: 'Follow-up',
};

const ProtocolDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [protocol, setProtocol] = useState<Protocol | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProtocol();
  }, [id]);

  const fetchProtocol = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get<Protocol>(`/api/v1/protocols/${id}`);
      setProtocol(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load protocol');
      console.error('Protocol error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50">
        <Spinner size="lg" />
        <p className="mt-4 text-gray-600 font-medium">Loading protocol...</p>
      </div>
    );
  }

  if (error || !protocol) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50 py-12">
        <div className="max-w-4xl mx-auto px-4">
          <Card>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">⚠️</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to Load Protocol</h2>
              <p className="text-gray-600 mb-6">{error || 'Protocol not found'}</p>
              <Button onClick={() => navigate('/protocols')}>Back to Protocols</Button>
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
            onClick={() => navigate('/protocols')}
            className="mb-4"
          >
            ← Back to Protocols
          </Button>
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-3">{protocol.name}</h1>
              <div className="flex flex-wrap gap-2">
                <Badge variant="teal">{protocol.therapy_type.toUpperCase()}</Badge>
                <Badge variant="gray">{protocol.condition_treated.replace(/_/g, ' ')}</Badge>
                <Badge variant="blue">v{protocol.version}</Badge>
                <Badge variant={protocol.status === 'active' ? 'green' : 'amber'}>
                  {protocol.status}
                </Badge>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Overview */}
            {protocol.overview && (
              <Card>
                <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <span className="text-3xl">📖</span> Overview
                </h2>
                <p className="text-gray-700 leading-relaxed">{protocol.overview}</p>
              </Card>
            )}

            {/* Protocol Steps */}
            {protocol.steps && protocol.steps.length > 0 && (
              <Card>
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                  <span className="text-3xl">📋</span> Protocol Steps
                </h2>
                <div className="space-y-4">
                  {protocol.steps.map((step: ProtocolStep, index: number) => (
                    <div
                      key={step.id}
                      className="border border-gray-200 rounded-xl p-5 hover:border-teal-300 hover:shadow-md transition-all duration-200"
                    >
                      <div className="flex items-start gap-4">
                        <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-teal-500 to-cyan-500 rounded-full flex items-center justify-center text-white font-bold shadow-md">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-2xl">{stepTypeIcons[step.step_type]}</span>
                            <h3 className="font-bold text-lg text-gray-900">{step.title}</h3>
                            <Badge variant="gray" className="text-xs">
                              {stepTypeLabels[step.step_type]}
                            </Badge>
                          </div>
                          {step.description && (
                            <p className="text-gray-600 mb-3 leading-relaxed">{step.description}</p>
                          )}
                          <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                            {step.duration_minutes && (
                              <div className="flex items-center gap-1">
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span>{step.duration_minutes} minutes</span>
                              </div>
                            )}
                            {step.safety_checks && step.safety_checks.length > 0 && (
                              <div className="flex items-center gap-1">
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                </svg>
                                <span>{step.safety_checks.length} safety checks</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Evidence Sources */}
            {protocol.evidence_sources && protocol.evidence_sources.length > 0 && (
              <Card>
                <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <span className="text-3xl">📚</span> Evidence Sources
                </h2>
                <ul className="space-y-3">
                  {protocol.evidence_sources.map((source, index) => (
                    <li key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      <span className="text-teal-600 font-bold">{index + 1}.</span>
                      <div>
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-teal-600 hover:text-teal-700 font-medium underline"
                        >
                          {source.title}
                        </a>
                        <span className="text-gray-500 text-sm ml-2">({source.type})</span>
                      </div>
                    </li>
                  ))}
                </ul>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <Card gradient>
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <span className="text-xl">📊</span> Quick Stats
              </h3>
              <div className="space-y-3">
                {protocol.duration_weeks && (
                  <div className="flex items-center justify-between py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">Duration</span>
                    <span className="font-bold text-teal-600">{protocol.duration_weeks} weeks</span>
                  </div>
                )}
                {protocol.total_sessions && (
                  <div className="flex items-center justify-between py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">Total Sessions</span>
                    <span className="font-bold text-teal-600">{protocol.total_sessions}</span>
                  </div>
                )}
                <div className="flex items-center justify-between py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Evidence Level</span>
                  <span className="font-semibold text-gray-900 text-xs capitalize">
                    {protocol.evidence_level.replace(/_/g, ' ')}
                  </span>
                </div>
                {protocol.steps && (
                  <div className="flex items-center justify-between py-2">
                    <span className="text-sm text-gray-600">Protocol Steps</span>
                    <span className="font-bold text-teal-600">{protocol.steps.length}</span>
                  </div>
                )}
              </div>
            </Card>

            {/* Actions */}
            <Card>
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <span className="text-xl">⚡</span> Actions
              </h3>
              <div className="space-y-3">
                <Button
                  variant="gradient"
                  className="w-full"
                  onClick={() => navigate(`/protocols/${protocol.id}/pre-screening`)}
                >
                  Start Pre-Screening
                </Button>
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => navigate('/protocols')}
                >
                  Browse More Protocols
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProtocolDetailPage;
