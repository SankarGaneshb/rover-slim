import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { DependencyMatrix } from '../components/DependencyMatrix';

describe('DependencyMatrix Component', () => {
  it('renders production and development dependency columns and allows moving packages', () => {
    const onClassificationChange = vi.fn();
    const initialProd = ['fastapi==0.110.0', 'pydantic>=2.0'];
    const initialDev = ['pytest>=7.0.0', 'ruff==0.0.280'];
    const prunedList = [
      { package: 'pytest', action: 'MOVED_TO_DEV', reason: 'Test framework', estimated_size_mb: 25.0 }
    ];

    render(
      <DependencyMatrix
        initialProd={initialProd}
        initialDev={initialDev}
        prunedList={prunedList}
        onClassificationChange={onClassificationChange}
      />
    );

    expect(screen.getByText(/Production Runtime/i)).toBeInTheDocument();
    expect(screen.getByText(/Dev & Tooling Dependencies/i)).toBeInTheDocument();
    expect(screen.getByText('fastapi==0.110.0')).toBeInTheDocument();
    expect(screen.getByText('pytest>=7.0.0')).toBeInTheDocument();

    const moveBtns = screen.getAllByText(/Move to Dev/i);
    fireEvent.click(moveBtns[0]);
    expect(onClassificationChange).toHaveBeenCalled();
  });
});
