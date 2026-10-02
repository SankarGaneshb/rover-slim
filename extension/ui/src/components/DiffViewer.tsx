import React, { useState } from 'react';
import { GitCompare, Check, RotateCcw, ShieldCheck, Zap, FileCode, CheckCircle } from 'lucide-react';

interface Improvement {
  type: string;
  title: string;
  description: string;
}

interface DiffViewerProps {
  originalDockerfile: string;
  optimizedDockerfile: string;
  unifiedDiff: string;
  improvements: Improvement[];
  onApply: () => Promise<void>;
  onRollback: () => Promise<void>;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({
  originalDockerfile,
  optimizedDockerfile,
  unifiedDiff,
  improvements,
  onApply,
  onRollback,
}) => {
  const [viewMode, setViewMode] = useState<'split' | 'unified'>('split');
  const [isApplying, setIsApplying] = useState(false);
  const [isRollingBack, setIsRollingBack] = useState(false);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  const handleApply = async () => {
    setIsApplying(true);
    setActionNotice(null);
    try {
      await onApply();
      setActionNotice('Artifacts successfully applied with safety checkpoint created!');
    } catch (e: any) {
      setActionNotice(`Apply error: ${e.message || 'Failed'}`);
    } finally {
      setIsApplying(false);
    }
  };

  const handleRollback = async () => {
    setIsRollingBack(true);
    setActionNotice(null);
    try {
      await onRollback();
      setActionNotice('Successfully restored project files from previous safety checkpoint.');
    } catch (e: any) {
      setActionNotice(`Rollback error: ${e.message || 'Failed'}`);
    } finally {
      setIsRollingBack(false);
    }
  };

  return (
    <div>
      {/* Top Action Header */}
      <div className="action-bar" style={{ justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ display: 'flex', background: 'var(--bg-card-secondary)', borderRadius: '8px', padding: '0.25rem', border: '1px solid var(--border-color)' }}>
            <button
              className={`btn ${viewMode === 'split' ? 'btn-secondary' : ''}`}
              style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem', background: viewMode === 'split' ? 'var(--border-color)' : 'transparent' }}
              onClick={() => setViewMode('split')}
            >
              Side-by-Side View
            </button>
            <button
              className={`btn ${viewMode === 'unified' ? 'btn-secondary' : ''}`}
              style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem', background: viewMode === 'unified' ? 'var(--border-color)' : 'transparent' }}
              onClick={() => setViewMode('unified')}
            >
              Unified Diff
            </button>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button
            className="btn btn-secondary"
            onClick={handleRollback}
            disabled={isRollingBack}
            title="Restore previous state from backup checkpoint"
          >
            <RotateCcw size={16} />
            {isRollingBack ? 'Restoring...' : 'Rollback Checkpoint'}
          </button>

          <button
            className="btn btn-success"
            onClick={handleApply}
            disabled={isApplying}
            title="Write Dockerfile, .dockerignore, and segregated requirements"
          >
            <Check size={16} />
            {isApplying ? 'Applying...' : 'Apply to Project'}
          </button>
        </div>
      </div>

      {actionNotice && (
        <div
          style={{
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid #10b981',
            borderRadius: '8px',
            padding: '0.75rem 1rem',
            color: '#34d399',
            fontSize: '0.85rem',
            marginBottom: '1.25rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <CheckCircle size={16} />
          {actionNotice}
        </div>
      )}

      {/* Structural Improvements Highlights */}
      {improvements && improvements.length > 0 && (
        <div className="card" style={{ marginBottom: '1.5rem', background: 'var(--bg-card)' }}>
          <h4 style={{ fontSize: '0.9rem', color: '#f8fafc', fontWeight: 600, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldCheck size={16} color="#38bdf8" /> Architectural & Security Enhancements Detected
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '0.75rem' }}>
            {improvements.map((imp, idx) => (
              <div
                key={idx}
                style={{
                  background: 'var(--bg-card-secondary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  padding: '0.6rem 0.85rem',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.2rem' }}>
                  <span className="badge badge-green" style={{ fontSize: '0.7rem' }}>
                    {imp.type}
                  </span>
                  <strong style={{ fontSize: '0.85rem', color: '#f1f5f9' }}>{imp.title}</strong>
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{imp.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Diff Representation */}
      {viewMode === 'split' ? (
        <div className="grid-2">
          {/* Baseline Dockerfile */}
          <div className="card">
            <div className="card-title">
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <FileCode size={16} color="#f59e0b" /> Original Dockerfile (Baseline)
              </span>
              <span className="badge badge-orange">Before</span>
            </div>
            <pre className="code-view">{originalDockerfile || '# No Dockerfile found in project root'}</pre>
          </div>

          {/* Synthesized Multi-Stage Dockerfile */}
          <div className="card" style={{ border: '1px solid rgba(16, 185, 129, 0.4)' }}>
            <div className="card-title">
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Zap size={16} color="#34d399" /> Synthesized Multi-Stage Dockerfile
              </span>
              <span className="badge badge-green">Optimized Candidate</span>
            </div>
            <pre className="code-view">{optimizedDockerfile}</pre>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="card-title">
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <GitCompare size={16} color="#38bdf8" /> Unified Patch Diff
            </span>
          </div>
          <pre className="code-view">
            {unifiedDiff.split('\n').map((line, i) => {
              let color = '#e2e8f0';
              let bg = 'transparent';
              if (line.startsWith('+') && !line.startsWith('+++')) {
                color = '#34d399';
                bg = 'rgba(16, 185, 129, 0.1)';
              } else if (line.startsWith('-') && !line.startsWith('---')) {
                color = '#f87171';
                bg = 'rgba(239, 68, 68, 0.1)';
              } else if (line.startsWith('@@')) {
                color = '#38bdf8';
              }
              return (
                <div key={i} style={{ color, background: bg, padding: '0 0.2rem' }}>
                  {line}
                </div>
              );
            })}
          </pre>
        </div>
      )}
    </div>
  );
};
