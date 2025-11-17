import React from 'react';

const HowItWorksSection: React.FC = () => {
  const steps = [
    {
      number: '01',
      title: 'Browse Evidence-Based Protocols',
      description: 'Search our comprehensive database of 91+ protocols across 20+ therapy types. Filter by condition, treatment type, or patient characteristics to find the perfect match.',
      icon: (
        <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      ),
      color: 'from-blue-500 to-cyan-500'
    },
    {
      number: '02',
      title: 'Connect with Certified Providers',
      description: 'Our platform matches you with qualified healthcare professionals trained in your selected therapy. Review credentials, experience, and patient outcomes before booking.',
      icon: (
        <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      color: 'from-primary-500 to-green-500'
    },
    {
      number: '03',
      title: 'Track Your Treatment Journey',
      description: 'Monitor progress with AI-powered insights. Track symptoms, side effects, and outcomes. Receive personalized recommendations and safety alerts throughout your treatment.',
      icon: (
        <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      color: 'from-purple-500 to-pink-500'
    }
  ];

  return (
    <section className="py-20 bg-white" id="how-it-works">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            How It
            <span className="bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent"> Works</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Get started with evidence-based care in three simple steps
          </p>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Connection line - desktop only */}
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-1 bg-gradient-to-r from-blue-200 via-primary-200 to-purple-200 transform -translate-y-1/2 -z-10"></div>

          {/* Steps grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            {steps.map((step, index) => (
              <div key={index} className="relative">
                {/* Step card */}
                <div className="bg-white rounded-2xl p-8 border-2 border-gray-200 hover:border-transparent hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 group">
                  {/* Gradient border effect */}
                  <div className={`absolute inset-0 bg-gradient-to-r ${step.color} rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10 blur-xl`}></div>

                  {/* Step number */}
                  <div className={`inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-r ${step.color} text-white font-bold text-2xl mb-6 shadow-lg`}>
                    {step.number}
                  </div>

                  {/* Icon */}
                  <div className="text-gray-400 mb-4">
                    {step.icon}
                  </div>

                  {/* Content */}
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">
                    {step.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {step.description}
                  </p>

                  {/* Progress indicator for mobile */}
                  {index < steps.length - 1 && (
                    <div className="lg:hidden mt-8 flex justify-center">
                      <svg className="w-6 h-6 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                      </svg>
                    </div>
                  )}
                </div>

                {/* Desktop connector dot */}
                <div className="hidden lg:block absolute top-1/2 -right-6 w-12 h-12 transform -translate-y-1/2">
                  {index < steps.length - 1 && (
                    <div className={`w-4 h-4 rounded-full bg-gradient-to-r ${step.color} shadow-lg ring-4 ring-white`}></div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <div className="inline-flex flex-col sm:flex-row items-center gap-4 bg-gradient-to-r from-primary-50 to-blue-50 rounded-2xl p-8 border border-primary-200">
            <div className="flex-1 text-left">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                Ready to get started?
              </h3>
              <p className="text-gray-600">
                Join thousands of providers delivering evidence-based care
              </p>
            </div>
            <button className="px-8 py-4 bg-gradient-to-r from-primary-600 to-primary-500 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200">
              Start Free Trial
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
