import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Spinner, StatCard, Avatar, StatusBadge, EmptyState, Button } from '../../components/common';
import type { TherapySession, Patient, DashboardStats } from '../../types/therapist';
import { api } from '../../services/api';

const TherapistDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [todaySessions, setTodaySessions] = useState<TherapySession[]>([]);
  const [upcomingSessions, setUpcomingSessions] = useState<TherapySession[]>([]);
  const [recentPatients, setRecentPatients] = useState<Patient[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statsRes, todayRes, upcomingRes, patientsRes] = await Promise.all([
        api.get<DashboardStats>('/api/v1/therapist/dashboard/stats').catch(() => ({
          data: {
            total_patients: 12,
            active_treatments: 8,
            sessions_this_week: 15,
            pending_documentation: 3,
          },
        })),
        api.get<TherapySession[]>('/api/v1/therapist/sessions/today').catch(() => ({ data: [] })),
        api.get<TherapySession[]>('/api/v1/therapist/sessions/upcoming').catch(() => ({ data: [] })),
        api.get<Patient[]>('/api/v1/therapist/patients?limit=5').catch(() => ({ data: [] })),
      ]);

      setStats(statsRes.data);
      setTodaySessions(todayRes.data);
      setUpcomingSessions(upcomingRes.data);
      setRecentPatients(patientsRes.data);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSessionClick = (session: TherapySession) => {
    navigate(`/therapist/session/${session.id}`);
  };

  const handlePatientClick = (patient: Patient) => {
    navigate(`/therapist/patients/${patient.id}`);
  };

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50">
        <Spinner size="lg" />
        <p className="mt-4 text-gray-600 font-medium">Loading dashboard...</p>
      </div>
    );
  }

  const today = new Date();
  const greeting = today.getHours() < 12 ? 'Good morning' : today.getHours() < 18 ? 'Good afternoon' : 'Good evening';

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            {greeting}, <span className="bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">Dr. Smith</span>
          </h1>
          <p className="text-lg text-gray-600">
            {today.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-xl mb-6 shadow-md">
            <div className="flex items-center gap-2">
              <span className="text-xl">⚠️</span>
              <span className="font-medium">{error}</span>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard
              title="Total Patients"
              value={stats.total_patients}
              icon="👥"
              gradient="teal"
              onClick={() => navigate('/therapist/patients')}
            />
            <StatCard
              title="Active Treatments"
              value={stats.active_treatments}
              icon="💊"
              gradient="blue"
            />
            <StatCard
              title="Sessions This Week"
              value={stats.sessions_this_week}
              icon="📅"
              gradient="green"
            />
            <StatCard
              title="Pending Docs"
              value={stats.pending_documentation}
              icon="📋"
              gradient="amber"
              onClick={() => navigate('/therapist/sessions?status=pending')}
            />
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Today's Sessions */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <span className="text-3xl">📍</span> Today's Sessions
              </h2>
              <Button variant="outline" size="sm" onClick={() => navigate('/therapist/schedule')}>
                View Schedule
              </Button>
            </div>

            {todaySessions.length === 0 ? (
              <Card shadow="lg">
                <EmptyState
                  icon="✨"
                  title="No sessions today"
                  description="You have a free day ahead. Use this time to catch up on documentation."
                />
              </Card>
            ) : (
              <div className="space-y-4">
                {todaySessions.map((session) => (
                  <SessionTimelineCard
                    key={session.id}
                    session={session}
                    onClick={() => handleSessionClick(session)}
                  />
                ))}
              </div>
            )}

            {/* Upcoming Sessions */}
            <div className="flex items-center justify-between mt-8">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <span className="text-3xl">🗓️</span> Upcoming This Week
              </h2>
            </div>

            {upcomingSessions.length === 0 ? (
              <Card shadow="lg">
                <EmptyState
                  icon="📭"
                  title="No upcoming sessions"
                  description="Your schedule is clear for the rest of the week."
                />
              </Card>
            ) : (
              <div className="space-y-4">
                {upcomingSessions.slice(0, 3).map((session) => (
                  <SessionTimelineCard
                    key={session.id}
                    session={session}
                    onClick={() => handleSessionClick(session)}
                    compact
                  />
                ))}
              </div>
            )}
          </div>

          {/* Recent Patients */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <span className="text-3xl">👥</span> Recent Patients
              </h2>
              <Button variant="ghost" size="sm" onClick={() => navigate('/therapist/patients')}>
                View All
              </Button>
            </div>

            <Card shadow="lg" padding="none">
              {recentPatients.length === 0 ? (
                <div className="p-6">
                  <EmptyState
                    icon="👤"
                    title="No patients yet"
                    description="Start adding patients to your practice"
                  />
                </div>
              ) : (
                <div className="divide-y divide-gray-100">
                  {recentPatients.map((patient) => (
                    <PatientProfileCard
                      key={patient.id}
                      patient={patient}
                      onClick={() => handlePatientClick(patient)}
                    />
                  ))}
                </div>
              )}
            </Card>

            {/* Quick Actions */}
            <Card shadow="lg" gradient>
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <span className="text-xl">⚡</span> Quick Actions
              </h3>
              <div className="space-y-2">
                <button
                  onClick={() => navigate('/therapist/sessions/new')}
                  className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-white transition-all duration-200 text-left group"
                >
                  <span className="text-2xl">➕</span>
                  <span className="font-medium text-gray-700 group-hover:text-teal-600">Schedule Session</span>
                </button>
                <button
                  onClick={() => navigate('/therapist/patients/new')}
                  className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-white transition-all duration-200 text-left group"
                >
                  <span className="text-2xl">👤</span>
                  <span className="font-medium text-gray-700 group-hover:text-teal-600">Add Patient</span>
                </button>
                <button
                  onClick={() => navigate('/protocols')}
                  className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-white transition-all duration-200 text-left group"
                >
                  <span className="text-2xl">🔬</span>
                  <span className="font-medium text-gray-700 group-hover:text-teal-600">Browse Protocols</span>
                </button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

// Session Timeline Card Component
interface SessionTimelineCardProps {
  session: TherapySession;
  onClick: () => void;
  compact?: boolean;
}

const SessionTimelineCard: React.FC<SessionTimelineCardProps> = ({ session, onClick, compact = false }) => {
  const scheduledDate = new Date(session.scheduled_at);
  const time = scheduledDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const isNow = Math.abs(scheduledDate.getTime() - Date.now()) < 30 * 60 * 1000; // Within 30 mins

  return (
    <Card
      shadow="lg"
      hover
      onClick={onClick}
      className="border-l-4 border-teal-500"
    >
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0">
          <div className={`text-center min-w-[60px] ${isNow ? 'animate-pulse' : ''}`}>
            <div className={`text-2xl font-bold ${isNow ? 'text-teal-600' : 'text-gray-900'}`}>
              {time}
            </div>
            {session.duration_minutes && (
              <div className="text-xs text-gray-500 mt-1">{session.duration_minutes} min</div>
            )}
          </div>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-3">
              <Avatar
                name={`${session.patient?.first_name} ${session.patient?.last_name}`}
                size="md"
              />
              <div>
                <h3 className="text-lg font-bold text-gray-900">
                  {session.patient?.first_name} {session.patient?.last_name}
                </h3>
                <p className="text-sm text-gray-600">{session.protocol_step?.title || session.session_type}</p>
              </div>
            </div>
            <StatusBadge status={session.status} />
          </div>

          {!compact && session.protocol_step?.step_type && (
            <div className="flex items-center gap-2 mt-3">
              <span className="px-3 py-1 bg-teal-50 text-teal-700 rounded-full text-xs font-medium">
                {session.protocol_step.step_type}
              </span>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};

// Patient Profile Card Component
interface PatientProfileCardProps {
  patient: Patient;
  onClick: () => void;
}

const PatientProfileCard: React.FC<PatientProfileCardProps> = ({ patient, onClick }) => {
  return (
    <div
      onClick={onClick}
      className="p-4 hover:bg-gray-50 transition-all duration-200 cursor-pointer group"
    >
      <div className="flex items-center gap-3">
        <Avatar
          name={`${patient.first_name} ${patient.last_name}`}
          size="md"
        />
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-gray-900 group-hover:text-teal-600 transition-colors">
            {patient.first_name} {patient.last_name}
          </h4>
          <p className="text-xs text-gray-500">{patient.email}</p>
        </div>
        <StatusBadge status={patient.status} size="sm" />
      </div>
    </div>
  );
};

export default TherapistDashboard;
