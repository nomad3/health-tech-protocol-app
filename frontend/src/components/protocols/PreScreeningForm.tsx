import React, { useState } from 'react';
import { Button } from '../common';

interface PreScreeningFormProps {
  protocolId: number;
  protocolName: string;
  onSubmit: (data: PreScreeningData) => void;
  onCancel: () => void;
}

export interface PreScreeningData {
  medicalHistory: string;
  currentMedications: string;
  hasContraindications: boolean;
  consent: boolean;
}

const PreScreeningForm: React.FC<PreScreeningFormProps> = ({
  protocolName,
  onSubmit,
  onCancel,
}) => {
  const [formData, setFormData] = useState<PreScreeningData>({
    medicalHistory: '',
    currentMedications: '',
    hasContraindications: false,
    consent: false,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        Pre-Screening for {protocolName}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Medical History
          </label>
          <textarea
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-teal-500 focus:border-teal-500"
            rows={4}
            value={formData.medicalHistory}
            onChange={(e) => setFormData({ ...formData, medicalHistory: e.target.value })}
            placeholder="Please describe your relevant medical history..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Current Medications
          </label>
          <textarea
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-teal-500 focus:border-teal-500"
            rows={3}
            value={formData.currentMedications}
            onChange={(e) => setFormData({ ...formData, currentMedications: e.target.value })}
            placeholder="List any medications you are currently taking..."
          />
        </div>

        <div className="flex items-start">
          <div className="flex items-center h-5">
            <input
              id="contraindications"
              type="checkbox"
              className="h-4 w-4 text-teal-600 focus:ring-teal-500 border-gray-300 rounded"
              checked={formData.hasContraindications}
              onChange={(e) => setFormData({ ...formData, hasContraindications: e.target.checked })}
            />
          </div>
          <div className="ml-3 text-sm">
            <label htmlFor="contraindications" className="font-medium text-gray-700">
              I have reviewed the contraindications for this therapy
            </label>
            <p className="text-gray-500">Check this box if you have reviewed and understand the risks.</p>
          </div>
        </div>

        <div className="flex items-start">
          <div className="flex items-center h-5">
            <input
              id="consent"
              type="checkbox"
              required
              className="h-4 w-4 text-teal-600 focus:ring-teal-500 border-gray-300 rounded"
              checked={formData.consent}
              onChange={(e) => setFormData({ ...formData, consent: e.target.checked })}
            />
          </div>
          <div className="ml-3 text-sm">
            <label htmlFor="consent" className="font-medium text-gray-700">
              Informed Consent
            </label>
            <p className="text-gray-500">I agree to participate in the pre-screening process and share my medical information.</p>
          </div>
        </div>

        <div className="flex justify-end gap-4 pt-4 border-t border-gray-200">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" variant="gradient" disabled={!formData.consent}>
            Submit Screening
          </Button>
        </div>
      </form>
    </div>
  );
};

export default PreScreeningForm;
