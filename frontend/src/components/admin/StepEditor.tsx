import React, { useState } from 'react';
import { Card, Input, Button } from '../common';
import { StepType, type ProtocolStep } from '../../types/protocol';

interface StepEditorProps {
  step?: ProtocolStep;
  sequenceOrder: number;
  onSave: (step: Partial<ProtocolStep>) => void;
  onCancel: () => void;
}

const StepEditor: React.FC<StepEditorProps> = ({ step, sequenceOrder, onSave, onCancel }) => {
  const [formData, setFormData] = useState<Partial<ProtocolStep>>(
    step || {
      sequence_order: sequenceOrder,
      step_type: StepType.SCREENING,
      title: '',
      description: '',
      duration_minutes: undefined,
      required_roles: [],
    }
  );

  const handleChange = (field: keyof ProtocolStep, value: unknown) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <Card>
      <form onSubmit={handleSubmit} className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {step ? 'Edit Step' : 'Add New Step'}
        </h3>

        {/* Step Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Step Type *
          </label>
          <select
            value={formData.step_type}
            onChange={(e) => handleChange('step_type', e.target.value as StepType)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            required
          >
            {Object.values(StepType).map((type) => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Title *
          </label>
          <Input
            type="text"
            value={formData.title}
            onChange={(e) => handleChange('title', e.target.value)}
            placeholder="e.g., Initial Psychiatric Evaluation"
            required
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={formData.description || ''}
            onChange={(e) => handleChange('description', e.target.value)}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            placeholder="Enter a detailed description of this step..."
          />
        </div>

        {/* Duration */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Duration (minutes)
          </label>
          <Input
            type="number"
            min="0"
            value={formData.duration_minutes || ''}
            onChange={(e) => handleChange('duration_minutes', e.target.value ? parseInt(e.target.value) : undefined)}
            placeholder="90"
          />
        </div>

        {/* Sequence Order */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Sequence Order
          </label>
          <Input
            type="number"
            min="1"
            value={formData.sequence_order}
            onChange={(e) => handleChange('sequence_order', parseInt(e.target.value))}
            required
          />
        </div>

        {/* Required Roles */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Required Roles
          </label>
          <div className="space-y-2">
            {['therapist', 'medical_director', 'psychiatrist'].map((role) => (
              <label key={role} className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.required_roles?.includes(role) || false}
                  onChange={(e) => {
                    const roles = formData.required_roles || [];
                    handleChange(
                      'required_roles',
                      e.target.checked
                        ? [...roles, role]
                        : roles.filter((r) => r !== role)
                    );
                  }}
                  className="rounded border-gray-300 text-teal-600 focus:ring-teal-500"
                />
                <span className="ml-2 text-sm text-gray-700 capitalize">
                  {role.replace('_', ' ')}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Buttons */}
        <div className="flex gap-2 pt-4">
          <Button type="submit">Save Step</Button>
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default StepEditor;
