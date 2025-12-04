import React, { useEffect, useState } from 'react';
import { EmptyState, Input, Spinner } from '../../components/common';
import ProtocolCard from '../../components/protocols/ProtocolCard';
import ProtocolDetail from '../../components/protocols/ProtocolDetail';
import { useAppDispatch, useAppSelector } from '../../hooks';
import { clearFilters, fetchProtocol, fetchProtocols, setFilters } from '../../store/protocolSlice';
import { EvidenceLevel, TherapyType, type Protocol } from '../../types/protocol';

const ProtocolBrowser: React.FC = () => {
  const dispatch = useAppDispatch();
  const { protocols, selectedProtocol, filters, loading, error } = useAppSelector((state) => state.protocol);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    dispatch(fetchProtocols({ filters, page: 1, pageSize: 20 }));
  }, [dispatch, filters]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    dispatch(setFilters({ ...filters, search: searchQuery }));
  };

  const handleFilterChange = (key: string, value: string) => {
    if (value === 'all') {
      const newFilters = { ...filters };
      delete newFilters[key as keyof typeof filters];
      dispatch(setFilters(newFilters));
    } else {
      dispatch(setFilters({ ...filters, [key]: value }));
    }
  };

  const handleProtocolClick = async (protocol: Protocol) => {
    await dispatch(fetchProtocol(protocol.id));
    setIsDetailOpen(true);
  };

  const handleClearFilters = () => {
    dispatch(clearFilters());
    setSearchQuery('');
  };

  const activeFiltersCount = Object.keys(filters).filter(key => filters[key as keyof typeof filters]).length;

  const therapyTypeColors: Partial<Record<TherapyType, string>> = {
    psilocybin: 'from-purple-500 to-pink-500',
    mdma: 'from-blue-500 to-cyan-500',
    ketamine: 'from-cyan-500 to-teal-500',
    lsd: 'from-green-500 to-emerald-500',
    ibogaine: 'from-amber-500 to-orange-500',
    other: 'from-indigo-500 to-purple-500',
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-3">
            Discover{' '}
            <span className="bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">
              Evidence-Based
            </span>{' '}
            Protocols
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Browse scientifically-validated psychedelic therapy protocols tailored to your needs
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-8 max-w-3xl mx-auto">
          <form onSubmit={handleSearch}>
            <div className="relative">
              <Input
                type="text"
                placeholder="Search protocols by name, condition, or therapy type..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full shadow-lg"
                icon="🔍"
                iconPosition="left"
              />
              <button
                type="submit"
                className="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-2 bg-gradient-to-r from-teal-600 to-cyan-600 text-white font-semibold rounded-lg hover:from-teal-700 hover:to-cyan-700 transition-all duration-200 shadow-md hover:shadow-lg"
              >
                Search
              </button>
            </div>
          </form>
        </div>

        {/* Filters */}
        <div className="mb-8 bg-white rounded-2xl shadow-lg p-6 max-w-5xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
            {activeFiltersCount > 0 && (
              <button
                onClick={handleClearFilters}
                className="text-sm text-teal-600 hover:text-teal-700 font-medium flex items-center gap-1"
              >
                <span>✕</span> Clear all ({activeFiltersCount})
              </button>
            )}
          </div>

          {/* Therapy Type Pills */}
          <div className="mb-4">
            <label className="block text-sm font-semibold text-gray-700 mb-3">Therapy Type</label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => handleFilterChange('therapy_type', 'all')}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${!filters.therapy_type
                  ? 'bg-gradient-to-r from-teal-600 to-cyan-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
              >
                All Types
              </button>
              {Object.values(TherapyType).map((type) => (
                <button
                  key={type}
                  onClick={() => handleFilterChange('therapy_type', type)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${filters.therapy_type === type
                    ? `bg-gradient-to-r ${therapyTypeColors[type] || 'from-gray-500 to-slate-500'} text-white shadow-md`
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                >
                  {type.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {/* Evidence Level Pills */}
          <div className="mb-4">
            <label className="block text-sm font-semibold text-gray-700 mb-3">Evidence Level</label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => handleFilterChange('evidence_level', 'all')}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${!filters.evidence_level
                  ? 'bg-gradient-to-r from-teal-600 to-cyan-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
              >
                All Levels
              </button>
              {Object.values(EvidenceLevel).map((level) => (
                <button
                  key={level}
                  onClick={() => handleFilterChange('evidence_level', level)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${filters.evidence_level === level
                    ? 'bg-gradient-to-r from-green-600 to-teal-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                >
                  {level.replace(/_/g, ' ').toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {/* Status Pills */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">Status</label>
            <div className="flex flex-wrap gap-2">
              {['all', 'active', 'draft', 'archived'].map((status) => (
                <button
                  key={status}
                  onClick={() => handleFilterChange('status', status)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${(!filters.status && status === 'all') || filters.status === status
                    ? 'bg-gradient-to-r from-teal-600 to-cyan-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                >
                  {status === 'all' ? 'All Status' : status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-xl mb-6 max-w-3xl mx-auto shadow-md">
            <div className="flex items-center gap-2">
              <span className="text-xl">⚠️</span>
              <span className="font-medium">{error}</span>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col justify-center items-center py-20">
            <Spinner size="lg" />
            <p className="mt-4 text-gray-600 font-medium">Loading protocols...</p>
          </div>
        )}

        {/* Protocol Grid */}
        {!loading && (
          <>
            {protocols.length === 0 ? (
              <EmptyState
                icon="🔬"
                title="No protocols found"
                description="Try adjusting your filters or search query to find what you're looking for"
                action={{
                  label: 'Clear Filters',
                  onClick: handleClearFilters,
                }}
              />
            ) : (
              <>
                <div className="mb-4 text-center">
                  <p className="text-gray-600">
                    Showing <span className="font-semibold text-gray-900">{protocols.length}</span> protocols
                  </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                  {protocols.map((protocol) => (
                    <div
                      key={protocol.id}
                      className="transform transition-all duration-300 hover:scale-105"
                    >
                      <ProtocolCard
                        protocol={protocol}
                        onClick={() => handleProtocolClick(protocol)}
                      />
                    </div>
                  ))}
                </div>
              </>
            )}
          </>
        )}

        {/* Protocol Detail Modal */}
        {selectedProtocol && (
          <ProtocolDetail
            protocol={selectedProtocol}
            isOpen={isDetailOpen}
            onClose={() => setIsDetailOpen(false)}
          />
        )}
      </div>
    </div>
  );
};

export default ProtocolBrowser;
