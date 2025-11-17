import React from 'react';

export interface ProgressBarProps {
  value: number;
  max?: number;
  label?: string;
  color?: 'teal' | 'blue' | 'green' | 'purple' | 'amber' | 'red';
  size?: 'sm' | 'md' | 'lg';
  showPercentage?: boolean;
  animated?: boolean;
}

const colorClasses = {
  teal: 'bg-gradient-to-r from-teal-500 to-cyan-500',
  blue: 'bg-gradient-to-r from-blue-500 to-cyan-500',
  green: 'bg-gradient-to-r from-green-500 to-teal-500',
  purple: 'bg-gradient-to-r from-purple-500 to-pink-500',
  amber: 'bg-gradient-to-r from-amber-500 to-orange-500',
  red: 'bg-gradient-to-r from-red-500 to-orange-500',
};

const sizeClasses = {
  sm: 'h-1.5',
  md: 'h-2.5',
  lg: 'h-4',
};

const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  label,
  color = 'teal',
  size = 'md',
  showPercentage = false,
  animated = false,
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  return (
    <div className="w-full">
      {(label || showPercentage) && (
        <div className="flex items-center justify-between mb-2">
          {label && <span className="text-sm font-medium text-gray-700">{label}</span>}
          {showPercentage && (
            <span className="text-sm font-semibold text-gray-900">{percentage.toFixed(0)}%</span>
          )}
        </div>
      )}
      <div className={`w-full bg-gray-200 rounded-full overflow-hidden ${sizeClasses[size]}`}>
        <div
          className={`${sizeClasses[size]} ${colorClasses[color]} rounded-full transition-all duration-500 ease-out ${
            animated ? 'animate-pulse' : ''
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
