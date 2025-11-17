import React from 'react';

export interface AvatarProps {
  name: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  src?: string;
  className?: string;
  onClick?: () => void;
}

const sizeClasses = {
  xs: 'w-6 h-6 text-xs',
  sm: 'w-8 h-8 text-sm',
  md: 'w-10 h-10 text-base',
  lg: 'w-12 h-12 text-lg',
  xl: 'w-16 h-16 text-2xl',
};

const getInitials = (name: string): string => {
  const parts = name.trim().split(' ');
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
};

const getColorFromName = (name: string): string => {
  const colors = [
    'bg-gradient-to-br from-purple-500 to-pink-500',
    'bg-gradient-to-br from-blue-500 to-cyan-500',
    'bg-gradient-to-br from-green-500 to-teal-500',
    'bg-gradient-to-br from-amber-500 to-orange-500',
    'bg-gradient-to-br from-red-500 to-pink-500',
    'bg-gradient-to-br from-indigo-500 to-purple-500',
  ];
  const index = name.charCodeAt(0) % colors.length;
  return colors[index];
};

const Avatar: React.FC<AvatarProps> = ({
  name,
  size = 'md',
  src,
  className = '',
  onClick,
}) => {
  const initials = getInitials(name);
  const gradient = getColorFromName(name);

  return (
    <div
      className={`${sizeClasses[size]} rounded-full flex items-center justify-center font-semibold text-white shadow-md ${
        onClick ? 'cursor-pointer hover:shadow-lg transition-shadow duration-200' : ''
      } ${className}`}
      onClick={onClick}
      title={name}
    >
      {src ? (
        <img src={src} alt={name} className="w-full h-full rounded-full object-cover" />
      ) : (
        <div className={`w-full h-full rounded-full flex items-center justify-center ${gradient}`}>
          {initials}
        </div>
      )}
    </div>
  );
};

export default Avatar;
