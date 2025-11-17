import React from 'react';

export type InputVariant = 'default' | 'error' | 'success';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  variant?: InputVariant;
  fullWidth?: boolean;
  icon?: string;
  iconPosition?: 'left' | 'right';
}

const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  variant = 'default',
  fullWidth = false,
  icon,
  iconPosition = 'left',
  className = '',
  id,
  ...props
}) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

  const variantClasses = {
    default: 'border-gray-300 focus:border-teal-500 focus:ring-teal-500',
    error: 'border-red-500 focus:border-red-500 focus:ring-red-500',
    success: 'border-green-500 focus:border-green-500 focus:ring-green-500',
  };

  const actualVariant = error ? 'error' : variant;
  const widthClass = fullWidth ? 'w-full' : '';

  const inputClasses = `
    block rounded-lg border px-4 py-2.5 text-base
    focus:outline-none focus:ring-2 transition-all duration-200
    disabled:bg-gray-100 disabled:cursor-not-allowed
    ${variantClasses[actualVariant]}
    ${icon && iconPosition === 'left' ? 'pl-10' : ''}
    ${icon && iconPosition === 'right' ? 'pr-10' : ''}
    ${widthClass}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  return (
    <div className={widthClass}>
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-semibold text-gray-700 mb-2"
        >
          {label}
        </label>
      )}
      <div className="relative">
        {icon && iconPosition === 'left' && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg">
            {icon}
          </div>
        )}
        <input
          id={inputId}
          className={inputClasses}
          {...props}
        />
        {icon && iconPosition === 'right' && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg">
            {icon}
          </div>
        )}
      </div>
      {error && (
        <p className="mt-1.5 text-sm text-red-600 font-medium">{error}</p>
      )}
      {!error && helperText && (
        <p className="mt-1.5 text-sm text-gray-500">{helperText}</p>
      )}
    </div>
  );
};

export default Input;
