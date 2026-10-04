import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { FeedbackModal } from '../components/FeedbackModal';

describe('FeedbackModal Component', () => {
  it('renders modal with emoji reactions and quick chips', () => {
    const handleClose = vi.fn();

    render(
      <FeedbackModal
        isOpen={true}
        onClose={handleClose}
        context="general"
        projectName="my-service"
      />
    );

    expect(screen.getByText(/1-Click Rover Feedback/i)).toBeInTheDocument();
    expect(screen.getByText(/Loved it/i)).toBeInTheDocument();
    expect(screen.getByText(/Blazing Fast/i)).toBeInTheDocument();
    expect(screen.getByText(/⚡ Cut cold-start in half/i)).toBeInTheDocument();
    expect(screen.getByText(/Post as GitHub Issue/i)).toBeInTheDocument();

    const cancelBtn = screen.getByText(/Cancel/i);
    fireEvent.click(cancelBtn);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('does not render when isOpen is false', () => {
    const handleClose = vi.fn();

    const { container } = render(
      <FeedbackModal
        isOpen={false}
        onClose={handleClose}
      />
    );

    expect(container.firstChild).toBeNull();
  });
});
