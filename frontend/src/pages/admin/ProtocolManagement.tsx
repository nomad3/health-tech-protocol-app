import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Badge, Button, Card, Spinner } from '../../components/common';
import { useAppDispatch, useAppSelector } from '../../hooks';
import { deleteProtocol, fetchProtocols } from '../../store/protocolSlice';
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
                    <tr key={protocol.id} className="hover:bg-teal-50/50 transition-colors duration-150 group">
                      <td className="px-6 py-4">
                        <div>
                          <div className="text-sm font-semibold text-gray-900 group-hover:text-teal-700 transition-colors">
                            {protocol.name}
                          </div>
                          <div className="text-xs text-gray-500 mt-0.5">v{protocol.version}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge variant="teal">{protocol.therapy_type}</Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-600 capitalize">
                          {protocol.evidence_level.replace(/_/g, ' ')}
                        </span>
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
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-1 text-sm text-gray-600">
                          <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                          </svg>
                          <span className="font-medium">{protocol.steps?.length || 0}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="flex gap-2 justify-end opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                          <button
                            onClick={() => handleView()}
                            className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-teal-700 bg-teal-50 rounded-md hover:bg-teal-100 transition-colors"
                            title="View Protocol"
                          >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                            </svg>
                            View
                          </button>
                          <button
                            onClick={() => handleEdit(protocol.id)}
                            className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
                            title="Edit Protocol"
                          >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                            Edit
                          </button>
                          <button
                            onClick={() => handleDelete(protocol.id)}
                            className={`inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${deleteConfirm === protocol.id
                                ? 'text-white bg-red-600 hover:bg-red-700'
                                : 'text-red-700 bg-red-50 hover:bg-red-100'
                              }`}
                            title={deleteConfirm === protocol.id ? "Click again to confirm" : "Delete Protocol"}
                          >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
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
