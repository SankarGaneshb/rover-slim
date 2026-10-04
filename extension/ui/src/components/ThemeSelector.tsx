import React from 'react';
import { Sun, Moon, Laptop, Palette } from 'lucide-react';
import { ThemeMode } from '../utils/theme';

interface ThemeSelectorProps {
  currentTheme: ThemeMode;
  onThemeChange: (theme: ThemeMode) => void;
}

export const ThemeSelector: React.FC<ThemeSelectorProps> = ({ currentTheme, onThemeChange }) => {
  const options: Array<{ id: ThemeMode; label: string; icon: React.ReactNode; tooltip: string }> = [
    {
      id: 'rover-custom',
      label: 'Rover Neon',
      icon: <Palette size={14} />,
      tooltip: 'Custom Rover-Slim Cyberpunk Dark Theme (Default)',
    },
    {
      id: 'light',
      label: 'Light',
      icon: <Sun size={14} />,
      tooltip: 'Standard Docker Desktop Light Theme',
    },
    {
      id: 'dark',
      label: 'Dark',
      icon: <Moon size={14} />,
      tooltip: 'Standard Docker Desktop Dark Theme',
    },
    {
      id: 'system',
      label: 'System',
      icon: <Laptop size={14} />,
      tooltip: 'Use System / Docker Desktop Settings',
    },
  ];

  return (
    <div
      role="group"
      aria-label="Theme selection"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        background: 'var(--bg-card-secondary)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        padding: '2px',
        gap: '2px',
      }}
    >
      {options.map((option) => {
        const isActive = currentTheme === option.id;
        return (
          <button
            key={option.id}
            type="button"
            title={option.tooltip}
            onClick={() => onThemeChange(option.id)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 8px',
              fontSize: '0.75rem',
              fontWeight: 600,
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              background: isActive ? 'var(--bg-card)' : 'transparent',
              color: isActive ? 'var(--accent-blue)' : 'var(--text-muted)',
              boxShadow: isActive ? '0 1px 3px rgba(0,0,0,0.2)' : 'none',
              outline: 'none',
            }}
          >
            {option.icon}
            <span className="theme-btn-label">{option.label}</span>
          </button>
        );
      })}
    </div>
  );
};
