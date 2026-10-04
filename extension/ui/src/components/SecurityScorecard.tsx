import React from 'react';
import { ShieldCheck, CheckCircle2, XCircle, AlertTriangle, FileCode2, Lock, UserCheck } from 'lucide-react';

export interface SecurityCheck {
  id: string;
  name: string;
  status: string; // PASSED, FAILED, WARNING
  standard: string;
  description: string;
  remediation: string;
}

export interface SecurityScorecardReport {
  hardening_score: number;
  grade: string;
  is_non_root: boolean;
  user_uid: number;
  has_zero_compilers: boolean;
  sbom_generated: boolean;
  checks: SecurityCheck[];
}

interface SecurityScorecardProps {
  scorecard: SecurityScorecardReport | null;
  onOpenFeedback: (context: string) => void;
}

export const SecurityScorecard: React.FC<SecurityScorecardProps> = ({
  scorecard,
  onOpenFeedback
}) => {
  if (!scorecard) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
        <ShieldCheck size={36} color="var(--text-dim)" style={{ margin: '0 auto 0.5rem auto' }} />
        <p style={{ fontSize: '0.875rem' }}>Run an audit to generate the CIS Docker Benchmark Security Scorecard.</p>
      </div>
    );
  }

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1.25rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.25rem' }}>🛡️</span>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>CIS Benchmark Security Scorecard</h2>
            <span className="badge badge-green">
              CIS 4.1 & Supply Chain
            </span>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '0.25rem 0 0 0' }}>
            Audits unprivileged user enforcement, attack surface reduction, and compiler elimination.
          </p>
        </div>

        {/* Grade & Score Pill */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', background: 'var(--bg-card-secondary)', padding: '0.6rem 1rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)', fontWeight: 600 }}>Security Grade</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 900, color: 'var(--accent-green)' }}>{scorecard.grade}</div>
          </div>
          <div style={{ height: '30px', width: '1px', background: 'var(--border-color)' }} />
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)', fontWeight: 600 }}>Hardening Score</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 900, color: 'var(--text-main)' }}>{scorecard.hardening_score} <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: 400 }}>/ 100</span></div>
          </div>
        </div>
      </div>

      {/* Key Security Pillars */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
        {/* Non-Root */}
        <div style={{ background: 'var(--bg-card-secondary)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ padding: '0.5rem', borderRadius: '8px', background: scorecard.is_non_root ? 'var(--accent-green-glow)' : 'rgba(239, 68, 68, 0.15)', color: scorecard.is_non_root ? 'var(--accent-green)' : 'var(--accent-red)', display: 'flex' }}>
            <UserCheck size={18} />
          </div>
          <div>
            <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', fontWeight: 700, color: 'var(--text-muted)' }}>Unprivileged User</div>
            <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--text-main)' }}>
              {scorecard.is_non_root ? `appuser (UID ${scorecard.user_uid})` : "Root (UID 0 - Risk)"}
            </div>
          </div>
        </div>

        {/* Zero Compilers */}
        <div style={{ background: 'var(--bg-card-secondary)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ padding: '0.5rem', borderRadius: '8px', background: scorecard.has_zero_compilers ? 'var(--accent-green-glow)' : 'rgba(245, 158, 11, 0.15)', color: scorecard.has_zero_compilers ? 'var(--accent-green)' : 'var(--accent-orange)', display: 'flex' }}>
            <Lock size={18} />
          </div>
          <div>
            <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', fontWeight: 700, color: 'var(--text-muted)' }}>Compiler Removal</div>
            <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--text-main)' }}>
              {scorecard.has_zero_compilers ? "Zero Compilers in Prod" : "Compilers Present in Prod"}
            </div>
          </div>
        </div>

        {/* SBOM */}
        <div style={{ background: 'var(--bg-card-secondary)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ padding: '0.5rem', borderRadius: '8px', background: scorecard.sbom_generated ? 'var(--accent-blue-glow)' : 'rgba(14, 165, 233, 0.1)', color: 'var(--accent-blue)', display: 'flex' }}>
            <FileCode2 size={18} />
          </div>
          <div>
            <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', fontWeight: 700, color: 'var(--text-muted)' }}>Supply Chain SBOM</div>
            <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--text-main)' }}>
              {scorecard.sbom_generated ? "SPDX / CycloneDX Ready" : "Auto-Generated on Build"}
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Check List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <h4 style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', margin: 0 }}>Compliance Rules Breakdown</h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {scorecard.checks.map(check => (
            <div
              key={check.id}
              style={{
                background: 'var(--bg-card-secondary)',
                border: '1px solid var(--border-color)',
                borderRadius: '10px',
                padding: '0.85rem',
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
                gap: '0.75rem',
                fontSize: '0.8rem',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                <div style={{ marginTop: '2px', flexShrink: 0 }}>
                  {check.status === "PASSED" ? (
                    <CheckCircle2 size={16} color="var(--accent-green)" />
                  ) : check.status === "WARNING" ? (
                    <AlertTriangle size={16} color="var(--accent-orange)" />
                  ) : (
                    <XCircle size={16} color="var(--accent-red)" />
                  )}
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{check.name}</span>
                    <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', background: 'var(--bg-card)', padding: '0.1rem 0.4rem', borderRadius: '4px', border: '1px solid var(--border-color)' }}>
                      {check.standard}
                    </span>
                  </div>
                  <p style={{ color: 'var(--text-muted)', margin: '0.25rem 0 0 0' }}>{check.description}</p>
                  {check.status !== "PASSED" && (
                    <p style={{ color: 'var(--accent-green)', margin: '0.25rem 0 0 0', fontWeight: 500 }}>Fix: {check.remediation}</p>
                  )}
                </div>
              </div>

              <span className={`badge ${check.status === 'PASSED' ? 'badge-green' : 'badge-red'}`} style={{ flexShrink: 0 }}>
                {check.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border-color)', fontSize: '0.75rem', color: 'var(--text-dim)', flexWrap: 'wrap' }}>
        <span>Verified against CIS Docker Benchmark v1.6.0 & NIST SP 800-190.</span>
        <button
          onClick={() => onOpenFeedback("security_scorecard")}
          style={{ color: 'var(--accent-blue)', background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '0.75rem', fontWeight: 500 }}
        >
          Share Security Feedback
        </button>
      </div>
    </div>
  );
};
