import React from 'react';

export interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md' | 'lg';
  withDot?: boolean;
  className?: string;
}

const statusStyles: Record<string, { bg: string; text: string; dot: string }> = {
  // Session statuses
  scheduled: { bg: 'bg-blue-50', text: 'text-blue-700', dot: 'bg-blue-500' },
  in_progress: { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-500' },
  completed: { bg: 'bg-green-50', text: 'text-green-700', dot: 'bg-green-500' },
  cancelled: { bg: 'bg-gray-50', text: 'text-gray-700', dot: 'bg-gray-500' },

  // Protocol statuses
  active: { bg: 'bg-green-50', text: 'text-green-700', dot: 'bg-green-500' },
  draft: { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-500' },
  archived: { bg: 'bg-gray-50', text: 'text-gray-700', dot: 'bg-gray-500' },

  // Patient statuses
  pending: { bg: 'bg-yellow-50', text: 'text-yellow-700', dot: 'bg-yellow-500' },
  approved: { bg: 'bg-green-50', text: 'text-green-700', dot: 'bg-green-500' },
  declined: { bg: 'bg-red-50', text: 'text-red-700', dot: 'bg-red-500' },

  // Default
  default: { bg: 'bg-gray-50', text: 'text-gray-700', dot: 'bg-gray-500' },
};

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-0.5 text-sm',
  lg: 'px-3 py-1 text-base',
};

const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  withDot = true,
  className = '',
}) => {
  const normalizedStatus = (status || 'unknown').toLowerCase().replace(/\s+/g, '_');
  const style = statusStyles[normalizedStatus] || statusStyles.default;
  const label = (status || 'unknown').replace(/_/g, ' ');

  return (
    <span
      className={`inline-flex items-center gap-1.5 ${sizeClasses[size]} ${style.bg} ${style.text} rounded-full font-medium ${className}`}
    >
      {withDot && <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />}
      <span className="capitalize">{label}</span>
    </span>
  );
};

export default StatusBadge;
