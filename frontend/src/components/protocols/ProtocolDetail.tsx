import React from 'react';
import type { Protocol, ProtocolStep, StepType } from '../../types/protocol';
import { Badge, Button, Modal } from '../common';

interface ProtocolDetailProps {
  protocol: Protocol;
  isOpen: boolean;
  onClose: () => void;
}

const stepTypeIcons: Record<StepType, string> = {
  screening: '🔍',
  preparation: '📋',
  dosing: '💊',
  integration: '🧘',
  decision_point: '🔀',
  followup: '📞',
};

const stepTypeLabels: Record<StepType, string> = {
  screening: 'Screening',
  preparation: 'Preparation',
  dosing: 'Dosing Session',
  integration: 'Integration',
  decision_point: 'Decision Point',
  followup: 'Follow-up',
};

const ProtocolDetail: React.FC<ProtocolDetailProps> = ({ protocol, isOpen, onClose }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={protocol.name}>
      <div className="space-y-6">
        {/* Header Info */}
        <div className="flex flex-wrap gap-2">
          <Badge variant="teal">{protocol.therapy_type.toUpperCase()}</Badge>
          <Badge variant="gray">{protocol.condition_treated.replace(/_/g, ' ')}</Badge>
          <Badge variant="blue">v{protocol.version}</Badge>
        </div>

        {/* Overview */}
        {protocol.overview && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Overview</h4>
            <p className="text-gray-600">{protocol.overview}</p>
          </div>
        )}

        {/* Protocol Details */}
        <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
          {protocol.duration_weeks && (
            <div>
              <span className="text-sm font-medium text-gray-700">Duration</span>
              <p className="text-lg font-semibold text-teal-600">{protocol.duration_weeks} weeks</p>
            </div>
          )}
          {protocol.total_sessions && (
            <div>
              <span className="text-sm font-medium text-gray-700">Total Sessions</span>
              <p className="text-lg font-semibold text-teal-600">{protocol.total_sessions}</p>
            </div>
          )}
          <div>
            <span className="text-sm font-medium text-gray-700">Evidence Level</span>
            <p className="text-sm text-gray-600">{protocol.evidence_level.replace(/_/g, ' ')}</p>
          </div>
          <div>
            <span className="text-sm font-medium text-gray-700">Status</span>
            <p className="text-sm text-gray-600 capitalize">{protocol.status}</p>
          </div>
        </div>

        {/* Protocol Steps */}
        {protocol.steps && protocol.steps.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Protocol Steps</h4>
            <div className="space-y-3">
              {protocol.steps.map((step: ProtocolStep, index: number) => (
                <div
                  key={step.id}
                  className="border border-gray-200 rounded-lg p-4 hover:border-teal-300 transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-teal-100 rounded-full flex items-center justify-center text-teal-600 font-semibold">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-lg">{stepTypeIcons[step.step_type]}</span>
                        <h5 className="font-semibold text-gray-900">{step.title}</h5>
                        <Badge variant="gray" className="text-xs">
                          {stepTypeLabels[step.step_type]}
                        </Badge>
                      </div>
                      {step.description && (
                        <p className="text-sm text-gray-600 mb-2">{step.description}</p>
                      )}
                      <div className="flex gap-4 text-xs text-gray-500">
                        {step.duration_minutes && (
                          <span>{step.duration_minutes} min</span>
                        )}
                        {step.safety_checks && step.safety_checks.length > 0 && (
                          <span>{step.safety_checks.length} safety checks</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Evidence Sources */}
        {protocol.evidence_sources && protocol.evidence_sources.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Evidence Sources</h4>
            <ul className="space-y-1">
              {protocol.evidence_sources.map((source, index) => (
                <li key={index} className="text-sm">
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-teal-600 hover:text-teal-700 underline"
                  >
                    {source.title}
                  </a>
                  <span className="text-gray-500 ml-2">({source.type})</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-between items-center pt-4 border-t border-gray-200">
          <Button
            variant="gradient"
            onClick={() => {
              // TODO: Navigate to pre-screening page with protocol ID
              console.log('Start pre-screening for protocol:', protocol.id);
              alert(`Pre-screening feature coming soon for ${protocol.name}!`);
            }}
          >
            Start Pre-Screening
          </Button>
          <Button onClick={onClose} variant="outline">Close</Button>
        </div>
      </div>
    </Modal>
  );
};

export default ProtocolDetail;
