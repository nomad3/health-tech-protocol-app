import React from 'react';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  shadow?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  hover?: boolean;
  gradient?: boolean;
  onClick?: () => void;
}

const Card: React.FC<CardProps> = ({
  children,
  className = '',
  padding = 'md',
  shadow = 'md',
  hover = false,
  gradient = false,
  onClick,
}) => {
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-6',
    lg: 'p-8',
  };

  const shadowClasses = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
    xl: 'shadow-xl',
  };

  const hoverClasses = hover || onClick
    ? 'transition-all duration-300 hover:shadow-xl hover:-translate-y-1 cursor-pointer'
    : '';

  const gradientClasses = gradient
    ? 'bg-gradient-to-br from-white to-gray-50 border border-gray-100'
    : 'bg-white';

  const classes = `rounded-xl ${paddingClasses[padding]} ${shadowClasses[shadow]} ${hoverClasses} ${gradientClasses} ${className}`.trim();

  return (
    <div className={classes} onClick={onClick}>
      {children}
    </div>
  );
};

export default Card;
