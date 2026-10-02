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

  it('limits display to 5 images by default and paginates cleanly without scrollbar', () => {
    const onSelectAndAudit = vi.fn();
    const onRefresh = vi.fn().mockResolvedValue(undefined);
    const mock11Images = Array.from({ length: 11 }, (_, i) => ({
      id: `sha256:id-${i + 1}`,
      tag: `service-image-${i + 1}:v1`,
      size_mb: 100.0 + i * 10,
      created: 'yesterday'
    }));

    render(
      <LocalImageExplorer
        images={mock11Images}
        selectedImage="service-image-1:v1"
        onSelectAndAudit={onSelectAndAudit}
        onRefresh={onRefresh}
        isLoading={false}
      />
    );

    // Initial page shows 5 images: service-image-1 through service-image-5
    expect(screen.getByText('service-image-1:v1')).toBeInTheDocument();
    expect(screen.getByText('service-image-5:v1')).toBeInTheDocument();
    expect(screen.queryByText('service-image-6:v1')).not.toBeInTheDocument();

    // Pagination info
    expect(screen.getByText(/Showing/i)).toHaveTextContent('Showing 1–5 of 11 images');
    expect(screen.getByText(/Page 1 of 3/i)).toBeInTheDocument();

    // Click Next button
    const nextBtn = screen.getByRole('button', { name: /Next/i });
    fireEvent.click(nextBtn);

    // Now page 2 shows service-image-6 through service-image-10
    expect(screen.getByText('service-image-6:v1')).toBeInTheDocument();
    expect(screen.getByText('service-image-10:v1')).toBeInTheDocument();
    expect(screen.queryByText('service-image-1:v1')).not.toBeInTheDocument();
    expect(screen.getByText(/Page 2 of 3/i)).toBeInTheDocument();

    // Click Show All
    const showAllBtn = screen.getByRole('button', { name: /Show All \(11\)/i });
    fireEvent.click(showAllBtn);

    // All 11 images visible
    expect(screen.getByText('service-image-1:v1')).toBeInTheDocument();
    expect(screen.getByText('service-image-11:v1')).toBeInTheDocument();
  });
});
