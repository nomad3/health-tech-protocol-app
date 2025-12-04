import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Card, StatusBadge } from '../components/common';
import { useAppDispatch, useAppSelector } from '../hooks';
import { protocolService } from '../services/protocolService';
import { logoutUser } from '../store/authSlice';

const DashboardPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { user, loading } = useAppSelector((state) => state.auth);
  const [treatmentPlans, setTreatmentPlans] = React.useState<any[]>([]);

  React.useEffect(() => {
    const fetchPlans = async () => {
      try {
        const plans = await protocolService.getTreatmentPlans();
        setTreatmentPlans(plans);
      } catch (error) {
        console.error('Failed to fetch treatment plans', error);
      }
    };

    if (user) {
      fetchPlans();
    }
  }, [user]);

  const handleLogout = async () => {
    await dispatch(logoutUser());
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-bold text-gray-900">Health Protocol</h1>
            <Button variant="secondary" onClick={handleLogout} disabled={loading}>
              Logout
            </Button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="col-span-1">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Profile</h2>
              <div className="space-y-2">
                <p className="text-gray-600">
                  <span className="font-medium">Email:</span> {user?.email}
                </p>
                <p className="text-gray-600">
                  <span className="font-medium">Role:</span> {user?.role}
                </p>
                <p className="text-gray-600">
                  <span className="font-medium">Status:</span>{' '}
                  {user?.is_active ? 'Active' : 'Inactive'}
                </p>
              </div>
            </Card>

            <div className="col-span-1 md:col-span-2">
              <Card>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">My Treatment Plans</h2>
                  <Button variant="outline" size="sm" onClick={() => navigate('/protocols')}>
                    Browse More
                  </Button>
                </div>
                {treatmentPlans.length === 0 ? (
                  <div className="text-center py-12 bg-gradient-to-br from-teal-50 to-blue-50 rounded-lg border-2 border-dashed border-teal-200">
                    <svg className="mx-auto h-12 w-12 text-teal-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p className="text-gray-600 mb-2 font-medium">No active treatment plans yet</p>
                    <p className="text-gray-500 text-sm mb-6">Start your healing journey by exploring our evidence-based protocols</p>
                    <Button variant="gradient" onClick={() => navigate('/protocols')}>
                      Explore Protocols
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {treatmentPlans.map((plan) => (
                      <div
                        key={plan.id}
                        className="group relative border border-gray-200 rounded-xl p-5 hover:border-teal-300 hover:shadow-lg transition-all duration-200 bg-white overflow-hidden"
                      >
                        {/* Gradient accent */}
                        <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-teal-400 to-blue-500"></div>

                        <div className="flex justify-between items-start ml-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="font-bold text-lg text-gray-900 group-hover:text-teal-600 transition-colors">
                                {plan.protocol_name}
                              </h3>
                              <StatusBadge status={plan.status} size="sm" />
                            </div>

                            <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-3">
                              <div className="flex items-center gap-1">
                                <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                                <span>Started {new Date(plan.start_date).toLocaleDateString()}</span>
                              </div>

                              {plan.therapist_name && (
                                <div className="flex items-center gap-1">
                                  <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                  </svg>
                                  <span>{plan.therapist_name}</span>
                                </div>
                              )}
                            </div>

                            {plan.estimated_completion && (
                              <div className="flex items-center gap-2 text-xs text-gray-500">
                                <span>Est. completion:</span>
                                <span className="font-medium">{new Date(plan.estimated_completion).toLocaleDateString()}</span>
                              </div>
                            )}
                          </div>

                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => navigate(`/treatment/${plan.id}`)}
                            className="group-hover:border-teal-500 group-hover:text-teal-600 transition-colors"
                          >
                            View Details →
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;
