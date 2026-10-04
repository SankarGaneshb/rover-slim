import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { BloatExplainerCard } from '../components/BloatExplainerCard';

describe('BloatExplainerCard Component', () => {
  const mockReport = {
    project_path: '/test/app',
    total_bloat_mb: 685.0,
    potential_reduction_pct: 72.5,
    findings: [
      {
        id: 'compiler-toolchain-leak',
        category: 'COMPILER_TOOLCHAIN',
        title: 'Build-time Compilers Retained in Production Image',
        severity: 'HIGH',
        wasted_mb: 420.0,
        explanation: 'Compilers like gcc are installed in runtime stage.',
        remediation: 'Rover-Slim synthesizes a 2-stage multi-stage build.'
      },
      {
        id: 'dev-dependency-bloat',
        category: 'DEV_DEPENDENCIES',
        title: 'Development & Test Packages Bundled in Production',
        severity: 'HIGH',
        wasted_mb: 170.0,
        explanation: 'Tools like pytest are bundled in prod.',
        remediation: 'Rover-Slim segregates runtime packages into requirements-prod.txt.'
      }
    ],
    has_single_stage: true,
    has_root_user: true,
    missing_dockerignore: true
  };

  it('renders bloat diagnosis and recoverable fat', () => {
    const handleApply = vi.fn();
    const handleFeedback = vi.fn();

    render(
      <BloatExplainerCard
        report={mockReport}
        onApplyOptimization={handleApply}
        onOpenFeedback={handleFeedback}
      />
    );

    expect(screen.getByText(/Why Is My Image Fat\?/i)).toBeInTheDocument();
    expect(screen.getByText(/~685 MB/i)).toBeInTheDocument();
    expect(screen.getByText(/-73%/i)).toBeInTheDocument();
    expect(screen.getByText(/Build-time Compilers Retained in Production Image/i)).toBeInTheDocument();

    const slimBtn = screen.getByText(/1-Click Auto-Slim Fix/i);
    fireEvent.click(slimBtn);
    expect(handleApply).toHaveBeenCalledTimes(1);
  });
});
