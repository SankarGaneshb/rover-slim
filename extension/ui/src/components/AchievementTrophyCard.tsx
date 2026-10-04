import React, { useState, useEffect } from 'react';
import { Award, Trophy, Zap, Shield, Flame, Sparkles, CheckCircle, Lock, Star, Target } from 'lucide-react';
import { loadGamificationState, UserGamificationState, getCurrentRank } from '../utils/gamification';
import { triggerConfetti } from '../utils/confetti';

interface AchievementTrophyCardProps {
  onOpenFeedback: (context: string) => void;
}

export const AchievementTrophyCard: React.FC<AchievementTrophyCardProps> = ({
  onOpenFeedback
}) => {
  const [state, setState] = useState<UserGamificationState>(loadGamificationState());

  useEffect(() => {
    setState(loadGamificationState());
  }, []);

  const unlockedCount = state.badges.filter(b => b.unlocked).length;
  const { current: rank, next: nextRank, progressPct } = getCurrentRank(state.xp);

  const handleCelebrate = () => {
    triggerConfetti();
  };

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1.25rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.25rem' }}>🏆</span>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>Rover Trophy Room & Achievements</h2>
            <span className="badge badge-orange">
              Level {rank.level} • {rank.title}
            </span>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '0.25rem 0 0 0' }}>
            Unlock achievements by trimming bloat, securing images, and accelerating boot times.
          </p>
        </div>

        {/* Eco-Score Pill */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button
            onClick={handleCelebrate}
            className="btn btn-secondary"
            style={{ fontSize: '0.75rem', padding: '0.45rem 0.85rem', borderColor: 'rgba(245, 158, 11, 0.4)', color: 'var(--accent-orange)' }}
          >
            <Sparkles size={14} color="var(--accent-orange)" />
            <span>Celebrate 🎉</span>
          </button>

          <div style={{ background: 'var(--bg-card-secondary)', padding: '0.5rem 1rem', borderRadius: '10px', border: '1px solid var(--border-color)', textAlign: 'right' }}>
            <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)', fontWeight: 600 }}>Container Eco-Score</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 900, color: 'var(--accent-green)' }}>{state.score} <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: 400 }}>/ 100</span></div>
          </div>
        </div>
      </div>

      {/* Level & XP Progression Banner */}
      <div style={{ background: 'var(--bg-card-secondary)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(245, 158, 11, 0.15)', border: '1px solid rgba(245, 158, 11, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.4rem' }}>
              {rank.icon}
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--text-main)' }}>Level {rank.level}: {rank.title}</span>
                <span style={{ fontSize: '0.65rem', background: 'rgba(245, 158, 11, 0.15)', color: 'var(--accent-orange)', padding: '0.1rem 0.4rem', borderRadius: '4px', fontFamily: 'monospace', fontWeight: 600 }}>
                  {state.xp} XP
                </span>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '0.15rem 0 0 0' }}>
                {nextRank ? `Earn ${nextRank.minXp - state.xp} more XP to reach Level ${nextRank.level} (${nextRank.title})` : "Maximum Grandmaster Rank Achieved!"}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.75rem' }}>
            <div style={{ textAlign: 'right' }}>
              <span style={{ color: 'var(--text-dim)', display: 'block', fontSize: '0.65rem', textTransform: 'uppercase', fontWeight: 700 }}>Total Space Trimmed</span>
              <span style={{ color: 'var(--accent-green)', fontWeight: 700 }}>{state.totalSavedMb.toLocaleString()} MB</span>
            </div>
            <div style={{ height: '24px', width: '1px', background: 'var(--border-color)' }} />
            <div style={{ textAlign: 'right' }}>
              <span style={{ color: 'var(--text-dim)', display: 'block', fontSize: '0.65rem', textTransform: 'uppercase', fontWeight: 700 }}>Optimizations</span>
              <span style={{ color: 'var(--accent-blue)', fontWeight: 700 }}>{state.optimizationsCount} runs</span>
            </div>
          </div>
        </div>

        {/* XP Progress Bar */}
        <div style={{ width: '100%', background: 'var(--bg-card)', height: '8px', borderRadius: '9999px', overflow: 'hidden', border: '1px solid var(--border-color)' }}>
          <div
            style={{
              background: 'linear-gradient(90deg, var(--accent-orange), var(--accent-green))',
              height: '100%',
              borderRadius: '9999px',
              width: `${progressPct}%`,
              transition: 'all 0.5s ease',
            }}
          />
        </div>
      </div>

      {/* Badges Progress Header */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <span style={{ fontWeight: 600 }}>Badge Milestones</span>
          <span style={{ color: 'var(--accent-green)', fontWeight: 600 }}>{unlockedCount} of {state.badges.length} Unlocked</span>
        </div>
        <div style={{ width: '100%', background: 'var(--bg-card-secondary)', height: '6px', borderRadius: '9999px', overflow: 'hidden', border: '1px solid var(--border-color)' }}>
          <div
            style={{
              background: 'linear-gradient(90deg, var(--accent-blue), var(--accent-green))',
              height: '100%',
              borderRadius: '9999px',
              width: `${(unlockedCount / state.badges.length) * 100}%`,
              transition: 'all 0.5s ease',
            }}
          />
        </div>
      </div>

      {/* Badges Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem' }}>
        {state.badges.map(badge => (
          <div
            key={badge.id}
            style={{
              padding: '1rem',
              borderRadius: '10px',
              border: badge.unlocked ? '1px solid rgba(245, 158, 11, 0.4)' : '1px solid var(--border-color)',
              background: badge.unlocked ? 'var(--bg-card-secondary)' : 'var(--bg-card)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              opacity: badge.unlocked ? 1 : 0.65,
              transition: 'all 0.2s ease',
            }}
          >
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem', position: 'relative' }}>
              <span>{badge.icon}</span>
              {!badge.unlocked && (
                <div style={{ position: 'absolute', bottom: '-4px', right: '-4px', background: 'var(--bg-card-secondary)', padding: '2px', borderRadius: '50%', border: '1px solid var(--border-color)', display: 'flex' }}>
                  <Lock size={10} color="var(--text-dim)" />
                </div>
              )}
            </div>
            <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>{badge.name}</h4>
            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem', lineHeight: '1.3' }}>{badge.description}</p>
            <div style={{ marginTop: '0.75rem' }}>
              {badge.unlocked ? (
                <span className="badge badge-green" style={{ fontSize: '0.65rem' }}>
                  Unlocked ✓
                </span>
              ) : (
                <span style={{ fontSize: '0.65rem', color: 'var(--text-dim)', fontFamily: 'monospace' }}>Locked</span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border-color)', fontSize: '0.75rem', color: 'var(--text-dim)', flexWrap: 'wrap' }}>
        <span>Level up your score by optimizing repositories and achieving Green-on-Arrival status!</span>
        <button
          onClick={() => onOpenFeedback("trophy_room")}
          style={{ color: 'var(--accent-orange)', background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '0.75rem', fontWeight: 500 }}
        >
          Submit Community Feedback
        </button>
      </div>
    </div>
  );
};
