import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { GoAConsole } from '../components/GoAConsole';

describe('GoAConsole Component', () => {
  it('renders startup integrity, health probes, and triggers re-verification', async () => {
    const onReVerify = vi.fn().mockResolvedValue(undefined);
    const mockGoaData = {
      overall_status: 'GREEN (PASSED)',
      startup_integrity: {
        command: 'python -c "import server"',
        status: 'PASSED',
        exit_code: 0,
        output: 'Startup Integrity verified'
      },
      probes: [
        { probe: 'HTTP /health', type: 'http', status: 'PASSED', latency_ms: 24, expected_status: 200 }
      ],
      static_assets: {
        status: 'PASSED',
        checked_paths: ['/static/index.html']
      }
    };

    render(<GoAConsole goaData={mockGoaData} onReVerify={onReVerify} />);

    expect(screen.getByText(/Sentinel State: GREEN \(PASSED\)/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Startup Integrity/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Active Health Probes/i)).toBeInTheDocument();

    const runBtn = screen.getByText(/Re-run GoA Health Sentinel/i);
    fireEvent.click(runBtn);
    expect(onReVerify).toHaveBeenCalled();
  });
});
