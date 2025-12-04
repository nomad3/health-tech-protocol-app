import React from 'react';
import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import { Navigation } from './components/common';
import { useAppSelector } from './hooks';
import ProtocolBuilder from './pages/admin/ProtocolBuilder';
import ProtocolManagement from './pages/admin/ProtocolManagement';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import LandingPage from './pages/LandingPage';
import ProtocolBrowser from './pages/patient/ProtocolBrowser';
import TherapistDashboard from './pages/therapist/TherapistDashboard';

// Import SessionDocumentation component dynamically to avoid type-only import error
const SessionDocumentation = React.lazy(() => import('./pages/therapist/SessionDocumentation'));
const PreScreeningPage = React.lazy(() => import('./pages/patient/PreScreeningPage'));
const TreatmentPlanDetail = React.lazy(() => import('./pages/patient/TreatmentPlanDetail'));
const ProtocolDetailPage = React.lazy(() => import('./pages/patient/ProtocolDetailPage'));
const PatientDetail = React.lazy(() => import('./pages/therapist/PatientDetail'));

// Protected route component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAppSelector((state) => state.auth);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Layout component with navigation
const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <>
      <Navigation />
      {children}
    </>
  );
};

function App() {
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected routes with navigation */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <DashboardPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/protocols"
          element={
            <ProtectedRoute>
              <Layout>
                <ProtocolBrowser />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/protocols/:id"
          element={
            <ProtectedRoute>
              <Layout>
                <React.Suspense fallback={<div>Loading...</div>}>
                  <ProtocolDetailPage />
                </React.Suspense>
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/protocols/:id/pre-screening"
          element={
            <ProtectedRoute>
              <Layout>
                <React.Suspense fallback={<div>Loading...</div>}>
                  <PreScreeningPage />
                </React.Suspense>
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/treatment/:id"
          element={
            <ProtectedRoute>
              <Layout>
                <React.Suspense fallback={<div>Loading...</div>}>
                  <TreatmentPlanDetail />
                </React.Suspense>
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/therapist/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <TherapistDashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/therapist/session/:id"
          element={
            <ProtectedRoute>
              <Layout>
                <React.Suspense fallback={<div>Loading...</div>}>
                  <SessionDocumentation />
                </React.Suspense>
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/therapist/patients/:id"
          element={
            <ProtectedRoute>
              <Layout>
                <React.Suspense fallback={<div>Loading...</div>}>
                  <PatientDetail />
                </React.Suspense>
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/protocols"
          element={
            <ProtectedRoute>
              <Layout>
                <ProtocolManagement />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/protocols/new"
          element={
            <ProtectedRoute>
              <Layout>
                <ProtocolBuilder />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/protocols/:id/edit"
          element={
            <ProtectedRoute>
              <Layout>
                <ProtocolBuilder />
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
