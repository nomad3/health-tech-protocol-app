import React from 'react';
import Button from './Button';

export interface EmptyStateProps {
  icon?: string;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  icon = '📋',
  title,
  description,
  action,
  className = '',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center py-12 px-4 text-center ${className}`}>
      <div className="w-20 h-20 rounded-full bg-gradient-to-br from-teal-50 to-blue-50 border border-teal-100 flex items-center justify-center text-4xl mb-6 shadow-sm">
        {icon}
      </div>
      <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>
      {description && (
        <p className="text-gray-500 max-w-sm mb-8 leading-relaxed">{description}</p>
      )}
      {action && (
        <Button onClick={action.onClick} variant="gradient">
          {action.label}
        </Button>
      )}
    </div>
  );
};

export default EmptyState;
