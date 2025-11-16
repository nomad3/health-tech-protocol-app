import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Card from './Card';

describe('Card', () => {
  it('renders children', () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  it('applies default classes', () => {
    const { container } = render(<Card>Content</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('bg-white', 'rounded-lg');
  });

  it('applies padding classes', () => {
    const { container, rerender } = render(<Card padding="none">Content</Card>);
    let card = container.firstChild as HTMLElement;
    expect(card).not.toHaveClass('p-3', 'p-6', 'p-8');

    rerender(<Card padding="sm">Content</Card>);
    card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('p-3');

    rerender(<Card padding="md">Content</Card>);
    card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('p-6');

    rerender(<Card padding="lg">Content</Card>);
    card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('p-8');
  });

  it('applies shadow classes', () => {
    const { container, rerender } = render(<Card shadow="none">Content</Card>);
    let card = container.firstChild as HTMLElement;
    expect(card).not.toHaveClass('shadow-sm', 'shadow-md', 'shadow-lg');

    rerender(<Card shadow="sm">Content</Card>);
    card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('shadow-sm');

    rerender(<Card shadow="md">Content</Card>);
    card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('shadow-md');

    rerender(<Card shadow="lg">Content</Card>);
    card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('shadow-lg');
  });

  it('accepts custom className', () => {
    const { container } = render(<Card className="custom-class">Content</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('custom-class');
  });
});
