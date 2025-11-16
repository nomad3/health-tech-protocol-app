import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import SessionCard from './SessionCard';
import type { TherapySession } from '../../types/therapist';

describe('SessionCard', () => {
  const mockSession: TherapySession = {
    id: 1,
    treatment_plan_id: 1,
    protocol_step_id: 1,
    patient_id: 1,
    therapist_id: 1,
    scheduled_at: '2024-11-16T10:00:00Z',
    status: 'scheduled',
    session_type: 'Preparation Session',
    duration_minutes: 90,
    patient: {
      id: 1,
      user_id: 1,
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com',
      date_of_birth: '1985-01-01',
      status: 'active',
      created_at: '2024-01-01T00:00:00Z',
    },
    protocol_step: {
      id: 1,
      title: 'Initial Preparation Session',
      step_type: 'preparation',
    },
  };

  it('should render patient name', () => {
    render(<SessionCard session={mockSession} />);
    expect(screen.getByText('John Doe')).toBeDefined();
  });

  it('should render protocol step title', () => {
    render(<SessionCard session={mockSession} />);
    expect(screen.getByText('Initial Preparation Session')).toBeDefined();
  });

  it('should render status badge', () => {
    render(<SessionCard session={mockSession} />);
    expect(screen.getByText('scheduled')).toBeDefined();
  });

  it('should render duration', () => {
    render(<SessionCard session={mockSession} />);
    expect(screen.getByText('90 min')).toBeDefined();
  });

  it('should call onClick when clicked', () => {
    const onClick = vi.fn();
    const { container } = render(<SessionCard session={mockSession} onClick={onClick} />);

    const card = container.firstChild as HTMLElement;
    fireEvent.click(card);

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('should show pending documentation for past sessions', () => {
    const pastSession = {
      ...mockSession,
      scheduled_at: '2024-01-01T10:00:00Z', // Past date
      status: 'scheduled' as const,
    };

    render(<SessionCard session={pastSession} />);
    expect(screen.getByText(/Pending documentation/)).toBeDefined();
  });

  it('should not show pending documentation for completed sessions', () => {
    const completedSession = {
      ...mockSession,
      scheduled_at: '2024-01-01T10:00:00Z',
      status: 'completed' as const,
    };

    render(<SessionCard session={completedSession} />);
    expect(screen.queryByText(/Pending documentation/)).toBeNull();
  });
});
