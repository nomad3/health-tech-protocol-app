import React, { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../../hooks';
import { fetchProtocols, setFilters, clearFilters, fetchProtocol } from '../../store/protocolSlice';
import ProtocolCard from '../../components/protocols/ProtocolCard';
import ProtocolDetail from '../../components/protocols/ProtocolDetail';
import { Input, Button, Spinner } from '../../components/common';
import { TherapyType, EvidenceLevel, type Protocol } from '../../types/protocol';

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

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Protocol Browser</h1>
          <p className="text-gray-600">
            Browse evidence-based psychedelic therapy protocols
          </p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <form onSubmit={handleSearch} className="mb-4">
            <div className="flex gap-2">
              <Input
                type="text"
                placeholder="Search protocols..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1"
              />
              <Button type="submit">Search</Button>
            </div>
          </form>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Therapy Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Therapy Type
              </label>
              <select
                value={filters.therapy_type || 'all'}
                onChange={(e) => handleFilterChange('therapy_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                <option value="all">All Types</option>
                {Object.values(TherapyType).map((type) => (
                  <option key={type} value={type}>
                    {type.toUpperCase()}
                  </option>
                ))}
              </select>
            </div>

            {/* Evidence Level Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Evidence Level
              </label>
              <select
                value={filters.evidence_level || 'all'}
                onChange={(e) => handleFilterChange('evidence_level', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                <option value="all">All Levels</option>
                {Object.values(EvidenceLevel).map((level) => (
                  <option key={level} value={level}>
                    {level.replace(/_/g, ' ').toUpperCase()}
                  </option>
                ))}
              </select>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={filters.status || 'all'}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="draft">Draft</option>
                <option value="archived">Archived</option>
              </select>
            </div>
          </div>

          {activeFiltersCount > 0 && (
            <div className="mt-4">
              <Button variant="outline" size="sm" onClick={handleClearFilters}>
                Clear Filters ({activeFiltersCount})
              </Button>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-12">
            <Spinner size="lg" />
          </div>
        )}

        {/* Protocol Grid */}
        {!loading && (
          <>
            {protocols.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No protocols found</p>
                <p className="text-gray-400 text-sm mt-2">
                  Try adjusting your filters or search query
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {protocols.map((protocol) => (
                  <ProtocolCard
                    key={protocol.id}
                    protocol={protocol}
                    onClick={() => handleProtocolClick(protocol)}
                  />
                ))}
              </div>
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
