import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../hooks';
import { logoutUser, clearAuth } from '../../store/authSlice';
import Button from './Button';

const Navigation: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    dispatch(logoutUser());
    dispatch(clearAuth());
    navigate('/login');
  };

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  if (!isAuthenticated) {
    return null;
  }

  const navLinks = {
    patient: [
      { path: '/protocols', label: 'Browse Protocols', icon: '📚' },
      { path: '/dashboard', label: 'My Journey', icon: '🌟' },
    ],
    therapist: [
      { path: '/therapist/dashboard', label: 'Dashboard', icon: '📊' },
      { path: '/protocols', label: 'Protocols', icon: '📚' },
    ],
    clinic_admin: [
      { path: '/admin/protocols', label: 'Manage Protocols', icon: '⚙️' },
      { path: '/therapist/dashboard', label: 'Dashboard', icon: '📊' },
      { path: '/protocols', label: 'Protocols', icon: '📚' },
    ],
    medical_director: [
      { path: '/admin/protocols', label: 'Manage Protocols', icon: '⚙️' },
      { path: '/therapist/dashboard', label: 'Dashboard', icon: '📊' },
      { path: '/protocols', label: 'Protocols', icon: '📚' },
    ],
    platform_admin: [
      { path: '/admin/protocols', label: 'Manage Protocols', icon: '⚙️' },
      { path: '/therapist/dashboard', label: 'Dashboard', icon: '📊' },
      { path: '/protocols', label: 'Protocols', icon: '📚' },
    ],
  };

  const userRole = user?.role || 'patient';
  const links = navLinks[userRole as keyof typeof navLinks] || navLinks.patient;

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo and primary nav */}
          <div className="flex">
            {/* Logo */}
            <Link to="/dashboard" className="flex items-center">
              <span className="text-2xl font-bold text-teal-600">PsyProtocol</span>
            </Link>

            {/* Desktop navigation */}
            <div className="hidden md:ml-10 md:flex md:space-x-8">
              {links.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                    isActive(link.path)
                      ? 'border-teal-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  }`}
                >
                  <span className="mr-2">{link.icon}</span>
                  {link.label}
                </Link>
              ))}
            </div>
          </div>

          {/* User menu */}
          <div className="hidden md:flex md:items-center md:space-x-4">
            {user && (
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{user.email}</p>
                  <p className="text-xs text-gray-500 capitalize">{user.role.replace('_', ' ')}</p>
                </div>
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  Logout
                </Button>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex items-center md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
            >
              <span className="sr-only">Open main menu</span>
              {mobileMenuOpen ? (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="md:hidden">
          <div className="pt-2 pb-3 space-y-1">
            {links.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`block pl-3 pr-4 py-2 border-l-4 text-base font-medium ${
                  isActive(link.path)
                    ? 'bg-teal-50 border-teal-500 text-teal-700'
                    : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'
                }`}
              >
                <span className="mr-2">{link.icon}</span>
                {link.label}
              </Link>
            ))}
          </div>
          <div className="pt-4 pb-3 border-t border-gray-200">
            {user && (
              <div className="px-4">
                <div className="text-base font-medium text-gray-800">{user.email}</div>
                <div className="text-sm text-gray-500 capitalize">{user.role.replace('_', ' ')}</div>
                <Button variant="outline" size="sm" onClick={handleLogout} className="mt-3 w-full">
                  Logout
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navigation;
