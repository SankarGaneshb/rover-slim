import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { DiffViewer } from '../components/DiffViewer';

describe('DiffViewer Component', () => {
  it('renders side-by-side diff and triggers onApply action', async () => {
    const onApply = vi.fn().mockResolvedValue(undefined);
    const onRollback = vi.fn().mockResolvedValue(undefined);

    render(
      <DiffViewer
        originalDockerfile="FROM python:3.11\nCMD python server.py"
        optimizedDockerfile={'FROM python:3.11 AS builder\nFROM python:3.11\nCMD ["python", "server.py"]'}
        unifiedDiff="--- baseline\n+++ optimized"
        improvements={[{ type: 'SECURITY', title: 'Non-root user', description: 'Enforced appuser' }]}
        onApply={onApply}
        onRollback={onRollback}
      />
    );

    expect(screen.getByText(/Side-by-Side View/i)).toBeInTheDocument();
    expect(screen.getByText(/Unified Diff/i)).toBeInTheDocument();
    expect(screen.getByText(/Non-root user/i)).toBeInTheDocument();

    const applyBtn = screen.getByText(/Apply to Project/i);
    fireEvent.click(applyBtn);
    expect(onApply).toHaveBeenCalled();
  });
});
