import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { SandboxStudio } from '../components/SandboxStudio';

describe('SandboxStudio Component', () => {
  it('renders ephemeral sandbox terminal logs and probe runner', () => {
    const handleRollback = vi.fn();
    const handleFeedback = vi.fn();

    render(
      <SandboxStudio
        projectPath="/test/app"
        onRollback={handleRollback}
        onOpenFeedback={handleFeedback}
      />
    );

    expect(screen.getByText(/Ephemeral Sandbox Lab/i)).toBeInTheDocument();
    expect(screen.getByText(/Live Micro-Container Boot Stream/i)).toBeInTheDocument();
    expect(screen.getByText(/Live Probe Terminal/i)).toBeInTheDocument();
    expect(screen.getByText(/Rollback Snapshot/i)).toBeInTheDocument();

    const rollbackBtn = screen.getByText(/Rollback Snapshot/i);
    fireEvent.click(rollbackBtn);
    expect(handleRollback).toHaveBeenCalledTimes(1);
  });
});
