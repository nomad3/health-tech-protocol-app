import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Spinner } from '../../components/common';
import SessionCard from '../../components/therapist/SessionCard';
import PatientList from '../../components/therapist/PatientList';
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

      // In a real app, these would be actual API calls
      // For now, we'll use mock data
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
      <div className="flex justify-center items-center min-h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Therapist Dashboard</h1>
          <p className="text-gray-600">
            {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <div className="text-center">
                <p className="text-sm font-medium text-gray-600">Total Patients</p>
                <p className="text-3xl font-bold text-teal-600 mt-2">{stats.total_patients}</p>
              </div>
            </Card>
            <Card>
              <div className="text-center">
                <p className="text-sm font-medium text-gray-600">Active Treatments</p>
                <p className="text-3xl font-bold text-blue-600 mt-2">{stats.active_treatments}</p>
              </div>
            </Card>
            <Card>
              <div className="text-center">
                <p className="text-sm font-medium text-gray-600">Sessions This Week</p>
                <p className="text-3xl font-bold text-green-600 mt-2">{stats.sessions_this_week}</p>
              </div>
            </Card>
            <Card>
              <div className="text-center">
                <p className="text-sm font-medium text-gray-600">Pending Docs</p>
                <p className="text-3xl font-bold text-amber-600 mt-2">{stats.pending_documentation}</p>
              </div>
            </Card>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Today's Sessions */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">Today's Sessions</h2>
            {todaySessions.length === 0 ? (
              <Card>
                <p className="text-gray-500 text-center py-8">No sessions scheduled for today</p>
              </Card>
            ) : (
              <div className="space-y-4">
                {todaySessions.map((session) => (
                  <SessionCard
                    key={session.id}
                    session={session}
                    onClick={() => handleSessionClick(session)}
                  />
                ))}
              </div>
            )}

            {/* Upcoming Sessions */}
            <h2 className="text-xl font-semibold text-gray-900 mt-8">Upcoming Sessions</h2>
            {upcomingSessions.length === 0 ? (
              <Card>
                <p className="text-gray-500 text-center py-8">No upcoming sessions</p>
              </Card>
            ) : (
              <div className="space-y-4">
                {upcomingSessions.map((session) => (
                  <SessionCard
                    key={session.id}
                    session={session}
                    onClick={() => handleSessionClick(session)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Recent Patients */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">Recent Patients</h2>
            <PatientList patients={recentPatients} onPatientClick={handlePatientClick} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TherapistDashboard;
