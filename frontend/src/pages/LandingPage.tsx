import {
  Activity,
  ArrowRight,
  Brain,
  ChevronRight,
  Clock,
  Database,
  FlaskConical,
  Heart,
  HeartPulse,
  Lightbulb,
  MessageCircle,
  Shield,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  Users,
  Zap
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import NeuralBackground from '../components/landing/NeuralBackground';

interface ProtocolCardProps {
  icon: React.ReactNode;
  code: string;
  title: string;
  description: string;
  features: string[];
  gradient: string;
  borderColor: string;
}

const ProtocolCard: React.FC<ProtocolCardProps> = ({ icon, code, title, description, features, gradient, borderColor }) => (
  <div className={`group relative p-8 rounded-2xl bg-gradient-to-b from-white/5 to-white/[0.02] border border-white/10 hover:${borderColor} transition-all duration-300 hover:-translate-y-1`}>
    <div className={`absolute inset-0 ${gradient} opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl`}></div>
    <div className="relative z-10">
      <div className="flex items-center justify-between mb-4">
        <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
          {icon}
        </div>
        <span className="text-xs font-mono text-slate-500 bg-white/5 px-2 py-1 rounded">{code}</span>
      </div>
      <h3 className="text-xl font-bold text-white mb-3">{title}</h3>
      <p className="text-slate-400 text-sm leading-relaxed mb-4">{description}</p>
      <ul className="space-y-2">
        {features.map((feature, index) => (
          <li key={index} className="flex items-start space-x-2 text-sm text-slate-500">
            <ChevronRight className="w-4 h-4 text-teal-400 mt-0.5 flex-shrink-0" />
            <span>{feature}</span>
          </li>
        ))}
      </ul>
    </div>
  </div>
);

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

  const currentProtocols = [
    {
      icon: <Brain className="w-6 h-6 text-teal-400" />,
      code: "NDP-1",
      title: "Neuroadaptive Depression Protocol",
      description: "A structured treatment pathway for Major Depressive Disorder designed to reduce rumination patterns and improve emotional regulation.",
      features: [
        "Medical evaluation & adaptive dosing",
        "Trauma-informed therapy sessions",
        "Post-session integration support",
        "Continuous progress monitoring"
      ],
      gradient: "bg-gradient-to-br from-teal-500/10 to-cyan-500/10",
      borderColor: "border-teal-500/30"
    },
    {
      icon: <HeartPulse className="w-6 h-6 text-purple-400" />,
      code: "TRP-2",
      title: "PTSD & Trauma Resolution Protocol",
      description: "A comprehensive program for trauma survivors incorporating clinician-guided therapeutic sessions and memory reconsolidation.",
      features: [
        "Memory reconsolidation protocols",
        "Somatic & cognitive integration",
        "Long-term resilience training",
        "Functional recovery tracking"
      ],
      gradient: "bg-gradient-to-br from-purple-500/10 to-pink-500/10",
      borderColor: "border-purple-500/30"
    },
    {
      icon: <Activity className="w-6 h-6 text-blue-400" />,
      code: "ARP-3",
      title: "Anxiety Reduction Protocol",
      description: "Targeted for chronic anxiety, panic behaviors, and stress dysregulation with focus on nervous system regulation.",
      features: [
        "Nervous system regulation exercises",
        "Guided therapeutic interventions",
        "Medication-assisted components",
        "Weekly platform tracking"
      ],
      gradient: "bg-gradient-to-br from-blue-500/10 to-indigo-500/10",
      borderColor: "border-blue-500/30"
    },
    {
      icon: <Target className="w-6 h-6 text-amber-400" />,
      code: "RPX-4",
      title: "Addiction Recovery Protocol",
      description: "A personalized, multi-layered recovery framework with craving prediction and behavioral pattern analysis.",
      features: [
        "Behavioral pattern analysis",
        "Harm-reduction strategies",
        "Emotional resilience coaching",
        "Relapse-prevention monitoring"
      ],
      gradient: "bg-gradient-to-br from-amber-500/10 to-orange-500/10",
      borderColor: "border-amber-500/30"
    }
  ];

  const upcomingProtocols = [
    {
      icon: <FlaskConical className="w-6 h-6 text-emerald-400" />,
      code: "PAT-5",
      title: "Psychedelic-Assisted Therapy",
      description: "Clinical applications pending regulatory alignment.",
      features: ["Psilocybin-based therapy", "MDMA-assisted therapy", "AI-assisted preparation", "Real-time monitoring"],
      gradient: "bg-gradient-to-br from-emerald-500/10 to-green-500/10",
      borderColor: "border-emerald-500/30"
    },
    {
      icon: <Database className="w-6 h-6 text-cyan-400" />,
      code: "DBX-1",
      title: "Digital Biomarkers Protocol",
      description: "Early detection and personalized treatment adjustments.",
      features: ["Voice biomarkers", "Facial micro-expression analysis", "Wearable data integration", "Behavioral patterns"],
      gradient: "bg-gradient-to-br from-cyan-500/10 to-sky-500/10",
      borderColor: "border-cyan-500/30"
    },
    {
      icon: <Zap className="w-6 h-6 text-rose-400" />,
      code: "CPR-5",
      title: "Chronic Pain & Somatic Relief",
      description: "Mind-body modulation for neural and emotional dysregulation.",
      features: ["Trauma-somatic analysis", "Clinically supervised sessions", "Pain perception recalibration", "Neural pathway work"],
      gradient: "bg-gradient-to-br from-rose-500/10 to-red-500/10",
      borderColor: "border-rose-500/30"
    },
    {
      icon: <Lightbulb className="w-6 h-6 text-yellow-400" />,
      code: "CEP-6",
      title: "Cognitive Enhancement Protocol",
      description: "Neuroplasticity-focused performance and recovery program.",
      features: ["Memory optimization", "Focus enhancement", "Emotional agility", "Stress resilience"],
      gradient: "bg-gradient-to-br from-yellow-500/10 to-amber-500/10",
      borderColor: "border-yellow-500/30"
    }
  ];

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
              Health Protocol
            </span>
          </div>
          <div className="hidden md:flex items-center space-x-8">
            <a href="#protocols" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Protocols</a>
            <a href="#roadmap" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Roadmap</a>
            <a href="#why-us" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Why Us</a>
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
          <NeuralBackground />
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-600/20 rounded-full mix-blend-screen filter blur-[128px] animate-pulse-slow"></div>
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-teal-600/20 rounded-full mix-blend-screen filter blur-[128px] animate-pulse-slow delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-600/5 rounded-full mix-blend-screen filter blur-[100px]"></div>
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
              Advanced, Clinically Guided
            </span>
            <span className="block text-white mt-2">Mental Healthcare</span>
          </h1>

          <p className="mt-4 text-xl text-slate-400 max-w-3xl mx-auto mb-10 animate-fade-in-up delay-200 leading-relaxed">
            Experience meaningful relief from <strong className="text-white">Depression</strong>, <strong className="text-white">PTSD</strong>, <strong className="text-white">Anxiety</strong>, and <strong className="text-white">Addiction</strong> through structured, evidence-based treatment protocols. Our programs integrate medical oversight, modern therapeutics, biometric insights, and ongoing support.
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
              View Treatment Programs
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

      {/* Our Clinical Protocols Section */}
      <section id="protocols" className="relative py-24 bg-slate-950">
        <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/20 mb-4">
              <Shield className="w-4 h-4 text-teal-400" />
              <span className="text-xs font-medium text-teal-300 tracking-wide uppercase">Outcomes-Driven</span>
            </div>
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">Our Clinical Protocols</h2>
            <p className="text-slate-400 max-w-3xl mx-auto text-lg">
              We operate under a structured, outcomes-driven protocol system designed to maximize safety, personalization, and long-term therapeutic impact.
            </p>
          </div>

          <div className="mb-12">
            <h3 className="text-xl font-semibold text-white mb-8 flex items-center">
              <span className="w-8 h-8 rounded-full bg-teal-500/20 flex items-center justify-center mr-3">
                <Sparkles className="w-4 h-4 text-teal-400" />
              </span>
              Current Protocols (2025)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {currentProtocols.map((protocol, index) => (
                <ProtocolCard key={index} {...protocol} />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Upcoming Protocols / Roadmap Section */}
      <section id="roadmap" className="relative py-24 bg-gradient-to-b from-slate-950 to-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 mb-4">
              <TrendingUp className="w-4 h-4 text-purple-400" />
              <span className="text-xs font-medium text-purple-300 tracking-wide uppercase">2025–2026 Roadmap</span>
            </div>
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">Upcoming Protocols</h2>
            <p className="text-slate-400 max-w-3xl mx-auto text-lg">
              These programs extend the platform toward deeper precision medicine and next-generation therapeutic models.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {upcomingProtocols.map((protocol, index) => (
              <div key={index} className={`group relative p-6 rounded-2xl bg-gradient-to-b from-white/5 to-white/[0.02] border border-white/10 border-dashed hover:border-solid transition-all duration-300`}>
                <div className={`absolute inset-0 ${protocol.gradient} opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl`}></div>
                <div className="relative z-10">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center">
                      {protocol.icon}
                    </div>
                    <span className="text-xs font-mono text-slate-600 bg-white/5 px-2 py-1 rounded">{protocol.code}</span>
                  </div>
                  <h4 className="text-lg font-bold text-white mb-2">{protocol.title}</h4>
                  <p className="text-slate-500 text-sm mb-4">{protocol.description}</p>
                  <div className="flex flex-wrap gap-1">
                    {protocol.features.slice(0, 2).map((feature, idx) => (
                      <span key={idx} className="text-xs text-slate-600 bg-white/5 px-2 py-1 rounded">
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="absolute top-4 right-4">
                  <span className="text-[10px] font-medium text-slate-600 bg-slate-800 px-2 py-0.5 rounded-full">Coming Soon</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why Patients Choose Section */}
      <section id="why-us" className="py-24 bg-slate-900 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent"></div>
        <div className="absolute top-1/4 left-0 w-72 h-72 bg-teal-500/10 rounded-full blur-[120px]"></div>
        <div className="absolute bottom-1/4 right-0 w-72 h-72 bg-purple-500/10 rounded-full blur-[120px]"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">Why Patients Choose Health Protocol</h2>
            <p className="text-slate-400 max-w-3xl mx-auto text-lg">
              Traditional treatments focus on symptom management. We deliver structured, medically guided programs built around your brain, biology, and story—so healing becomes predictable, supported, and sustainable.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="group relative p-8 rounded-2xl bg-gradient-to-b from-white/5 to-white/[0.02] border border-white/10 hover:border-teal-500/30 transition-all duration-300 hover:-translate-y-1">
              <div className="absolute inset-0 bg-gradient-to-br from-teal-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl"></div>
              <div className="relative z-10">
                <div className="w-14 h-14 rounded-xl bg-teal-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Brain className="w-7 h-7 text-teal-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Root-Cause Healing</h3>
                <p className="text-slate-400 leading-relaxed">
                  Go beyond symptom management. Our protocols are designed to help you process trauma, shift perspectives, and achieve durable remission—not just temporary relief.
                </p>
              </div>
            </div>

            <div className="group relative p-8 rounded-2xl bg-gradient-to-b from-white/5 to-white/[0.02] border border-white/10 hover:border-blue-500/30 transition-all duration-300 hover:-translate-y-1">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl"></div>
              <div className="relative z-10">
                <div className="w-14 h-14 rounded-xl bg-blue-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <ShieldCheck className="w-7 h-7 text-blue-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Safe, Guided Healing</h3>
                <p className="text-slate-400 leading-relaxed">
                  Your safety is our priority. Every step of your journey is monitored by medical professionals and supported by advanced safety protocols and real-time tracking.
                </p>
              </div>
            </div>

            <div className="group relative p-8 rounded-2xl bg-gradient-to-b from-white/5 to-white/[0.02] border border-white/10 hover:border-purple-500/30 transition-all duration-300 hover:-translate-y-1">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl"></div>
              <div className="relative z-10">
                <div className="w-14 h-14 rounded-xl bg-purple-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Heart className="w-7 h-7 text-purple-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Support Beyond Sessions</h3>
                <p className="text-slate-400 leading-relaxed">
                  Healing continues after the treatment. We provide comprehensive integration support, ongoing monitoring, and tools to help you apply insights to daily life.
                </p>
              </div>
            </div>
          </div>

          {/* Additional Features */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="flex items-start space-x-4 p-6 rounded-xl bg-white/5 border border-white/5">
              <div className="w-10 h-10 rounded-lg bg-teal-500/20 flex items-center justify-center flex-shrink-0">
                <Users className="w-5 h-5 text-teal-400" />
              </div>
              <div>
                <h4 className="text-white font-semibold">Dedicated Care Team</h4>
                <p className="text-slate-500 text-sm mt-1">Compassionate therapists and medical experts at every step.</p>
              </div>
            </div>
            <div className="flex items-start space-x-4 p-6 rounded-xl bg-white/5 border border-white/5">
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                <Activity className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <h4 className="text-white font-semibold">Personalized For You</h4>
                <p className="text-slate-500 text-sm mt-1">Treatment tailored to your unique history and biology.</p>
              </div>
            </div>
            <div className="flex items-start space-x-4 p-6 rounded-xl bg-white/5 border border-white/5">
              <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                <Clock className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <h4 className="text-white font-semibold">Long-Term Focus</h4>
                <p className="text-slate-500 text-sm mt-1">Building sustainable recovery, not quick fixes.</p>
              </div>
            </div>
            <div className="flex items-start space-x-4 p-6 rounded-xl bg-white/5 border border-white/5">
              <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                <MessageCircle className="w-5 h-5 text-amber-400" />
              </div>
              <div>
                <h4 className="text-white font-semibold">Continuous Support</h4>
                <p className="text-slate-500 text-sm mt-1">24/7 access to care coordinators and resources.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <div className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-slate-900 to-slate-950"></div>
        <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-full h-full max-w-4xl bg-teal-500/5 blur-[100px] rounded-full pointer-events-none"></div>

        <div className="relative z-10 max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">Begin Your Healing Journey</h2>
          <p className="text-xl text-slate-400 mb-10">
            Take the first step toward clinically supported relief and long-term transformation.
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
                <span className="text-lg font-bold text-white">Health Protocol</span>
              </div>
              <p className="text-slate-500 text-sm">
                Advancing mental healthcare through technology and evidence-based protocols.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Protocols</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-teal-400 transition-colors">Depression (NDP-1)</a></li>
                <li><a href="#" className="hover:text-teal-400 transition-colors">PTSD (TRP-2)</a></li>
                <li><a href="#" className="hover:text-teal-400 transition-colors">Anxiety (ARP-3)</a></li>
                <li><a href="#" className="hover:text-teal-400 transition-colors">Addiction (RPX-4)</a></li>
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
            &copy; 2025 Health Protocol. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
