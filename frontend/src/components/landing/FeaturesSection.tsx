import React from 'react';

const FeaturesSection: React.FC = () => {
  const features = [
    {
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
      title: 'AI-Powered Protocol Engine',
      description: 'Advanced machine learning algorithms analyze patient data and recommend optimal treatment protocols based on the latest clinical research and outcomes data.',
      gradient: 'from-purple-500 to-pink-500'
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      ),
      title: '20+ Therapy Types Supported',
      description: 'Comprehensive coverage from psychedelic therapies and hormone optimization to cancer treatments, regenerative medicine, and cutting-edge gene therapy protocols.',
      gradient: 'from-primary-500 to-blue-500'
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      title: 'Clinical Decision Support',
      description: 'Real-time guidance for healthcare providers with safety monitoring, drug interaction checks, contraindication alerts, and evidence-based recommendations.',
      gradient: 'from-green-500 to-teal-500'
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      ),
      title: 'HIPAA-Compliant Audit Trail',
      description: 'Complete compliance with healthcare regulations. Every action, protocol change, and patient interaction is securely logged with end-to-end encryption.',
      gradient: 'from-blue-500 to-indigo-500'
    }
  ];

  return (
    <section className="py-20 bg-white" id="features">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Powerful Features for
            <span className="bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent"> Modern Healthcare</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Everything you need to deliver evidence-based care with confidence
          </p>
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group relative bg-white rounded-2xl p-8 border border-gray-200 hover:border-transparent hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1"
            >
              {/* Gradient border effect on hover */}
              <div className={`absolute inset-0 bg-gradient-to-r ${feature.gradient} rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10 blur-xl`}></div>

              {/* Icon */}
              <div className={`inline-flex items-center justify-center w-16 h-16 rounded-xl bg-gradient-to-r ${feature.gradient} text-white mb-6 transform group-hover:scale-110 transition-transform duration-300`}>
                {feature.icon}
              </div>

              {/* Content */}
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                {feature.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>

              {/* Decorative element */}
              <div className="absolute top-4 right-4 w-20 h-20 bg-gradient-to-br from-gray-100 to-transparent rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10"></div>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <p className="text-gray-600 mb-4">
            Trusted by healthcare providers worldwide
          </p>
          <div className="flex justify-center items-center gap-12 flex-wrap opacity-60">
            {/* Placeholder for partner/certification logos */}
            <div className="text-sm font-semibold text-gray-500">HIPAA Certified</div>
            <div className="text-sm font-semibold text-gray-500">SOC 2 Compliant</div>
            <div className="text-sm font-semibold text-gray-500">FDA Guidelines</div>
            <div className="text-sm font-semibold text-gray-500">Clinical Research</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
