export type ThemeMode = 'rover-custom' | 'light' | 'dark' | 'system';

export const THEME_STORAGE_KEY = 'rover_slim_theme_mode';

/**
 * Resolves the effective appearance ('rover-custom' | 'light' | 'dark')
 * based on selected mode and system preference.
 */
export function getEffectiveTheme(mode: ThemeMode): 'rover-custom' | 'light' | 'dark' {
  if (mode === 'rover-custom') {
    return 'rover-custom';
  }
  if (mode === 'light') {
    return 'light';
  }
  if (mode === 'dark') {
    return 'dark';
  }
  // 'system' mode: inspect OS / browser prefers-color-scheme
  if (typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
    return 'light';
  }
  return 'dark';
}

/**
 * Applies theme data-attribute and color-scheme to document root.
 */
export function applyTheme(mode: ThemeMode): void {
  if (typeof document === 'undefined') return;
  const effective = getEffectiveTheme(mode);
  document.documentElement.setAttribute('data-theme', effective);
  document.documentElement.setAttribute('data-theme-mode', mode);
  
  if (effective === 'light') {
    document.documentElement.style.colorScheme = 'light';
  } else {
    document.documentElement.style.colorScheme = 'dark';
  }
}

/**
 * Loads current saved theme mode, defaulting to 'rover-custom'.
 */
export function loadSavedTheme(): ThemeMode {
  try {
    const saved = localStorage.getItem(THEME_STORAGE_KEY) as ThemeMode | null;
    if (saved && ['rover-custom', 'light', 'dark', 'system'].includes(saved)) {
      return saved;
    }
  } catch (e) {
    console.warn('Unable to access localStorage for theme preference:', e);
  }
  return 'rover-custom';
}

/**
 * Saves and applies theme mode.
 */
export function saveTheme(mode: ThemeMode): void {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, mode);
  } catch (e) {
    console.warn('Unable to save theme preference:', e);
  }
  applyTheme(mode);
}
