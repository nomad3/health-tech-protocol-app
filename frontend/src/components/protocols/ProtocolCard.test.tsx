import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ProtocolCard from './ProtocolCard';
import { TherapyType, EvidenceLevel, type Protocol } from '../../types/protocol';

describe('ProtocolCard', () => {
  const mockProtocol: Protocol = {
    id: 1,
    name: 'Psilocybin for Depression',
    version: '1.0',
    status: 'active',
    therapy_type: TherapyType.PSILOCYBIN,
    condition_treated: 'treatment_resistant_depression',
    evidence_level: EvidenceLevel.PHASE_3,
    overview: 'A comprehensive protocol for treating depression with psilocybin',
    duration_weeks: 12,
    total_sessions: 10,
    created_by: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  it('should render protocol name', () => {
    render(<ProtocolCard protocol={mockProtocol} />);
    expect(screen.getByText('Psilocybin for Depression')).toBeDefined();
  });

  it('should render therapy type badge', () => {
    render(<ProtocolCard protocol={mockProtocol} />);
    expect(screen.getByText('PSILOCYBIN')).toBeDefined();
  });

  it('should render evidence level badge', () => {
    render(<ProtocolCard protocol={mockProtocol} />);
    expect(screen.getByText('Phase 3 Trial')).toBeDefined();
  });

  it('should render overview when provided', () => {
    render(<ProtocolCard protocol={mockProtocol} />);
    expect(
      screen.getByText('A comprehensive protocol for treating depression with psilocybin')
    ).toBeDefined();
  });

  it('should render duration and sessions', () => {
    render(<ProtocolCard protocol={mockProtocol} />);
    expect(screen.getByText('12 weeks')).toBeDefined();
    expect(screen.getByText('10 sessions')).toBeDefined();
  });

  it('should render version', () => {
    render(<ProtocolCard protocol={mockProtocol} />);
    expect(screen.getByText('v1.0')).toBeDefined();
  });

  it('should call onClick when clicked', () => {
    const onClick = vi.fn();
    const { container } = render(<ProtocolCard protocol={mockProtocol} onClick={onClick} />);

    const card = container.firstChild as HTMLElement;
    fireEvent.click(card);

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('should format condition treated correctly', () => {
    render(<ProtocolCard protocol={mockProtocol} />);
    expect(screen.getByText('treatment resistant depression')).toBeDefined();
  });
});
