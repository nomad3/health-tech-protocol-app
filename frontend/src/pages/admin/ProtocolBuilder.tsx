import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../hooks';
import { fetchProtocol, createProtocol, updateProtocol } from '../../store/protocolSlice';
import { Card, Input, Button, Spinner, Badge } from '../../components/common';
import StepEditor from '../../components/admin/StepEditor';
import SafetyCheckEditor from '../../components/admin/SafetyCheckEditor';
import { TherapyType, EvidenceLevel, type Protocol, type ProtocolStep, type SafetyCheck } from '../../types/protocol';
import protocolService from '../../services/protocolService';

const ProtocolBuilder: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { selectedProtocol, loading } = useAppSelector((state) => state.protocol);
  const isEditMode = id !== 'new';

  const [formData, setFormData] = useState<Partial<Protocol>>({
    name: '',
    version: '1.0',
    status: 'draft',
    therapy_type: TherapyType.PSILOCYBIN,
    condition_treated: '',
    evidence_level: EvidenceLevel.CLINICAL_PRACTICE,
    overview: '',
    duration_weeks: undefined,
    total_sessions: undefined,
    steps: [],
  });

  const [showStepEditor, setShowStepEditor] = useState(false);
  const [editingStep, setEditingStep] = useState<ProtocolStep | null>(null);
  const [showSafetyEditor, setShowSafetyEditor] = useState(false);
  const [editingStepId, setEditingStepId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isEditMode && id) {
      dispatch(fetchProtocol(parseInt(id)));
    }
  }, [dispatch, id, isEditMode]);

  useEffect(() => {
    if (selectedProtocol && isEditMode) {
      setFormData(selectedProtocol);
    }
  }, [selectedProtocol, isEditMode]);

  const handleChange = (field: keyof Protocol, value: unknown) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);

      if (isEditMode && id) {
        await dispatch(updateProtocol({ id: parseInt(id), updates: formData }));
      } else {
        await dispatch(createProtocol(formData));
      }

      navigate('/admin/protocols');
    } catch (err) {
      setError('Failed to save protocol');
      console.error('Save error:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleAddStep = () => {
    setEditingStep(null);
    setShowStepEditor(true);
  };

  const handleEditStep = (step: ProtocolStep) => {
    setEditingStep(step);
    setShowStepEditor(true);
  };

  const handleSaveStep = async (step: Partial<ProtocolStep>) => {
    try {
      if (isEditMode && id) {
        if (editingStep) {
          await protocolService.updateProtocolStep(parseInt(id), editingStep.id, step);
        } else {
          await protocolService.addProtocolStep(parseInt(id), step);
        }
        // Refresh protocol
        dispatch(fetchProtocol(parseInt(id)));
      } else {
        // In create mode, just add to local state
        const newSteps = formData.steps || [];
        if (editingStep) {
          const index = newSteps.findIndex((s) => s.id === editingStep.id);
          newSteps[index] = { ...editingStep, ...step };
        } else {
          newSteps.push({ ...step, id: Date.now() } as ProtocolStep);
        }
        setFormData((prev) => ({ ...prev, steps: newSteps }));
      }
      setShowStepEditor(false);
      setEditingStep(null);
    } catch (err) {
      setError('Failed to save step');
      console.error('Step save error:', err);
    }
  };

  const handleDeleteStep = async (stepId: number) => {
    try {
      if (isEditMode && id) {
        await protocolService.deleteProtocolStep(parseInt(id), stepId);
        dispatch(fetchProtocol(parseInt(id)));
      } else {
        setFormData((prev) => ({
          ...prev,
          steps: (prev.steps || []).filter((s) => s.id !== stepId),
        }));
      }
    } catch (err) {
      setError('Failed to delete step');
      console.error('Delete step error:', err);
    }
  };

  const handleAddSafetyCheck = (stepId: number) => {
    setEditingStepId(stepId);
    setShowSafetyEditor(true);
  };

  const handleSaveSafetyCheck = async (safetyCheck: Partial<SafetyCheck>) => {
    try {
      if (isEditMode && id && editingStepId) {
        await protocolService.addSafetyCheck(parseInt(id), editingStepId, safetyCheck);
        dispatch(fetchProtocol(parseInt(id)));
      }
      setShowSafetyEditor(false);
      setEditingStepId(null);
    } catch (err) {
      setError('Failed to save safety check');
      console.error('Safety check error:', err);
    }
  };

  if (loading && isEditMode) {
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {isEditMode ? 'Edit Protocol' : 'Create New Protocol'}
          </h1>
          <p className="text-gray-600">
            {isEditMode ? 'Update protocol details and steps' : 'Build a new therapy protocol'}
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Protocol Details */}
        <Card className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Protocol Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Protocol Name *
              </label>
              <Input
                type="text"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="e.g., Psilocybin for Depression"
                required
              />
            </div>

            {/* Version */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Version *</label>
              <Input
                type="text"
                value={formData.version}
                onChange={(e) => handleChange('version', e.target.value)}
                placeholder="1.0"
                required
              />
            </div>

            {/* Therapy Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Therapy Type *
              </label>
              <select
                value={formData.therapy_type}
                onChange={(e) => handleChange('therapy_type', e.target.value as TherapyType)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                required
              >
                {Object.values(TherapyType).map((type) => (
                  <option key={type} value={type}>
                    {type.toUpperCase()}
                  </option>
                ))}
              </select>
            </div>

            {/* Condition Treated */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Condition Treated *
              </label>
              <Input
                type="text"
                value={formData.condition_treated}
                onChange={(e) => handleChange('condition_treated', e.target.value)}
                placeholder="e.g., treatment_resistant_depression"
                required
              />
            </div>

            {/* Evidence Level */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Evidence Level *
              </label>
              <select
                value={formData.evidence_level}
                onChange={(e) => handleChange('evidence_level', e.target.value as EvidenceLevel)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                required
              >
                {Object.values(EvidenceLevel).map((level) => (
                  <option key={level} value={level}>
                    {level.replace(/_/g, ' ').toUpperCase()}
                  </option>
                ))}
              </select>
            </div>

            {/* Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                value={formData.status}
                onChange={(e) => handleChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                <option value="draft">Draft</option>
                <option value="active">Active</option>
                <option value="archived">Archived</option>
              </select>
            </div>

            {/* Duration */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Duration (weeks)
              </label>
              <Input
                type="number"
                min="1"
                value={formData.duration_weeks || ''}
                onChange={(e) =>
                  handleChange('duration_weeks', e.target.value ? parseInt(e.target.value) : undefined)
                }
                placeholder="12"
              />
            </div>

            {/* Total Sessions */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Total Sessions
              </label>
              <Input
                type="number"
                min="1"
                value={formData.total_sessions || ''}
                onChange={(e) =>
                  handleChange('total_sessions', e.target.value ? parseInt(e.target.value) : undefined)
                }
                placeholder="10"
              />
            </div>
          </div>

          {/* Overview */}
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Overview</label>
            <textarea
              value={formData.overview || ''}
              onChange={(e) => handleChange('overview', e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              placeholder="Enter a comprehensive overview of this protocol..."
            />
          </div>
        </Card>

        {/* Protocol Steps */}
        <Card className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Protocol Steps</h2>
            <Button onClick={handleAddStep} size="sm">
              Add Step
            </Button>
          </div>

          {formData.steps && formData.steps.length > 0 ? (
            <div className="space-y-3">
              {formData.steps.map((step, index) => (
                <div key={step.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <Badge variant="gray">Step {index + 1}</Badge>
                        <Badge variant="teal">{step.step_type}</Badge>
                        <h3 className="font-semibold text-gray-900">{step.title}</h3>
                      </div>
                      {step.description && (
                        <p className="text-sm text-gray-600 mb-2">{step.description}</p>
                      )}
                      <div className="flex gap-4 text-xs text-gray-500">
                        {step.duration_minutes && <span>{step.duration_minutes} min</span>}
                        {step.safety_checks && (
                          <span>{step.safety_checks.length} safety checks</span>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleAddSafetyCheck(step.id)}
                        className="text-xs text-blue-600 hover:text-blue-700"
                      >
                        Add Safety Check
                      </button>
                      <button
                        onClick={() => handleEditStep(step)}
                        className="text-xs text-teal-600 hover:text-teal-700"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteStep(step.id)}
                        className="text-xs text-red-600 hover:text-red-700"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              No steps added yet. Click "Add Step" to get started.
            </p>
          )}
        </Card>

        {/* Step Editor Modal */}
        {showStepEditor && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <StepEditor
                step={editingStep || undefined}
                sequenceOrder={(formData.steps?.length || 0) + 1}
                onSave={handleSaveStep}
                onCancel={() => {
                  setShowStepEditor(false);
                  setEditingStep(null);
                }}
              />
            </div>
          </div>
        )}

        {/* Safety Check Editor Modal */}
        {showSafetyEditor && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <SafetyCheckEditor
                onSave={handleSaveSafetyCheck}
                onCancel={() => {
                  setShowSafetyEditor(false);
                  setEditingStepId(null);
                }}
              />
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-4 justify-end">
          <Button variant="outline" onClick={() => navigate('/admin/protocols')}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={saving || !formData.name}>
            {saving ? 'Saving...' : isEditMode ? 'Update Protocol' : 'Create Protocol'}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ProtocolBuilder;
