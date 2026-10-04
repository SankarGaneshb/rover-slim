export interface Badge {
  id: string;
  name: string;
  icon: string;
  description: string;
  unlocked: boolean;
  unlockedAt?: string;
}

export interface UserRank {
  level: number;
  title: string;
  icon: string;
  minXp: number;
  maxXp: number;
}

export const RANKS: UserRank[] = [
  { level: 1, title: "Docker Novice", icon: "🌱", minXp: 0, maxXp: 150 },
  { level: 2, title: "Layer Trimmer", icon: "✂️", minXp: 150, maxXp: 400 },
  { level: 3, title: "Sandbox Specialist", icon: "🧪", minXp: 400, maxXp: 750 },
  { level: 4, title: "FinOps Optimizer", icon: "💰", minXp: 750, maxXp: 1200 },
  { level: 5, title: "Grandmaster Architect", icon: "👑", minXp: 1200, maxXp: 2500 }
];

export interface UserGamificationState {
  score: number;
  xp: number;
  totalSavedMb: number;
  optimizationsCount: number;
  feedbacksCount: number;
  badges: Badge[];
}

const DEFAULT_BADGES: Badge[] = [
  {
    id: "bloat-buster",
    name: "Bloat Buster",
    icon: "🏆",
    description: "Reduced container size by over 40%",
    unlocked: false
  },
  {
    id: "speed-demon",
    name: "Speed Demon",
    icon: "⚡",
    description: "Achieved sub-2.0s cold-start boot time",
    unlocked: false
  },
  {
    id: "cis-guardian",
    name: "CIS Guardian",
    icon: "🛡️",
    description: "100% Non-root & 0-compiler verified container",
    unlocked: false
  },
  {
    id: "eco-champion",
    name: "Eco-Champion",
    icon: "🌿",
    description: "Saved more than 500 MB in egress bandwidth",
    unlocked: false
  },
  {
    id: "voice-of-rover",
    name: "Voice of Rover",
    icon: "💬",
    description: "Submitted feedback to shape Rover-Slim",
    unlocked: false
  }
];

const STORAGE_KEY = "rover_slim_gamification_v2";

export function loadGamificationState(): UserGamificationState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      const existingBadgeIds = new Set(parsed.badges.map((b: Badge) => b.id));
      const mergedBadges = [
        ...parsed.badges,
        ...DEFAULT_BADGES.filter(b => !existingBadgeIds.has(b.id))
      ];
      return {
        ...parsed,
        xp: parsed.xp || 350,
        badges: mergedBadges
      };
    }
  } catch {
    // Ignore error
  }
  return {
    score: 85,
    xp: 350,
    totalSavedMb: 1250,
    optimizationsCount: 3,
    feedbacksCount: 1,
    badges: DEFAULT_BADGES
  };
}

export function saveGamificationState(state: UserGamificationState): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Ignore error
  }
}

export function getCurrentRank(xp: number): { current: UserRank; next: UserRank | null; progressPct: number } {
  for (let i = 0; i < RANKS.length; i++) {
    const rank = RANKS[i];
    if (xp >= rank.minXp && (xp < rank.maxXp || i === RANKS.length - 1)) {
      const next = i < RANKS.length - 1 ? RANKS[i + 1] : null;
      const progressPct = next
        ? Math.min(100, Math.max(0, ((xp - rank.minXp) / (rank.maxXp - rank.minXp)) * 100))
        : 100;
      return { current: rank, next, progressPct };
    }
  }
  return { current: RANKS[0], next: RANKS[1], progressPct: 0 };
}

export function addXp(amount: number): { state: UserGamificationState; leveledUp: boolean } {
  const state = loadGamificationState();
  const oldRank = getCurrentRank(state.xp).current.level;
  state.xp += amount;
  const newRank = getCurrentRank(state.xp).current.level;
  saveGamificationState(state);
  return { state, leveledUp: newRank > oldRank };
}

export function unlockBadge(badgeId: string): { state: UserGamificationState; newlyUnlocked: boolean } {
  const state = loadGamificationState();
  let newlyUnlocked = false;
  state.badges = state.badges.map(badge => {
    if (badge.id === badgeId && !badge.unlocked) {
      newlyUnlocked = true;
      return { ...badge, unlocked: true, unlockedAt: new Date().toISOString() };
    }
    return badge;
  });
  if (newlyUnlocked) {
    state.score = Math.min(100, state.score + 5);
    state.xp += 150;
    saveGamificationState(state);
  }
  return { state, newlyUnlocked };
}

export function calculateHealthScore(baselineMb: number, optimizedMb: number, isRoot: boolean, hasGoaPassed: boolean): number {
  let score = 50;
  if (baselineMb > 0) {
    const reductionRatio = Math.max(0, (baselineMb - optimizedMb) / baselineMb);
    score += Math.round(reductionRatio * 30);
  }
  if (!isRoot) score += 10;
  if (hasGoaPassed) score += 10;
  return Math.min(100, Math.max(0, score));
}
