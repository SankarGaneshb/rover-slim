import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { SecurityScorecard } from '../components/SecurityScorecard';

describe('SecurityScorecard Component', () => {
  const mockScorecard = {
    hardening_score: 95,
    grade: 'A+',
    is_non_root: true,
    user_uid: 10001,
    has_zero_compilers: true,
    sbom_generated: true,
    checks: [
      {
        id: 'cis-4.1-non-root',
        name: 'Unprivileged User (Non-Root)',
        status: 'PASSED',
        standard: 'CIS Docker Benchmark 4.1',
        description: 'Container executes as unprivileged system user.',
        remediation: 'Verified secure.'
      }
    ]
  };

  it('renders CIS benchmark scorecard, score, and grade', () => {
    const handleFeedback = vi.fn();

    render(
      <SecurityScorecard
        scorecard={mockScorecard}
        onOpenFeedback={handleFeedback}
      />
    );

    expect(screen.getByText(/CIS Benchmark Security Scorecard/i)).toBeInTheDocument();
    expect(screen.getByText(/A\+/i)).toBeInTheDocument();
    expect(screen.getByText(/95/i)).toBeInTheDocument();
    expect(screen.getByText(/appuser \(UID 10001\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Zero Compilers in Prod/i)).toBeInTheDocument();
  });
});
