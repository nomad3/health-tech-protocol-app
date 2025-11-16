import React from 'react';
import { Card } from '../common';
import Badge from '../common/Badge';
import type { Protocol, TherapyType, EvidenceLevel } from '../../types/protocol';

interface ProtocolCardProps {
  protocol: Protocol;
  onClick?: () => void;
}

const therapyTypeColors: Record<TherapyType, 'blue' | 'teal' | 'purple' | 'green' | 'amber' | 'gray'> = {
  psilocybin: 'purple',
  mdma: 'teal',
  ketamine: 'blue',
  lsd: 'green',
  ibogaine: 'amber',
  other: 'gray',
};

const evidenceLevelColors: Record<EvidenceLevel, 'green' | 'blue' | 'teal' | 'amber' | 'gray' | 'red'> = {
  fda_approved: 'green',
  phase_3_trial: 'blue',
  phase_2_trial: 'teal',
  phase_1_trial: 'amber',
  preclinical: 'gray',
  clinical_practice: 'teal',
};

const evidenceLevelLabels: Record<EvidenceLevel, string> = {
  fda_approved: 'FDA Approved',
  phase_3_trial: 'Phase 3 Trial',
  phase_2_trial: 'Phase 2 Trial',
  phase_1_trial: 'Phase 1 Trial',
  preclinical: 'Preclinical',
  clinical_practice: 'Clinical Practice',
};

const ProtocolCard: React.FC<ProtocolCardProps> = ({ protocol, onClick }) => {
  return (
    <Card
      onClick={onClick}
      className="cursor-pointer hover:shadow-lg transition-shadow duration-200"
    >
      <div className="space-y-3">
        <div className="flex items-start justify-between">
          <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
            {protocol.name}
          </h3>
          <Badge variant={evidenceLevelColors[protocol.evidence_level]}>
            {evidenceLevelLabels[protocol.evidence_level]}
          </Badge>
        </div>

        <div className="flex flex-wrap gap-2">
          <Badge variant={therapyTypeColors[protocol.therapy_type]}>
            {protocol.therapy_type.toUpperCase()}
          </Badge>
          <Badge variant="gray">{protocol.condition_treated.replace(/_/g, ' ')}</Badge>
        </div>

        {protocol.overview && (
          <p className="text-sm text-gray-600 line-clamp-3">{protocol.overview}</p>
        )}

        <div className="flex items-center justify-between pt-2 border-t border-gray-200">
          <div className="flex gap-4 text-sm text-gray-500">
            {protocol.duration_weeks && (
              <span>{protocol.duration_weeks} weeks</span>
            )}
            {protocol.total_sessions && (
              <span>{protocol.total_sessions} sessions</span>
            )}
          </div>
          <span className="text-xs text-gray-400">v{protocol.version}</span>
        </div>
      </div>
    </Card>
  );
};

export default ProtocolCard;
