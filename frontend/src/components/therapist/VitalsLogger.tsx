import React, { useState } from 'react';
import { Card, Input, Button } from '../common';
import type { VitalsData } from '../../types/therapist';

interface VitalsLoggerProps {
  initialVitals?: VitalsData;
  onSave: (vitals: VitalsData) => void;
  onCancel?: () => void;
}

const VitalsLogger: React.FC<VitalsLoggerProps> = ({ initialVitals, onSave, onCancel }) => {
  const [vitals, setVitals] = useState<Partial<VitalsData>>(
    initialVitals || {
      recorded_at: new Date().toISOString(),
    }
  );

  const handleChange = (field: keyof VitalsData, value: string) => {
    setVitals((prev) => ({
      ...prev,
      [field]: value === '' ? undefined : field === 'recorded_at' ? value : parseFloat(value),
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(vitals as VitalsData);
  };

  const isValidVitals = () => {
    return (
      vitals.blood_pressure_systolic ||
      vitals.blood_pressure_diastolic ||
      vitals.heart_rate ||
      vitals.temperature ||
      vitals.spo2
    );
  };

  return (
    <Card>
      <form onSubmit={handleSubmit} className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Vital Signs</h3>

        {/* Blood Pressure */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              BP Systolic (mmHg)
            </label>
            <Input
              type="number"
              min="60"
              max="250"
              value={vitals.blood_pressure_systolic || ''}
              onChange={(e) => handleChange('blood_pressure_systolic', e.target.value)}
              placeholder="120"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              BP Diastolic (mmHg)
            </label>
            <Input
              type="number"
              min="40"
              max="150"
              value={vitals.blood_pressure_diastolic || ''}
              onChange={(e) => handleChange('blood_pressure_diastolic', e.target.value)}
              placeholder="80"
            />
          </div>
        </div>

        {/* Heart Rate */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Heart Rate (bpm)
          </label>
          <Input
            type="number"
            min="40"
            max="200"
            value={vitals.heart_rate || ''}
            onChange={(e) => handleChange('heart_rate', e.target.value)}
            placeholder="72"
          />
        </div>

        {/* Temperature */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Temperature (°C)
          </label>
          <Input
            type="number"
            min="35"
            max="42"
            step="0.1"
            value={vitals.temperature || ''}
            onChange={(e) => handleChange('temperature', e.target.value)}
            placeholder="37.0"
          />
        </div>

        {/* SpO2 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            SpO2 (%)
          </label>
          <Input
            type="number"
            min="70"
            max="100"
            value={vitals.spo2 || ''}
            onChange={(e) => handleChange('spo2', e.target.value)}
            placeholder="98"
          />
        </div>

        {/* Recorded At */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Recorded At
          </label>
          <Input
            type="datetime-local"
            value={
              vitals.recorded_at
                ? new Date(vitals.recorded_at).toISOString().slice(0, 16)
                : ''
            }
            onChange={(e) => handleChange('recorded_at', new Date(e.target.value).toISOString())}
            required
          />
        </div>

        {/* Buttons */}
        <div className="flex gap-2 pt-4">
          <Button type="submit" disabled={!isValidVitals()}>
            Save Vitals
          </Button>
          {onCancel && (
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
          )}
        </div>
      </form>
    </Card>
  );
};

export default VitalsLogger;
