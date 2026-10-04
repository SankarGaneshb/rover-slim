import React, { useState } from 'react';
import { MessageSquare, Heart, Sparkles, Send, Github, CheckCircle2, X } from 'lucide-react';
import { unlockBadge } from '../utils/gamification';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  context?: string;
  projectName?: string;
}

const EMOJI_OPTIONS = [
  { emoji: "😍", label: "Loved it" },
  { emoji: "🚀", label: "Blazing Fast" },
  { emoji: "💡", label: "Feature Idea" },
  { emoji: "🐛", label: "Bug Report" },
  { emoji: "👍", label: "Solid Tool" }
];

const QUICK_CHIPS = [
  "⚡ Cut cold-start in half",
  "📦 Saved >500MB fat",
  "🛡️ Great non-root user",
  "🧪 Ephemeral Sandbox is huge",
  "✨ Clean Multi-stage Dockerfile",
  "🔍 Need Node.js support",
  "📝 More CI/CD templates"
];

export const FeedbackModal: React.FC<FeedbackModalProps> = ({
  isOpen,
  onClose,
  context = "general",
  projectName = "my-project"
}) => {
  const [selectedEmoji, setSelectedEmoji] = useState("🚀");
  const [selectedChips, setSelectedChips] = useState<string[]>([]);
  const [comment, setComment] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const toggleChip = (chip: string) => {
    setSelectedChips(prev =>
      prev.includes(chip) ? prev.filter(c => c !== chip) : [...prev, chip]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await fetch("http://localhost:8000/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          rating_emoji: selectedEmoji,
          selected_chips: selectedChips,
          comment,
          feature_context: context,
          project_name: projectName
        })
      });
    } catch {
      // Local fallback
    }

    // Unlock "Voice of Rover" badge
    unlockBadge("voice-of-rover");

    setIsSubmitting(false);
    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      onClose();
    }, 2000);
  };

  const shareOnGithub = () => {
    const title = encodeURIComponent(`[Feedback] Rover-Slim Experience - ${selectedEmoji}`);
    const body = encodeURIComponent(
      `### Feedback Summary\n- **Reaction**: ${selectedEmoji}\n- **Highlights**: ${selectedChips.join(", ") || "N/A"}\n- **Context**: ${context}\n\n### User Notes\n${comment || "Loving the container optimization experience!"}`
    );
    window.open(`https://github.com/SankarGaneshb/rover-slim/issues/new?title=${title}&body=${body}`, "_blank");
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'rgba(0, 0, 0, 0.65)',
        backdropFilter: 'blur(4px)',
        padding: '1rem',
      }}
    >
      <div
        className="card"
        style={{
          maxWidth: '520px',
          width: '100%',
          overflow: 'hidden',
          padding: 0,
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3)',
          border: '1px solid var(--border-color)',
          background: 'var(--bg-card)',
          color: 'var(--text-main)',
        }}
      >
        {/* Modal Header */}
        <div
          style={{
            padding: '1rem 1.5rem',
            borderBottom: '1px solid var(--border-color)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: 'var(--bg-card-secondary)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div
              style={{
                padding: '0.5rem',
                borderRadius: '8px',
                background: 'var(--accent-green-glow)',
                color: 'var(--accent-green)',
                display: 'flex',
                alignItems: 'center',
              }}
            >
              <MessageSquare size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', margin: 0 }}>
                1-Click Rover Feedback
              </h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>
                Help shape the future of Rover-Slim
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            style={{
              color: 'var(--text-muted)',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              padding: '0.25rem',
              borderRadius: '6px',
            }}
          >
            <X size={18} />
          </button>
        </div>

        {submitted ? (
          <div style={{ padding: '2.5rem', textAlign: 'center' }}>
            <div
              style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                background: 'var(--accent-green-glow)',
                color: 'var(--accent-green)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem auto',
              }}
            >
              <CheckCircle2 size={36} />
            </div>
            <h4 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
              Thank You!
            </h4>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
              Badge <span style={{ color: 'var(--accent-green)', fontWeight: 600 }}>"Voice of Rover" 💬</span> unlocked in your Trophy Room!
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Emoji Selector */}
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                How was your experience?
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.5rem' }}>
                {EMOJI_OPTIONS.map(({ emoji, label }) => {
                  const isSelected = selectedEmoji === emoji;
                  return (
                    <button
                      key={emoji}
                      type="button"
                      onClick={() => setSelectedEmoji(emoji)}
                      style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        padding: '0.75rem 0.25rem',
                        borderRadius: '10px',
                        border: isSelected ? '1px solid var(--accent-green)' : '1px solid var(--border-color)',
                        background: isSelected ? 'var(--accent-green-glow)' : 'var(--bg-card-secondary)',
                        color: isSelected ? 'var(--text-main)' : 'var(--text-muted)',
                        cursor: 'pointer',
                        transform: isSelected ? 'scale(1.04)' : 'none',
                        transition: 'all 0.15s ease',
                      }}
                    >
                      <span style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>{emoji}</span>
                      <span style={{ fontSize: '0.65rem', fontWeight: 500, textAlign: 'center', lineHeight: 1.2 }}>{label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Quick Chips */}
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                Quick Highlights
              </label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {QUICK_CHIPS.map(chip => {
                  const isSelected = selectedChips.includes(chip);
                  return (
                    <button
                      key={chip}
                      type="button"
                      onClick={() => toggleChip(chip)}
                      style={{
                        fontSize: '0.75rem',
                        padding: '0.35rem 0.75rem',
                        borderRadius: '9999px',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                        border: isSelected ? '1px solid var(--accent-green)' : '1px solid var(--border-color)',
                        background: isSelected ? 'var(--accent-green-glow)' : 'var(--bg-card-secondary)',
                        color: isSelected ? 'var(--accent-green)' : 'var(--text-muted)',
                        fontWeight: isSelected ? 600 : 400,
                      }}
                    >
                      {chip}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Freeform Comment */}
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                Comments or Suggestions (Optional)
              </label>
              <textarea
                value={comment}
                onChange={e => setComment(e.target.value)}
                rows={2}
                placeholder="What did you like most? What would you like to see next?"
                className="input-field"
                style={{ width: '100%', resize: 'none' }}
              />
            </div>

            {/* Actions */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingTop: '0.75rem',
                borderTop: '1px solid var(--border-color)',
                flexWrap: 'wrap',
                gap: '0.5rem',
              }}
            >
              <button
                type="button"
                onClick={shareOnGithub}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  fontSize: '0.75rem',
                  color: 'var(--text-muted)',
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                }}
              >
                <Github size={14} />
                <span>Post as GitHub Issue</span>
              </button>

              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  type="button"
                  onClick={onClose}
                  className="btn btn-secondary"
                  style={{ padding: '0.45rem 0.9rem', fontSize: '0.75rem' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="btn btn-success"
                  style={{ padding: '0.45rem 1rem', fontSize: '0.75rem' }}
                >
                  <Send size={14} />
                  <span>{isSubmitting ? "Sending..." : "Submit"}</span>
                </button>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
