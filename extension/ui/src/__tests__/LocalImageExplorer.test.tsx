import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { LocalImageExplorer } from '../components/LocalImageExplorer';

describe('LocalImageExplorer Component', () => {
  it('renders docker images list, search bar, and triggers audit', () => {
    const onSelectAndAudit = vi.fn();
    const onRefresh = vi.fn().mockResolvedValue(undefined);
    const mockImages = [
      { id: 'sha256:123', tag: 'market-rover-app:latest', size_mb: 1080.0, created: '2 hours ago' },
      { id: 'sha256:456', tag: 'redis:7-alpine', size_mb: 55.0, created: '3 days ago' }
    ];

    render(
      <LocalImageExplorer
        images={mockImages}
        selectedImage="market-rover-app:latest"
        onSelectAndAudit={onSelectAndAudit}
        onRefresh={onRefresh}
        isLoading={false}
      />
    );

    expect(screen.getByText('market-rover-app:latest')).toBeInTheDocument();
    expect(screen.getByText('redis:7-alpine')).toBeInTheDocument();
    expect(screen.getByText(/1\.05 GB/i)).toBeInTheDocument();

    const searchInput = screen.getByPlaceholderText(/Search local images by repo or tag/i);
    fireEvent.change(searchInput, { target: { value: 'redis' } });
    expect(screen.queryByText('market-rover-app:latest')).not.toBeInTheDocument();
    expect(screen.getByText('redis:7-alpine')).toBeInTheDocument();
  });
});
