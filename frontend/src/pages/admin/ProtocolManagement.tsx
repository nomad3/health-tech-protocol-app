import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../hooks';
import { fetchProtocols, deleteProtocol } from '../../store/protocolSlice';
import { Card, Button, Badge, Spinner } from '../../components/common';
import type { Protocol } from '../../types/protocol';

const ProtocolManagement: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { protocols, loading, error } = useAppSelector((state) => state.protocol);
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);

  useEffect(() => {
    dispatch(fetchProtocols({ filters: {}, page: 1, pageSize: 50 }));
  }, [dispatch]);

  const handleCreate = () => {
    navigate('/admin/protocols/new');
  };

  const handleEdit = (id: number) => {
    navigate(`/admin/protocols/${id}/edit`);
  };

  const handleDelete = async (id: number) => {
    if (deleteConfirm === id) {
      await dispatch(deleteProtocol(id));
      setDeleteConfirm(null);
    } else {
      setDeleteConfirm(id);
      setTimeout(() => setDeleteConfirm(null), 3000);
    }
  };

  const handleView = () => {
    navigate(`/protocols`);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Protocol Management</h1>
            <p className="text-gray-600">Create and manage therapy protocols</p>
          </div>
          <Button onClick={handleCreate}>Create New Protocol</Button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Protocols Table */}
        <Card>
          {protocols.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg mb-4">No protocols yet</p>
              <Button onClick={handleCreate}>Create Your First Protocol</Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Evidence
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Steps
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {protocols.map((protocol: Protocol) => (
                    <tr key={protocol.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {protocol.name}
                          </div>
                          <div className="text-sm text-gray-500">v{protocol.version}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge variant="teal">{protocol.therapy_type}</Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {protocol.evidence_level.replace(/_/g, ' ')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge
                          variant={
                            protocol.status === 'active'
                              ? 'green'
                              : protocol.status === 'draft'
                              ? 'amber'
                              : 'gray'
                          }
                        >
                          {protocol.status}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {protocol.steps?.length || 0} steps
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex gap-2 justify-end">
                          <button
                            onClick={() => handleView()}
                            className="text-teal-600 hover:text-teal-900"
                          >
                            View
                          </button>
                          <button
                            onClick={() => handleEdit(protocol.id)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDelete(protocol.id)}
                            className={`${
                              deleteConfirm === protocol.id
                                ? 'text-red-900 font-bold'
                                : 'text-red-600 hover:text-red-900'
                            }`}
                          >
                            {deleteConfirm === protocol.id ? 'Confirm?' : 'Delete'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default ProtocolManagement;
