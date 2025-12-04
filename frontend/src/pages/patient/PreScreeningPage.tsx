import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '../../components/common';
import type { PreScreeningData } from '../../components/protocols/PreScreeningForm';
import PreScreeningForm from '../../components/protocols/PreScreeningForm';
import { protocolService } from '../../services/protocolService';
import type { Protocol } from '../../types/protocol';

const PreScreeningPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [protocol, setProtocol] = useState<Protocol | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);

  useEffect(() => {
    const fetchProtocol = async () => {
      if (!id) return;
      try {
        const data = await protocolService.getProtocol(parseInt(id));
        setProtocol(data);
      } catch (err) {
        setError('Failed to load protocol details');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchProtocol();
  }, [id]);

  const handleSubmit = async (data: PreScreeningData) => {
    if (!id) return;
    try {
      const response = await protocolService.submitPreScreening(parseInt(id), data);
      setResult(response);
    } catch (err) {
      setError('Failed to submit screening');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
      </div>
    );
  }

  if (error || !protocol) {
    return (
      <div className="max-w-2xl mx-auto mt-10 p-6 bg-red-50 rounded-lg">
        <h2 className="text-red-700 font-bold text-xl mb-2">Error</h2>
        <p className="text-red-600">{error || 'Protocol not found'}</p>
        <Button className="mt-4" onClick={() => navigate('/protocols')}>
          Back to Protocols
        </Button>
      </div>
    );
  }

  if (result) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-2xl mx-auto px-4">
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            <div className={`p-6 ${result.eligible ? 'bg-green-50' : 'bg-amber-50'}`}>
              <div className="flex items-center gap-4 mb-4">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl ${result.eligible ? 'bg-green-100 text-green-600' : 'bg-amber-100 text-amber-600'
                  }`}>
                  {result.eligible ? '✓' : '⚠️'}
                </div>
                <div>
                  <h2 className={`text-2xl font-bold ${result.eligible ? 'text-green-800' : 'text-amber-800'}`}>
                    {result.eligible ? 'Assessment Complete' : 'Review Needed'}
                  </h2>
                  <p className={`font-medium ${result.eligible ? 'text-green-700' : 'text-amber-700'}`}>
                    {result.eligible ? 'You are eligible to proceed' : 'Further clinical consultation required'}
                  </p>
                </div>
              </div>
            </div>

            <div className="p-8">
              <div className="mb-8">
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Risk Assessment</h3>
                <div className="flex items-center gap-2">
                  <span className="text-gray-700">Risk Level:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-bold uppercase ${result.risk_level === 'low' ? 'bg-green-100 text-green-800' :
                    result.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                    {result.risk_level}
                  </span>
                </div>
              </div>

              {result.recommendations && result.recommendations.length > 0 && (
                <div className="mb-8">
                  <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Recommendations</h3>
                  <ul className="space-y-3">
                    {result.recommendations.map((rec: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-3 text-gray-700">
                        <span className="text-teal-500 mt-1">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="flex flex-col sm:flex-row justify-end gap-4 pt-6 border-t border-gray-100">
                <Button variant="outline" onClick={() => navigate('/protocols')}>
                  Browse More Protocols
                </Button>
                {result.eligible && (
                  <Button variant="gradient" onClick={() => navigate('/dashboard')}>
                    Go to Dashboard
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );

  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-3xl">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Pre-Screening Assessment
          </h1>
          <p className="text-lg text-gray-600">
            {protocol.name}
          </p>
        </div>

        <PreScreeningForm
          protocolId={protocol.id}
          protocolName={protocol.name}
          onSubmit={handleSubmit}
          onCancel={() => navigate('/protocols')}
        />
      </div>
    </div>
  );
};

export default PreScreeningPage;
