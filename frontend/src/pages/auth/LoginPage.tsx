import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../hooks';
import { loginUser, clearError } from '../../store/authSlice';
import { Button, Input } from '../../components/common';

const LoginPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { loading, error, isAuthenticated } = useAppSelector((state) => state.auth);

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [formErrors, setFormErrors] = useState({
    email: '',
    password: '',
  });

  useEffect(() => {
    dispatch(clearError());
  }, [dispatch]);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const validateForm = (): boolean => {
    const errors = { email: '', password: '' };

    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email is invalid';
    }

    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }

    setFormErrors(errors);
    return !errors.email && !errors.password;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      await dispatch(loginUser(formData)).unwrap();
      navigate('/dashboard');
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (formErrors[name as keyof typeof formErrors]) {
      setFormErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Form */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-md w-full space-y-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">Welcome back</h1>
            <p className="mt-2 text-lg text-gray-600">
              Sign in to access your account
            </p>
          </div>

          <form onSubmit={handleSubmit} className="mt-8 space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <Input
              label="Email"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              error={formErrors.email}
              fullWidth
              autoComplete="email"
              placeholder="you@example.com"
              icon="📧"
            />

            <Input
              label="Password"
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              error={formErrors.password}
              fullWidth
              autoComplete="current-password"
              placeholder="Enter your password"
              icon="🔒"
            />

            <Button
              type="submit"
              variant="gradient"
              fullWidth
              loading={loading}
              disabled={loading}
            >
              Sign In
            </Button>

            <div className="text-center text-sm">
              <span className="text-gray-600">Don't have an account? </span>
              <Link to="/register" className="text-teal-600 hover:text-teal-700 font-semibold">
                Register here
              </Link>
            </div>
          </form>
        </div>
      </div>

      {/* Right Side - Gradient */}
      <div className="hidden lg:flex flex-1 bg-gradient-to-br from-teal-600 via-cyan-600 to-blue-600 items-center justify-center p-12 relative overflow-hidden">
        {/* Animated background elements */}
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>

        <div className="relative z-10 max-w-lg text-white">
          <h2 className="text-4xl font-bold mb-6">
            Evidence-Based Protocol Management
          </h2>
          <p className="text-xl mb-8 text-white/90">
            Access 91+ scientifically-validated protocols across 20+ therapy types. Trusted by healthcare professionals worldwide.
          </p>
          <div className="space-y-4">
            {[
              { icon: '✓', text: 'HIPAA Compliant & Secure' },
              { icon: '✓', text: 'AI-Powered Clinical Decision Support' },
              { icon: '✓', text: 'Real-time Session Documentation' },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center font-bold">
                  {item.icon}
                </div>
                <span className="text-lg">{item.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
