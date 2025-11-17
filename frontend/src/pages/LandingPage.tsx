import React from 'react';
import HeroSection from '../components/landing/HeroSection';
import FeaturesSection from '../components/landing/FeaturesSection';
import TherapyTypesSection from '../components/landing/TherapyTypesSection';
import HowItWorksSection from '../components/landing/HowItWorksSection';
import StatsSection from '../components/landing/StatsSection';
import CTASection from '../components/landing/CTASection';
import Footer from '../components/landing/Footer';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-white">
      <HeroSection />
      <FeaturesSection />
      <TherapyTypesSection />
      <HowItWorksSection />
      <StatsSection />
      <CTASection />
      <Footer />
    </div>
  );
};

export default LandingPage;
