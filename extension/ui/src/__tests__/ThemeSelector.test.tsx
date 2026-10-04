import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ThemeSelector } from '../components/ThemeSelector';
import { loadSavedTheme, saveTheme, applyTheme, getEffectiveTheme, THEME_STORAGE_KEY } from '../utils/theme';

describe('ThemeSelector and theme utilities', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute('data-theme');
    document.documentElement.removeAttribute('data-theme-mode');
  });

  it('defaults to rover-custom theme', () => {
    expect(loadSavedTheme()).toBe('rover-custom');
    expect(getEffectiveTheme('rover-custom')).toBe('rover-custom');
  });

  it('saves and applies selected theme', () => {
    saveTheme('light');
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe('light');
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    expect(document.documentElement.getAttribute('data-theme-mode')).toBe('light');

    saveTheme('dark');
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  it('renders all theme options and handles clicks', () => {
    const handleThemeChange = vi.fn();
    render(<ThemeSelector currentTheme="rover-custom" onThemeChange={handleThemeChange} />);

    expect(screen.getByText('Rover Neon')).toBeInTheDocument();
    expect(screen.getByText('Light')).toBeInTheDocument();
    expect(screen.getByText('Dark')).toBeInTheDocument();
    expect(screen.getByText('System')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Light'));
    expect(handleThemeChange).toHaveBeenCalledWith('light');

    fireEvent.click(screen.getByText('System'));
    expect(handleThemeChange).toHaveBeenCalledWith('system');
  });
});
