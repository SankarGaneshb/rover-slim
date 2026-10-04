import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { CloudROICalculator } from '../components/CloudROICalculator';

describe('CloudROICalculator Component', () => {
  it('renders multi-cloud egress savings and speedup metrics', () => {
    const handleFeedback = vi.fn();

    render(
      <CloudROICalculator
        baselineMb={1250}
        optimizedMb={210}
        onOpenFeedback={handleFeedback}
      />
    );

    expect(screen.getByText(/Cloud-Agnostic FinOps ROI Calculator/i)).toBeInTheDocument();
    expect(screen.getByText(/AWS \(ECR \/ ECS \/ EKS\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Google Cloud \(Artifact Reg \/ GKE\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Microsoft Azure \(ACR \/ AKS\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Cold-Start Speedup/i)).toBeInTheDocument();
  });
});
