import React from 'react';
import { Card, Badge } from '../common';
import type { TherapySession } from '../../types/therapist';

interface SessionCardProps {
  session: TherapySession;
  onClick?: () => void;
}

const statusColors: Record<string, 'green' | 'blue' | 'amber' | 'gray'> = {
  scheduled: 'blue',
  in_progress: 'amber',
  completed: 'green',
  cancelled: 'gray',
};

const SessionCard: React.FC<SessionCardProps> = ({ session, onClick }) => {
  const scheduledDate = new Date(session.scheduled_at);
  const isToday = scheduledDate.toDateString() === new Date().toDateString();
  const isPast = scheduledDate < new Date() && session.status !== 'completed';

  return (
    <Card
      onClick={onClick}
      className="cursor-pointer hover:shadow-md transition-shadow duration-200"
    >
      <div className="space-y-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">
              {session.patient?.first_name} {session.patient?.last_name}
            </h3>
            <p className="text-sm text-gray-600">
              {session.protocol_step?.title || session.session_type}
            </p>
          </div>
          <Badge variant={statusColors[session.status]}>
            {session.status.replace('_', ' ')}
          </Badge>
        </div>

        <div className="flex items-center gap-4 text-sm text-gray-600">
          <div className="flex items-center gap-1">
            <span>📅</span>
            <span className={isToday ? 'font-semibold text-teal-600' : ''}>
              {scheduledDate.toLocaleDateString()}
            </span>
          </div>
          <div className="flex items-center gap-1">
            <span>🕐</span>
            <span>{scheduledDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
          {session.duration_minutes && (
            <div className="flex items-center gap-1">
              <span>⏱️</span>
              <span>{session.duration_minutes} min</span>
            </div>
          )}
        </div>

        {isPast && (
          <div className="pt-2 border-t border-amber-200 bg-amber-50 -mx-4 -mb-4 px-4 py-2 rounded-b-lg">
            <p className="text-sm text-amber-700 font-medium">
              ⚠️ Pending documentation
            </p>
          </div>
        )}
      </div>
    </Card>
  );
};

export default SessionCard;
