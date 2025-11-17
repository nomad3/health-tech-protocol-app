import React from 'react';

export interface StatCardProps {
  title: string;
  value: string | number;
  icon?: string;
  trend?: {
    value: number;
    label: string;
  };
  gradient?: 'teal' | 'blue' | 'green' | 'purple' | 'amber' | 'red';
  onClick?: () => void;
}

const gradientClasses = {
  teal: 'from-teal-500 to-cyan-500',
  blue: 'from-blue-500 to-cyan-500',
  green: 'from-green-500 to-teal-500',
  purple: 'from-purple-500 to-pink-500',
  amber: 'from-amber-500 to-orange-500',
  red: 'from-red-500 to-orange-500',
};

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  trend,
  gradient = 'teal',
  onClick,
}) => {
  return (
    <div
      className={`bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden ${
        onClick ? 'cursor-pointer transform hover:-translate-y-1' : ''
      }`}
      onClick={onClick}
    >
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">{title}</p>
          {icon && (
            <div
              className={`w-12 h-12 rounded-lg bg-gradient-to-br ${gradientClasses[gradient]} flex items-center justify-center text-white text-2xl shadow-md`}
            >
              {icon}
            </div>
          )}
        </div>
        <div className="space-y-2">
          <p className={`text-4xl font-bold bg-gradient-to-br ${gradientClasses[gradient]} bg-clip-text text-transparent`}>
            {value}
          </p>
          {trend && (
            <div className="flex items-center gap-2">
              <span
                className={`text-sm font-medium ${
                  trend.value >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {trend.value >= 0 ? '↑' : '↓'} {Math.abs(trend.value)}%
              </span>
              <span className="text-sm text-gray-500">{trend.label}</span>
            </div>
          )}
        </div>
      </div>
      <div className={`h-1 bg-gradient-to-r ${gradientClasses[gradient]}`}></div>
    </div>
  );
};

export default StatCard;
