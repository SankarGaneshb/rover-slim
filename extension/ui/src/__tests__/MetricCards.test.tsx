import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MetricCards } from '../components/MetricCards';

describe('MetricCards Component', () => {
  const mockBaseline = {
    uncompressed_size_mb: 1000.0,
    compressed_size_mb: 350.0,
    build_context_mb: 12.0,
    layer_count: 18,
    wasted_space_mb: 150.0,
    wasted_percent: 15.0,
    total_packages: 40
  };

  const mockOptimized = {
    uncompressed_size_mb: 180.0,
    compressed_size_mb: 55.0,
    build_context_mb: 2.0,
    layer_count: 7,
    wasted_space_mb: 3.5,
    wasted_percent: 1.9,
    total_packages: 12
  };

  it('renders size reduction and savings percentage accurately', () => {
    render(<MetricCards baseline={mockBaseline} optimized={mockOptimized} status="PASSED" />);
    
    expect(screen.getByText(/Size Posture/i)).toBeInTheDocument();
    expect(screen.getByText(/-82\.0%/i)).toBeInTheDocument();
    expect(screen.getByText(/Image Footprint/i)).toBeInTheDocument();
    expect(screen.getAllByText(/180\.0/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Container Layer & Transfer Metrics Comparison/i)).toBeInTheDocument();
    expect(screen.getByText(/Uncompressed Image Size/i)).toBeInTheDocument();
  });
});
