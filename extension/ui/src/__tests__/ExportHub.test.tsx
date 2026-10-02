import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ExportHub } from '../components/ExportHub';

describe('ExportHub Component', () => {
  it('loads export format and allows switching between markdown and CI templates', async () => {
    const onFetchExport = vi.fn().mockImplementation((fmt: string) => {
      if (fmt === 'markdown') return Promise.resolve('# Optimization Summary Markdown');
      if (fmt === 'github_action') return Promise.resolve('name: Rover-Slim CI');
      return Promise.resolve('{"status": "PASSED"}');
    });

    render(<ExportHub onFetchExport={onFetchExport} />);

    await waitFor(() => {
      expect(screen.getByText(/Optimization Summary Markdown/i)).toBeInTheDocument();
    });

    const ciBtn = screen.getByText(/GitHub Action \(CI\/CD\)/i);
    fireEvent.click(ciBtn);

    await waitFor(() => {
      expect(screen.getByText(/Rover-Slim CI/i)).toBeInTheDocument();
    });
  });
});
