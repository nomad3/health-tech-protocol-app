import {
  Activity,
  ArrowRight,
  ChevronRight,
  Heart,
  ShieldCheck,
  Sun,
  Users
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-x-hidden font-sans selection:bg-teal-500 selection:text-white">
      {/* Navigation */}
      <nav className={`fixed w-full z-50 transition-all duration-300 ${scrolled ? 'bg-slate-950/80 backdrop-blur-md border-b border-white/10 py-4' : 'bg-transparent py-6'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-400 to-blue-600 flex items-center justify-center">
              <Heart className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
              PsyProtocol
            </span>
          </div>
          <div className="hidden md:flex items-center space-x-8">
            <a href="#benefits" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Benefits</a>
            <a href="#approach" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Our Approach</a>
            <a href="#stories" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Success Stories</a>
            <button
              onClick={() => navigate('/login')}
              className="px-5 py-2 rounded-full bg-white/10 hover:bg-white/20 border border-white/10 text-sm font-medium transition-all backdrop-blur-sm"
            >
              Patient Login
            </button>
            <button
              onClick={() => navigate('/register')}
              className="px-5 py-2 rounded-full bg-gradient-to-r from-teal-500 to-blue-600 hover:from-teal-400 hover:to-blue-500 text-white text-sm font-medium shadow-lg shadow-teal-500/25 transition-all transform hover:scale-105"
            >
              Start Your Journey
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative min-h-screen flex items-center justify-center pt-20 overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 z-0">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-600/20 rounded-full mix-blend-screen filter blur-[128px] animate-pulse-slow"></div>
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-teal-600/20 rounded-full mix-blend-screen filter blur-[128px] animate-pulse-slow delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-600/5 rounded-full mix-blend-screen filter blur-[100px]"></div>

          {/* Grid Overlay */}
          <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950"></div>
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm mb-8 animate-fade-in-up">
            <span className="flex h-2 w-2 rounded-full bg-teal-400 animate-pulse"></span>
            <span className="text-xs font-medium text-teal-300 tracking-wide uppercase">Accepting New Patients for 2025</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 animate-fade-in-up delay-100">
            <span className="block text-white mb-2">Reclaim Your Life With</span>
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-teal-400 via-blue-500 to-purple-600 animate-gradient-x">
              Advanced Mental Healthcare
            </span>
          </h1>

          <p className="mt-4 text-xl text-slate-400 max-w-2xl mx-auto mb-10 animate-fade-in-up delay-200 leading-relaxed">
            Break free from Depression, PTSD, and Anxiety.
            Experience lasting relief through our evidence-based, personalized treatment programs designed for deep healing.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6 animate-fade-in-up delay-300">
            <button
              onClick={() => navigate('/register')}
              className="w-full sm:w-auto px-8 py-4 rounded-full bg-gradient-to-r from-teal-500 to-blue-600 hover:from-teal-400 hover:to-blue-500 text-white font-semibold shadow-lg shadow-teal-500/25 transition-all transform hover:scale-105 flex items-center justify-center group"
            >
              Check Eligibility
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            <button
              onClick={() => navigate('/protocols')}
              className="w-full sm:w-auto px-8 py-4 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-white font-semibold backdrop-blur-sm transition-all flex items-center justify-center"
            >
              View Programs
            </button>
          </div>

          {/* Stats/Trust Indicators */}
          <div className="mt-16 pt-8 border-t border-white/5 grid grid-cols-2 md:grid-cols-4 gap-8 animate-fade-in-up delay-500">
            <div>
              <div className="text-3xl font-bold text-white">85%</div>
              <div className="text-sm text-slate-500 mt-1">Patient Improvement</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white">100%</div>
              <div className="text-sm text-slate-500 mt-1">Clinician Led</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white">24/7</div>
              <div className="text-sm text-slate-500 mt-1">Care Support</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white">FDA</div>
              <div className="text-sm text-slate-500 mt-1">Aligned Standards</div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="benefits" className="relative py-24 bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Why Choose Advanced Care?</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Traditional treatments don't work for everyone. We offer a new path forward focused on root-cause healing and long-term resilience.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="group relative p-8 rounded-2xl bg-gradient-to-b from-white/5 to-white/[0.02] border border-white/10 hover:border-teal-500/30 transition-all duration-300 hover:-translate-y-1">
              <div className="absolute inset-0 bg-gradient-to-br from-teal-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl"></div>
              <div className="relative z-10">
                <div className="w-12 h-12 rounded-lg bg-teal-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Sun className="w-6 h-6 text-teal-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Lasting Breakthroughs</h3>
                <p className="text-slate-400 leading-relaxed">
                  Go beyond symptom management. Our protocols are designed to help you process trauma, shift perspectives, and achieve durable remission.
                </p>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="group relative p-8 rounded-2xl bg-gradient-to-b from-white/5 to-white/[0.02] border border-white/10 hover:border-blue-500/30 transition-all duration-300 hover:-translate-y-1">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl"></div>
              <div className="relative z-10">
                <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <ShieldCheck className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Safe, Guided Healing</h3>
                <p className="text-slate-400 leading-relaxed">
                  Your safety is our priority. Every step of your journey is monitored by medical professionals and supported by advanced safety protocols.
                </p>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="group relative p-8 rounded-2xl bg-gradient-to-b from-white/5 to-white/[0.02] border border-white/10 hover:border-purple-500/30 transition-all duration-300 hover:-translate-y-1">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl"></div>
              <div className="relative z-10">
                <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Heart className="w-6 h-6 text-purple-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Support Beyond the Session</h3>
                <p className="text-slate-400 leading-relaxed">
                  Healing continues after the treatment. We provide comprehensive integration support to help you apply your insights to daily life.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Visual Showcase Section */}
      <div className="py-24 bg-slate-950 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col lg:flex-row items-center gap-16">
            <div className="lg:w-1/2">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
                Your Path to <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-teal-400">Total Wellness</span>
              </h2>
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="mt-1 w-6 h-6 rounded-full bg-teal-500/20 flex items-center justify-center flex-shrink-0">
                    <Users className="w-3 h-3 text-teal-400" />
                  </div>
                  <div>
                    <h4 className="text-white font-semibold">Dedicated Care Team</h4>
                    <p className="text-slate-400 text-sm mt-1">You are never alone. Our network of compassionate therapists and medical experts is with you at every step.</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="mt-1 w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                    <Activity className="w-3 h-3 text-blue-400" />
                  </div>
                  <div>
                    <h4 className="text-white font-semibold">Personalized for You</h4>
                    <p className="text-slate-400 text-sm mt-1">No two journeys are alike. We tailor your treatment plan to your unique history, biology, and goals.</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="mt-1 w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                    <Heart className="w-3 h-3 text-purple-400" />
                  </div>
                  <div>
                    <h4 className="text-white font-semibold">Empowering Your Growth</h4>
                    <p className="text-slate-400 text-sm mt-1">We give you the tools, insights, and support to build a life of meaning, connection, and joy.</p>
                  </div>
                </div>
              </div>

              <button className="mt-8 text-teal-400 font-medium flex items-center hover:text-teal-300 transition-colors">
                Meet our clinical team <ChevronRight className="w-4 h-4 ml-1" />
              </button>
            </div>

            <div className="lg:w-1/2 relative">
              <div className="absolute -inset-4 bg-gradient-to-r from-teal-500 to-purple-600 rounded-2xl opacity-20 blur-2xl animate-pulse-slow"></div>
              <div className="relative bg-slate-900 rounded-xl border border-white/10 shadow-2xl overflow-hidden">
                {/* Mockup Header */}
                <div className="h-8 bg-slate-800 border-b border-white/5 flex items-center px-4 space-x-2">
                  <div className="w-3 h-3 rounded-full bg-red-500/50"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500/50"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500/50"></div>
                </div>
                {/* Mockup Content - Abstract representation of dashboard */}
                <div className="p-6 space-y-4">
                  <div className="flex justify-between items-center">
                    <div className="h-8 w-32 bg-white/10 rounded animate-pulse"></div>
                    <div className="h-8 w-8 bg-teal-500/20 rounded-full"></div>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="h-24 bg-white/5 rounded-lg border border-white/5 p-3">
                      <div className="h-2 w-12 bg-teal-500/40 rounded mb-2"></div>
                      <div className="h-6 w-8 bg-white/20 rounded"></div>
                    </div>
                    <div className="h-24 bg-white/5 rounded-lg border border-white/5 p-3">
                      <div className="h-2 w-12 bg-blue-500/40 rounded mb-2"></div>
                      <div className="h-6 w-8 bg-white/20 rounded"></div>
                    </div>
                    <div className="h-24 bg-white/5 rounded-lg border border-white/5 p-3">
                      <div className="h-2 w-12 bg-purple-500/40 rounded mb-2"></div>
                      <div className="h-6 w-8 bg-white/20 rounded"></div>
                    </div>
                  </div>
                  <div className="h-40 bg-white/5 rounded-lg border border-white/5 p-4 space-y-3">
                    <div className="h-4 w-1/3 bg-white/10 rounded"></div>
                    <div className="space-y-2">
                      <div className="h-2 w-full bg-white/5 rounded"></div>
                      <div className="h-2 w-5/6 bg-white/5 rounded"></div>
                      <div className="h-2 w-4/6 bg-white/5 rounded"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-slate-900 to-slate-950"></div>
        <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-full h-full max-w-4xl bg-teal-500/5 blur-[100px] rounded-full pointer-events-none"></div>

        <div className="relative z-10 max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">Begin Your Healing Journey</h2>
          <p className="text-xl text-slate-400 mb-10">
            Take the first step towards mental wellness with our evidence-based psychedelic therapy program.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <button
              onClick={() => navigate('/register')}
              className="w-full sm:w-auto px-10 py-4 rounded-full bg-white text-slate-900 font-bold hover:bg-slate-100 transition-colors shadow-lg shadow-white/10"
            >
              See If You Qualify
            </button>
            <button
              onClick={() => navigate('/contact')}
              className="w-full sm:w-auto px-10 py-4 rounded-full bg-transparent border border-white/20 text-white font-semibold hover:bg-white/5 transition-colors"
            >
              Speak to a Care Coordinator
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-slate-950 border-t border-white/10 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Heart className="w-5 h-5 text-teal-500" />
                <span className="text-lg font-bold text-white">PsyProtocol</span>
              </div>
              <p className="text-slate-500 text-sm">
                Advancing mental healthcare through technology and evidence-based protocols.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Treatments</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-teal-400 transition-colors">Depression</a></li>
                <li><a href="#" className="hover:text-teal-400 transition-colors">PTSD</a></li>
                <li><a href="#" className="hover:text-teal-400 transition-colors">Anxiety</a></li>
                <li><a href="#" className="hover:text-teal-400 transition-colors">Addiction</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Patients</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-teal-400 transition-colors">How it Works</a></li>
                <li><a href="#" className="hover:text-teal-400 transition-colors">Safety</a></li>
                <li><a href="#" className="hover:text-teal-400 transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-teal-400 transition-colors">FAQ</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-teal-400 transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-teal-400 transition-colors">Terms of Service</a></li>
                <li><a href="#" className="hover:text-teal-400 transition-colors">HIPAA</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/10 pt-8 text-center text-sm text-slate-600">
            &copy; 2025 PsyProtocol. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
