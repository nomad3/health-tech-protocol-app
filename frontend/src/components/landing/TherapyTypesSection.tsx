import React, { useState } from 'react';

const TherapyTypesSection: React.FC = () => {
  const [activeCategory, setActiveCategory] = useState('all');

  const therapyCategories = [
    {
      id: 'psychedelic',
      name: 'Psychedelic Therapies',
      color: 'from-purple-500 to-pink-500',
      therapies: [
        { name: 'Psilocybin', protocols: 15 },
        { name: 'MDMA', protocols: 12 },
        { name: 'Ketamine', protocols: 18 },
        { name: 'LSD', protocols: 8 }
      ]
    },
    {
      id: 'hormone',
      name: 'Hormone Optimization',
      color: 'from-blue-500 to-cyan-500',
      therapies: [
        { name: 'Testosterone', protocols: 14 },
        { name: 'Growth Hormone', protocols: 10 },
        { name: 'Thyroid', protocols: 8 },
        { name: 'Peptides', protocols: 12 }
      ]
    },
    {
      id: 'cancer',
      name: 'Cancer Treatments',
      color: 'from-red-500 to-orange-500',
      therapies: [
        { name: 'Chemotherapy', protocols: 16 },
        { name: 'Immunotherapy', protocols: 14 },
        { name: 'Targeted Therapy', protocols: 11 },
        { name: 'Radiation', protocols: 9 }
      ]
    },
    {
      id: 'regenerative',
      name: 'Regenerative Medicine',
      color: 'from-green-500 to-teal-500',
      therapies: [
        { name: 'Stem Cells', protocols: 13 },
        { name: 'PRP Therapy', protocols: 10 },
        { name: 'Exosomes', protocols: 7 },
        { name: 'Tissue Engineering', protocols: 6 }
      ]
    },
    {
      id: 'emerging',
      name: 'Emerging Therapies',
      color: 'from-indigo-500 to-purple-500',
      therapies: [
        { name: 'Gene Therapy', protocols: 9 },
        { name: 'CRISPR', protocols: 6 },
        { name: 'CAR-T Cell', protocols: 8 },
        { name: 'mRNA Technology', protocols: 7 }
      ]
    }
  ];

  const filteredCategories = activeCategory === 'all'
    ? therapyCategories
    : therapyCategories.filter(cat => cat.id === activeCategory);

  const totalProtocols = therapyCategories.reduce(
    (sum, cat) => sum + cat.therapies.reduce((s, t) => s + t.protocols, 0),
    0
  );

  return (
    <section className="py-20 bg-gradient-to-b from-gray-50 to-white" id="therapies">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            20+ Therapy Types,
            <span className="bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent"> {totalProtocols} Protocols</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Comprehensive coverage across traditional and cutting-edge treatment modalities
          </p>
        </div>

        {/* Category filters */}
        <div className="flex flex-wrap justify-center gap-3 mb-12">
          <button
            onClick={() => setActiveCategory('all')}
            className={`px-6 py-3 rounded-full font-medium transition-all duration-200 ${
              activeCategory === 'all'
                ? 'bg-gradient-to-r from-primary-600 to-primary-500 text-white shadow-lg'
                : 'bg-white text-gray-700 border border-gray-300 hover:border-primary-500'
            }`}
          >
            All Therapies
          </button>
          {therapyCategories.map((category) => (
            <button
              key={category.id}
              onClick={() => setActiveCategory(category.id)}
              className={`px-6 py-3 rounded-full font-medium transition-all duration-200 ${
                activeCategory === category.id
                  ? `bg-gradient-to-r ${category.color} text-white shadow-lg`
                  : 'bg-white text-gray-700 border border-gray-300 hover:border-primary-500'
              }`}
            >
              {category.name}
            </button>
          ))}
        </div>

        {/* Therapy categories grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCategories.map((category) => (
            <div
              key={category.id}
              className="bg-white rounded-2xl p-6 border border-gray-200 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
            >
              {/* Category header */}
              <div className="mb-6">
                <div className={`inline-block px-4 py-2 rounded-full bg-gradient-to-r ${category.color} text-white text-sm font-semibold mb-3`}>
                  {category.therapies.reduce((sum, t) => sum + t.protocols, 0)} Protocols
                </div>
                <h3 className="text-2xl font-bold text-gray-900">
                  {category.name}
                </h3>
              </div>

              {/* Therapy list */}
              <div className="space-y-3">
                {category.therapies.map((therapy, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${category.color}`}></div>
                      <span className="font-medium text-gray-800">{therapy.name}</span>
                    </div>
                    <span className="text-sm text-gray-500">{therapy.protocols} protocols</span>
                  </div>
                ))}
              </div>

              {/* View button */}
              <button className={`mt-6 w-full py-3 rounded-lg font-medium bg-gradient-to-r ${category.color} text-white hover:shadow-lg transition-all duration-200 transform hover:-translate-y-0.5`}>
                View Protocols
              </button>
            </div>
          ))}
        </div>

        {/* Bottom stats */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="text-4xl font-bold bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent mb-2">
              {totalProtocols}+
            </div>
            <div className="text-gray-600">Total Protocols</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
              20+
            </div>
            <div className="text-gray-600">Therapy Types</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold bg-gradient-to-r from-green-600 to-teal-600 bg-clip-text text-transparent mb-2">
              1000+
            </div>
            <div className="text-gray-600">Research Papers</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent mb-2">
              24/7
            </div>
            <div className="text-gray-600">AI Support</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TherapyTypesSection;
