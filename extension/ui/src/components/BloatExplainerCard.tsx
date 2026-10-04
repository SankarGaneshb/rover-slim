import React, { useState } from 'react';
import { AlertTriangle, Cpu, PackageX, ShieldAlert, Sparkles, ArrowRight, CheckCircle, HelpCircle, ThumbsUp, Lightbulb } from 'lucide-react';

export interface BloatFinding {
  id: string;
  category: string;
  title: string;
  severity: string;
  wasted_mb: number;
  explanation: string;
  remediation: string;
}

export interface BloatDiagnosticReport {
  project_path: string;
  total_bloat_mb: number;
  potential_reduction_pct: number;
  findings: BloatFinding[];
  has_single_stage: boolean;
  has_root_user: boolean;
  missing_dockerignore: boolean;
}

interface BloatExplainerCardProps {
  report: BloatDiagnosticReport | null;
  onApplyOptimization: () => void;
  isOptimizing?: boolean;
  onOpenFeedback: (context: string) => void;
}

export const BloatExplainerCard: React.FC<BloatExplainerCardProps> = ({
  report,
  onApplyOptimization,
  isOptimizing = false,
  onOpenFeedback
}) => {
  const [selectedFinding, setSelectedFinding] = useState<string | null>(null);
  const [helpfulFeedbackGiven, setHelpfulFeedbackGiven] = useState(false);

  if (!report) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
        <HelpCircle size={36} color="var(--text-dim)" style={{ margin: '0 auto 0.5rem auto' }} />
        <p style={{ fontSize: '0.875rem' }}>Run an audit to diagnose container fat and structural bloat.</p>
      </div>
    );
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "COMPILER_TOOLCHAIN":
        return <Cpu size={18} color="var(--accent-orange)" />;
      case "DEV_DEPENDENCIES":
        return <PackageX size={18} color="var(--accent-red)" />;
      case "CONTEXT_LEAKAGE":
        return <AlertTriangle size={18} color="var(--accent-blue)" />;
      case "ROOT_SECURITY":
        return <ShieldAlert size={18} color="var(--accent-red)" />;
      default:
        return <Sparkles size={18} color="var(--accent-green)" />;
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity.toUpperCase()) {
      case "CRITICAL":
        return <span className="badge badge-red">Critical</span>;
      case "HIGH":
        return <span className="badge badge-orange">High Bloat</span>;
      case "MEDIUM":
        return <span className="badge badge-blue">Moderate</span>;
      default:
        return <span className="badge" style={{ background: 'var(--bg-card-secondary)', color: 'var(--text-muted)', border: '1px solid var(--border-color)' }}>Info</span>;
    }
  };

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header Banner */}
      <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1.25rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.25rem' }}>🔍</span>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>Why Is My Image Fat?</h2>
            <span className="badge badge-green">
              Beginner-Friendly Diagnosis
            </span>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem', margin: 0 }}>
            Layer-by-layer root cause breakdown of compilers, dev dependencies, and context leaks.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', background: 'var(--bg-card-secondary)', padding: '0.6rem 1rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)', fontWeight: 600 }}>Recoverable Fat</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 900, color: 'var(--accent-red)' }}>~{report.total_bloat_mb.toFixed(0)} MB</div>
          </div>
          <div style={{ height: '30px', width: '1px', background: 'var(--border-color)' }} />
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)', fontWeight: 600 }}>Potential Shrink</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 900, color: 'var(--accent-green)' }}>-{report.potential_reduction_pct.toFixed(0)}%</div>
          </div>
        </div>
      </div>

      {/* Findings Grid */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {report.findings.map(finding => {
          const isExpanded = selectedFinding === finding.id;
          return (
            <div
              key={finding.id}
              style={{
                borderRadius: '10px',
                border: isExpanded ? '1px solid var(--accent-green)' : '1px solid var(--border-color)',
                background: isExpanded ? 'var(--bg-card-hover)' : 'var(--bg-card-secondary)',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
              onClick={() => setSelectedFinding(isExpanded ? null : finding.id)}
            >
              <div style={{ padding: '0.85rem 1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', minWidth: 0 }}>
                  <div style={{ padding: '0.45rem', background: 'var(--bg-card)', borderRadius: '8px', display: 'flex', alignItems: 'center', flexShrink: 0, border: '1px solid var(--border-color)' }}>
                    {getCategoryIcon(finding.category)}
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <h4 style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-main)', margin: 0 }}>{finding.title}</h4>
                      {getSeverityBadge(finding.severity)}
                    </div>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '0.15rem 0 0 0', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {finding.explanation}
                    </p>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexShrink: 0 }}>
                  {finding.wasted_mb > 0 && (
                    <span className="badge badge-red">
                      +{finding.wasted_mb.toFixed(0)} MB
                    </span>
                  )}
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'monospace' }}>
                    {isExpanded ? "▲" : "▼"}
                  </span>
                </div>
              </div>

              {isExpanded && (
                <div style={{ padding: '0 1rem 1rem 1rem', borderTop: '1px solid var(--border-color)', paddingTop: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.8rem' }}>
                  <div>
                    <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>Why it happens: </span>
                    <span style={{ color: 'var(--text-muted)' }}>{finding.explanation}</span>
                  </div>
                  <div style={{ padding: '0.75rem', background: 'var(--accent-green-glow)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', color: 'var(--text-main)', display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                    <CheckCircle size={16} color="var(--accent-green)" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <div>
                      <span style={{ fontWeight: 600, color: 'var(--accent-green)' }}>How Rover-Slim fixes it: </span>
                      <span>{finding.remediation}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* 1-Click Action Footer */}
      <div style={{ paddingTop: '0.5rem', display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', borderTop: '1px solid var(--border-color)', flexWrap: 'wrap' }}>
        {/* Micro-Prompt */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <span>Helpful diagnosis?</span>
          {!helpfulFeedbackGiven ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <button
                onClick={() => {
                  setHelpfulFeedbackGiven(true);
                  onOpenFeedback("bloat_explainer_helpful");
                }}
                className="btn btn-secondary"
                style={{ padding: '0.25rem 0.5rem' }}
                title="Yes, helpful!"
              >
                <ThumbsUp size={12} />
              </button>
              <button
                onClick={() => {
                  onOpenFeedback("bloat_explainer_idea");
                }}
                className="btn btn-secondary"
                style={{ padding: '0.25rem 0.5rem' }}
                title="Have an idea"
              >
                <Lightbulb size={12} />
              </button>
            </div>
          ) : (
            <span style={{ color: 'var(--accent-green)', fontWeight: 600 }}>Thanks for the feedback!</span>
          )}
        </div>

        {/* 1-Click Auto-Slim Button */}
        <button
          onClick={onApplyOptimization}
          disabled={isOptimizing}
          className="btn btn-success"
          style={{ padding: '0.6rem 1.25rem', fontSize: '0.8rem' }}
        >
          <Sparkles size={14} />
          <span>{isOptimizing ? "Synthesizing Slim Build..." : "1-Click Auto-Slim Fix"}</span>
          <ArrowRight size={14} />
        </button>
      </div>
    </div>
  );
};
