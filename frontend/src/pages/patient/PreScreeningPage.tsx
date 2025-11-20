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
      <div className="max-w-2xl mx-auto mt-10 p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-4">Screening Result</h2>

        <div className={`p-4 rounded-lg mb-6 ${result.eligible ? 'bg-green-50 border border-green-200' : 'bg-yellow-50 border border-yellow-200'
          }`}>
          <h3 className={`font-bold text-lg ${result.eligible ? 'text-green-800' : 'text-yellow-800'
            }`}>
            {result.eligible ? 'You are eligible to proceed' : 'Further consultation needed'}
          </h3>
          <p className="mt-2 text-gray-700">
            Risk Level: <span className="font-semibold capitalize">{result.risk_level}</span>
          </p>
        </div>

        {result.recommendations && result.recommendations.length > 0 && (
          <div className="mb-6">
            <h4 className="font-semibold text-gray-900 mb-2">Recommendations:</h4>
            <ul className="list-disc list-inside space-y-1 text-gray-700">
              {result.recommendations.map((rec: string, idx: number) => (
                <li key={idx}>{rec}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="flex justify-end gap-4">
          <Button variant="outline" onClick={() => navigate('/protocols')}>
            Back to Protocols
          </Button>
          {result.eligible && (
            <Button variant="gradient" onClick={() => navigate('/dashboard')}>
              Go to Dashboard
            </Button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <PreScreeningForm
        protocolId={protocol.id}
        protocolName={protocol.name}
        onSubmit={handleSubmit}
        onCancel={() => navigate('/protocols')}
      />
    </div>
  );
};

export default PreScreeningPage;
