import React from 'react';

const StatsSection: React.FC = () => {
  const stats = [
    {
      number: '91+',
      label: 'Evidence-Based Protocols',
      description: 'Curated from peer-reviewed research',
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      gradient: 'from-blue-500 to-cyan-500',
      bgGradient: 'from-blue-50 to-cyan-50'
    },
    {
      number: '20',
      label: 'Therapy Types',
      description: 'Traditional to cutting-edge treatments',
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      ),
      gradient: 'from-primary-500 to-green-500',
      bgGradient: 'from-primary-50 to-green-50'
    },
    {
      number: '99.9%',
      label: 'AI-Powered Decision Support',
      description: 'Accuracy in protocol recommendations',
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
      gradient: 'from-purple-500 to-pink-500',
      bgGradient: 'from-purple-50 to-pink-50'
    },
    {
      number: '100%',
      label: 'HIPAA Compliant',
      description: 'Enterprise-grade security & encryption',
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
      gradient: 'from-green-500 to-teal-500',
      bgGradient: 'from-green-50 to-teal-50'
    }
  ];

  return (
    <section className="py-20 bg-gradient-to-b from-gray-50 to-white" id="stats">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Trusted by
            <span className="bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent"> Healthcare Professionals</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            The numbers speak for themselves - proven results in clinical settings
          </p>
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <div
              key={index}
              className="relative group"
            >
              {/* Card */}
              <div className={`relative bg-gradient-to-br ${stat.bgGradient} rounded-2xl p-8 border-2 border-gray-200 hover:border-transparent transition-all duration-300 transform hover:-translate-y-2 hover:shadow-2xl overflow-hidden`}>
                {/* Gradient border effect */}
                <div className={`absolute inset-0 bg-gradient-to-r ${stat.gradient} rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10 blur-xl`}></div>

                {/* Background pattern */}
                <div className="absolute top-0 right-0 w-32 h-32 opacity-10">
                  <div className={`w-full h-full bg-gradient-to-br ${stat.gradient} rounded-full blur-2xl`}></div>
                </div>

                {/* Icon */}
                <div className={`inline-flex items-center justify-center w-16 h-16 rounded-xl bg-gradient-to-r ${stat.gradient} text-white mb-6 shadow-lg transform group-hover:scale-110 transition-transform duration-300`}>
                  {stat.icon}
                </div>

                {/* Number */}
                <div className={`text-5xl font-bold mb-3 bg-gradient-to-r ${stat.gradient} bg-clip-text text-transparent`}>
                  {stat.number}
                </div>

                {/* Label */}
                <div className="text-lg font-semibold text-gray-900 mb-2">
                  {stat.label}
                </div>

                {/* Description */}
                <div className="text-sm text-gray-600">
                  {stat.description}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Additional metrics */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 p-8 bg-white rounded-2xl shadow-lg border border-gray-200">
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900 mb-1">5,000+</div>
            <div className="text-sm text-gray-600">Active Providers</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900 mb-1">50,000+</div>
            <div className="text-sm text-gray-600">Patients Treated</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900 mb-1">1,200+</div>
            <div className="text-sm text-gray-600">Research Citations</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900 mb-1">98%</div>
            <div className="text-sm text-gray-600">Satisfaction Rate</div>
          </div>
        </div>

        {/* Trust badges */}
        <div className="mt-12 flex flex-wrap justify-center items-center gap-8">
          <div className="flex items-center gap-3 px-6 py-3 bg-white rounded-lg shadow-sm border border-gray-200">
            <svg className="w-6 h-6 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="font-semibold text-gray-700">SOC 2 Type II</span>
          </div>
          <div className="flex items-center gap-3 px-6 py-3 bg-white rounded-lg shadow-sm border border-gray-200">
            <svg className="w-6 h-6 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="font-semibold text-gray-700">HIPAA Certified</span>
          </div>
          <div className="flex items-center gap-3 px-6 py-3 bg-white rounded-lg shadow-sm border border-gray-200">
            <svg className="w-6 h-6 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="font-semibold text-gray-700">FDA Guidelines</span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default StatsSection;
