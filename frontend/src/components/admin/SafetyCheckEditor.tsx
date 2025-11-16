import React, { useState } from 'react';
import { Card, Input, Button } from '../common';
import type { SafetyCheck } from '../../types/protocol';

interface SafetyCheckEditorProps {
  safetyCheck?: SafetyCheck;
  onSave: (safetyCheck: Partial<SafetyCheck>) => void;
  onCancel: () => void;
}

const SafetyCheckEditor: React.FC<SafetyCheckEditorProps> = ({ safetyCheck, onSave, onCancel }) => {
  const [formData, setFormData] = useState<Partial<SafetyCheck>>(
    safetyCheck || {
      check_type: 'absolute_contraindication',
      condition: {},
      severity: 'blocking',
      override_allowed: false,
      evidence_source: '',
    }
  );

  const [conditionKey, setConditionKey] = useState('');
  const [conditionValue, setConditionValue] = useState('');

  const handleChange = (field: keyof SafetyCheck, value: unknown) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleAddCondition = () => {
    if (conditionKey && conditionValue) {
      setFormData((prev) => ({
        ...prev,
        condition: { ...prev.condition, [conditionKey]: conditionValue },
      }));
      setConditionKey('');
      setConditionValue('');
    }
  };

  const handleRemoveCondition = (key: string) => {
    setFormData((prev) => {
      const newCondition = { ...prev.condition };
      delete newCondition[key];
      return { ...prev, condition: newCondition };
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <Card>
      <form onSubmit={handleSubmit} className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {safetyCheck ? 'Edit Safety Check' : 'Add Safety Check'}
        </h3>

        {/* Check Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Check Type *
          </label>
          <select
            value={formData.check_type}
            onChange={(e) => handleChange('check_type', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            required
          >
            <option value="absolute_contraindication">Absolute Contraindication</option>
            <option value="relative_contraindication">Relative Contraindication</option>
            <option value="risk_factor">Risk Factor</option>
          </select>
        </div>

        {/* Severity */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Severity *
          </label>
          <select
            value={formData.severity}
            onChange={(e) => handleChange('severity', e.target.value as 'blocking' | 'warning' | 'info')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            required
          >
            <option value="blocking">Blocking</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </select>
        </div>

        {/* Conditions */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Conditions
          </label>
          <div className="space-y-2 mb-2">
            {Object.entries(formData.condition || {}).map(([key, value]) => (
              <div key={key} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                <span className="flex-1 text-sm">
                  <strong>{key}:</strong> {String(value)}
                </span>
                <button
                  type="button"
                  onClick={() => handleRemoveCondition(key)}
                  className="text-red-600 hover:text-red-700"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-2">
            <Input
              type="text"
              placeholder="Condition key"
              value={conditionKey}
              onChange={(e) => setConditionKey(e.target.value)}
            />
            <div className="flex gap-2">
              <Input
                type="text"
                placeholder="Value"
                value={conditionValue}
                onChange={(e) => setConditionValue(e.target.value)}
              />
              <Button
                type="button"
                onClick={handleAddCondition}
                variant="outline"
                size="sm"
              >
                Add
              </Button>
            </div>
          </div>
        </div>

        {/* Override Allowed */}
        <div>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.override_allowed}
              onChange={(e) => handleChange('override_allowed', e.target.checked)}
              className="rounded border-gray-300 text-teal-600 focus:ring-teal-500"
            />
            <span className="ml-2 text-sm text-gray-700">
              Override allowed (with medical director approval)
            </span>
          </label>
        </div>

        {/* Evidence Source */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Evidence Source
          </label>
          <Input
            type="text"
            value={formData.evidence_source || ''}
            onChange={(e) => handleChange('evidence_source', e.target.value)}
            placeholder="e.g., FDA guidance, clinical trial data"
          />
        </div>

        {/* Buttons */}
        <div className="flex gap-2 pt-4">
          <Button type="submit">Save Safety Check</Button>
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default SafetyCheckEditor;
