import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { AchievementTrophyCard } from '../components/AchievementTrophyCard';

describe('AchievementTrophyCard Component', () => {
  it('renders badges and container eco-score', () => {
    const handleFeedback = vi.fn();

    render(
      <AchievementTrophyCard
        onOpenFeedback={handleFeedback}
      />
    );

    expect(screen.getByText(/Rover Trophy Room & Achievements/i)).toBeInTheDocument();
    expect(screen.getByText(/Container Eco-Score/i)).toBeInTheDocument();
    expect(screen.getByText(/Bloat Buster/i)).toBeInTheDocument();
    expect(screen.getByText(/Speed Demon/i)).toBeInTheDocument();
    expect(screen.getByText(/CIS Guardian/i)).toBeInTheDocument();
    expect(screen.getByText(/Eco-Champion/i)).toBeInTheDocument();
    expect(screen.getByText(/Voice of Rover/i)).toBeInTheDocument();
  });
});
