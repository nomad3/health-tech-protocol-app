import React, { useState } from 'react';
import { Card, Button } from '../common';

interface NotesEditorProps {
  therapistNotes?: string;
  patientNotes?: string;
  onSave: (therapistNotes: string, patientNotes: string) => void;
  onCancel?: () => void;
}

const NotesEditor: React.FC<NotesEditorProps> = ({
  therapistNotes: initialTherapistNotes = '',
  patientNotes: initialPatientNotes = '',
  onSave,
  onCancel,
}) => {
  const [therapistNotes, setTherapistNotes] = useState(initialTherapistNotes);
  const [patientNotes, setPatientNotes] = useState(initialPatientNotes);
  const [activeTab, setActiveTab] = useState<'therapist' | 'patient'>('therapist');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(therapistNotes, patientNotes);
  };

  const isModified = therapistNotes !== initialTherapistNotes || patientNotes !== initialPatientNotes;

  return (
    <Card>
      <form onSubmit={handleSubmit} className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Session Notes</h3>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px space-x-8">
            <button
              type="button"
              onClick={() => setActiveTab('therapist')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'therapist'
                  ? 'border-teal-500 text-teal-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Therapist Notes
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('patient')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'patient'
                  ? 'border-teal-500 text-teal-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Patient Notes
            </button>
          </nav>
        </div>

        {/* Therapist Notes */}
        {activeTab === 'therapist' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Clinical observations, interventions, and plan
            </label>
            <textarea
              value={therapistNotes}
              onChange={(e) => setTherapistNotes(e.target.value)}
              rows={12}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 font-mono text-sm"
              placeholder="Enter clinical notes here...

Common sections:
- Subjective observations
- Objective measurements
- Assessment
- Plan"
            />
            <p className="text-xs text-gray-500 mt-1">
              {therapistNotes.length} characters
            </p>
          </div>
        )}

        {/* Patient Notes */}
        {activeTab === 'patient' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Patient-reported experiences and insights
            </label>
            <textarea
              value={patientNotes}
              onChange={(e) => setPatientNotes(e.target.value)}
              rows={12}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 font-mono text-sm"
              placeholder="Enter patient notes here...

Patient's perspective on:
- Session experience
- Insights gained
- Challenges faced
- Integration plans"
            />
            <p className="text-xs text-gray-500 mt-1">
              {patientNotes.length} characters
            </p>
          </div>
        )}

        {/* Auto-save indicator */}
        {isModified && (
          <div className="bg-amber-50 border border-amber-200 rounded-md p-3">
            <p className="text-sm text-amber-700">Unsaved changes</p>
          </div>
        )}

        {/* Buttons */}
        <div className="flex gap-2 pt-4">
          <Button type="submit" disabled={!isModified}>
            Save Notes
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

export default NotesEditor;
