import React from 'react';
import type { EvidenceLevel, Protocol, TherapyType } from '../../types/protocol';
import { Badge } from '../common';

interface ProtocolCardProps {
  protocol: Protocol;
  onClick?: () => void;
}

const therapyTypeGradients: Partial<Record<TherapyType, string>> = {
  psilocybin: 'from-purple-500 to-pink-500',
  mdma: 'from-blue-500 to-cyan-500',
  ketamine: 'from-cyan-500 to-teal-500',
  lsd: 'from-green-500 to-emerald-500',
  ibogaine: 'from-amber-500 to-orange-500',
  other: 'from-indigo-500 to-purple-500',
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
  phase_3_trial: 'Phase 3',
  phase_2_trial: 'Phase 2',
  phase_1_trial: 'Phase 1',
  preclinical: 'Preclinical',
  clinical_practice: 'Clinical Practice',
};

const ProtocolCard: React.FC<ProtocolCardProps> = ({ protocol, onClick }) => {
  const gradient = therapyTypeGradients[protocol.therapy_type] || 'from-gray-500 to-slate-500';

  return (
    <div
      onClick={onClick}
      className="group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer overflow-hidden transform hover:-translate-y-2"
    >
      {/* Gradient Header */}
      <div className={`h-32 bg-gradient-to-br ${gradient} relative`}>
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="absolute top-4 right-4">
          <Badge variant={evidenceLevelColors[protocol.evidence_level]}>
            {evidenceLevelLabels[protocol.evidence_level]}
          </Badge>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <div className="mb-3">
          <h3 className="text-xl font-bold text-gray-900 mb-2 line-clamp-2 group-hover:text-teal-600 transition-colors duration-200">
            {protocol.name}
          </h3>
          <div className="flex items-center gap-2 mb-3">
            <span className={`px-3 py-1 rounded-full text-xs font-semibold text-white bg-gradient-to-r ${gradient} shadow-sm`}>
              {protocol.therapy_type.toUpperCase()}
            </span>
            <Badge variant="gray">
              {protocol.condition_treated.replace(/_/g, ' ')}
            </Badge>
          </div>
        </div>

        {protocol.overview && (
          <p className="text-sm text-gray-600 line-clamp-3 mb-4 leading-relaxed">
            {protocol.overview}
          </p>
        )}

        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <div className="flex items-center gap-4 text-sm text-gray-500">
            {protocol.duration_weeks && (
              <div className="flex items-center gap-1">
                <span className="text-base">📅</span>
                <span className="font-medium">{protocol.duration_weeks}w</span>
              </div>
            )}
            {protocol.total_sessions && (
              <div className="flex items-center gap-1">
                <span className="text-base">🔄</span>
                <span className="font-medium">{protocol.total_sessions} sessions</span>
              </div>
            )}
          </div>
          <span className="text-xs text-gray-400 font-medium">v{protocol.version}</span>
        </div>
      </div>

      {/* Hover Effect Border */}
      <div className={`absolute inset-0 rounded-2xl border-2 border-transparent group-hover:border-teal-400 transition-all duration-300 pointer-events-none`}></div>
    </div>
  );
};

export default ProtocolCard;
