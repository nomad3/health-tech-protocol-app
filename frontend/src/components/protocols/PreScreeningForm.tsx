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
    <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
      {/* Progress Indicator */}
      <div className="bg-gray-50 px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <span className="text-sm font-medium text-gray-500">Step 1 of 1</span>
        <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div className="h-full bg-teal-500 w-full rounded-full"></div>
        </div>
      </div>

      <div className="p-8">
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Medical Information Section */}
          <div className="space-y-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-full bg-teal-100 text-teal-600 flex items-center justify-center font-bold">1</div>
              <h3 className="text-lg font-bold text-gray-900">Medical Information</h3>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Medical History
              </label>
              <p className="text-sm text-gray-500 mb-3">
                Please describe any relevant medical conditions, past surgeries, or ongoing health issues.
              </p>
              <textarea
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-all duration-200 min-h-[120px]"
                value={formData.medicalHistory}
                onChange={(e) => setFormData({ ...formData, medicalHistory: e.target.value })}
                placeholder="e.g., Hypertension diagnosed in 2020..."
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Current Medications
              </label>
              <p className="text-sm text-gray-500 mb-3">
                List all prescription and over-the-counter medications, supplements, or vitamins you are currently taking.
              </p>
              <textarea
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-all duration-200 min-h-[100px]"
                value={formData.currentMedications}
                onChange={(e) => setFormData({ ...formData, currentMedications: e.target.value })}
                placeholder="e.g., Lisinopril 10mg daily..."
              />
            </div>
          </div>

          <div className="border-t border-gray-100 my-8"></div>

          {/* Safety & Consent Section */}
          <div className="space-y-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-full bg-teal-100 text-teal-600 flex items-center justify-center font-bold">2</div>
              <h3 className="text-lg font-bold text-gray-900">Safety & Consent</h3>
            </div>

            <div className="bg-amber-50 border border-amber-100 rounded-xl p-4">
              <div className="flex items-start">
                <div className="flex items-center h-5 mt-1">
                  <input
                    id="contraindications"
                    type="checkbox"
                    className="h-5 w-5 text-teal-600 focus:ring-teal-500 border-gray-300 rounded cursor-pointer"
                    checked={formData.hasContraindications}
                    onChange={(e) => setFormData({ ...formData, hasContraindications: e.target.checked })}
                  />
                </div>
                <div className="ml-3">
                  <label htmlFor="contraindications" className="font-bold text-gray-900 cursor-pointer">
                    I have reviewed the contraindications
                  </label>
                  <p className="text-sm text-gray-600 mt-1">
                    I confirm that I have read and understood the contraindications for this therapy type. I understand that certain medical conditions may exclude me from eligibility.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
              <div className="flex items-start">
                <div className="flex items-center h-5 mt-1">
                  <input
                    id="consent"
                    type="checkbox"
                    required
                    className="h-5 w-5 text-teal-600 focus:ring-teal-500 border-gray-300 rounded cursor-pointer"
                    checked={formData.consent}
                    onChange={(e) => setFormData({ ...formData, consent: e.target.checked })}
                  />
                </div>
                <div className="ml-3">
                  <label htmlFor="consent" className="font-bold text-gray-900 cursor-pointer">
                    Informed Consent
                  </label>
                  <p className="text-sm text-gray-600 mt-1">
                    I agree to participate in this pre-screening assessment and authorize the review of my provided medical information by a qualified healthcare professional.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-4 pt-6 border-t border-gray-100">
            <Button type="button" variant="ghost" onClick={onCancel}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="gradient"
              disabled={!formData.consent}
              className="px-8"
            >
              Submit Assessment
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PreScreeningForm;
