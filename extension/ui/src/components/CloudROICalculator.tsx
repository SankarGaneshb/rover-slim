import React, { useState } from 'react';
import { DollarSign, TrendingUp, Zap, Clock, Cloud } from 'lucide-react';

interface CloudROICalculatorProps {
  baselineMb: number;
  optimizedMb: number;
  onOpenFeedback: (context: string) => void;
}

export const CloudROICalculator: React.FC<CloudROICalculatorProps> = ({
  baselineMb = 1250,
  optimizedMb = 210,
  onOpenFeedback
}) => {
  const [dailyDeployments, setDailyDeployments] = useState(10);
  const [clusterNodes, setClusterNodes] = useState(8);

  const baseMb = Math.max(1, baselineMb);
  const optMb = Math.max(1, optimizedMb);
  const savedMb = Math.max(0, baseMb - optMb);

  // Bandwidth calculation
  const monthlyPulls = dailyDeployments * 30 * Math.max(1, clusterNodes);
  const monthlyBandwidthSavedGb = (savedMb * monthlyPulls) / 1024.0;

  // Cloud egress rates ($ / GB)
  const AWS_RATE = 0.09;
  const GCP_RATE = 0.085;
  const AZURE_RATE = 0.087;

  const awsMonthlySavings = monthlyBandwidthSavedGb * AWS_RATE;
  const gcpMonthlySavings = monthlyBandwidthSavedGb * GCP_RATE;
  const azureMonthlySavings = monthlyBandwidthSavedGb * AZURE_RATE;

  const annualAvgSavings = ((awsMonthlySavings + gcpMonthlySavings + azureMonthlySavings) / 3) * 12;

  // Cold start estimate
  const coldBaseSec = 1.5 + baseMb / 50.0;
  const coldOptSec = 1.0 + optMb / 65.0;
  const speedupFactor = Math.max(1.1, coldBaseSec / coldOptSec);

  // CI/CD Minutes Saved
  const cicdMinutesSaved = Math.round(dailyDeployments * 30 * (savedMb / 350.0) * 1.5);

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1.25rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.25rem' }}>💰</span>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>Cloud-Agnostic FinOps ROI Calculator</h2>
            <span className="badge badge-green">
              Multi-Cloud Ready
            </span>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '0.25rem 0 0 0' }}>
            Quantify real egress bandwidth cost reduction, faster auto-scaling, and developer CI/CD time saved.
          </p>
        </div>

        <div style={{ background: 'var(--bg-card-secondary)', border: '1px solid var(--border-color)', padding: '0.6rem 1rem', borderRadius: '10px', textAlign: 'right' }}>
          <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', fontWeight: 600, color: 'var(--accent-green)' }}>Estimated Annual Savings</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 900, color: 'var(--accent-green)' }}>
            ${annualAvgSavings.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
            <span style={{ fontSize: '0.75rem', fontWeight: 400, color: 'var(--text-dim)' }}> / yr</span>
          </div>
        </div>
      </div>

      {/* Interactive Controls */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', background: 'var(--bg-card-secondary)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.4rem', fontWeight: 500 }}>
            <span style={{ color: 'var(--text-main)' }}>Daily Deployments & Builds</span>
            <span style={{ color: 'var(--accent-green)', fontWeight: 700 }}>{dailyDeployments} / day</span>
          </div>
          <input
            type="range"
            min="1"
            max="50"
            value={dailyDeployments}
            onChange={e => setDailyDeployments(Number(e.target.value))}
            style={{ width: '100%', cursor: 'pointer', accentColor: 'var(--accent-green)' }}
          />
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.4rem', fontWeight: 500 }}>
            <span style={{ color: 'var(--text-main)' }}>Kubernetes / ECS Worker Nodes</span>
            <span style={{ color: 'var(--accent-blue)', fontWeight: 700 }}>{clusterNodes} nodes</span>
          </div>
          <input
            type="range"
            min="1"
            max="50"
            value={clusterNodes}
            onChange={e => setClusterNodes(Number(e.target.value))}
            style={{ width: '100%', cursor: 'pointer', accentColor: 'var(--accent-blue)' }}
          />
        </div>
      </div>

      {/* Cloud Provider Egress Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
        {/* AWS */}
        <div style={{ background: 'var(--bg-card-secondary)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.8rem' }}>
            <span style={{ fontWeight: 700, color: 'var(--accent-orange)' }}>AWS (ECR / ECS / EKS)</span>
            <Cloud size={16} color="var(--accent-orange)" />
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)' }}>
            ${awsMonthlySavings.toFixed(1)} <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: 400 }}>/ mo</span>
          </div>
          <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0 }}>
            Based on ${(AWS_RATE).toFixed(2)}/GB cross-AZ / Internet egress tariff.
          </p>
        </div>

        {/* GCP */}
        <div style={{ background: 'var(--bg-card-secondary)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.8rem' }}>
            <span style={{ fontWeight: 700, color: 'var(--accent-blue)' }}>Google Cloud (Artifact Reg / GKE)</span>
            <Cloud size={16} color="var(--accent-blue)" />
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)' }}>
            ${gcpMonthlySavings.toFixed(1)} <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: 400 }}>/ mo</span>
          </div>
          <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0 }}>
            Based on ${(GCP_RATE).toFixed(3)}/GB multi-region egress tariff.
          </p>
        </div>

        {/* Azure */}
        <div style={{ background: 'var(--bg-card-secondary)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.8rem' }}>
            <span style={{ fontWeight: 700, color: 'var(--accent-blue)' }}>Microsoft Azure (ACR / AKS)</span>
            <Cloud size={16} color="var(--accent-blue)" />
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)' }}>
            ${azureMonthlySavings.toFixed(1)} <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: 400 }}>/ mo</span>
          </div>
          <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0 }}>
            Based on ${(AZURE_RATE).toFixed(3)}/GB data transfer egress tariff.
          </p>
        </div>
      </div>

      {/* Performance & CI/CD Acceleration Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border-color)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', background: 'var(--bg-card-secondary)', padding: '0.75rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          <div style={{ padding: '0.5rem', background: 'var(--accent-green-glow)', color: 'var(--accent-green)', borderRadius: '8px', display: 'flex' }}>
            <Zap size={18} />
          </div>
          <div>
            <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', fontWeight: 700, color: 'var(--text-muted)' }}>Cold-Start Speedup</div>
            <div style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--accent-green)' }}>{speedupFactor.toFixed(1)}x Faster</div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)' }}>{coldBaseSec.toFixed(1)}s ➔ {coldOptSec.toFixed(1)}s</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', background: 'var(--bg-card-secondary)', padding: '0.75rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          <div style={{ padding: '0.5rem', background: 'var(--accent-blue-glow)', color: 'var(--accent-blue)', borderRadius: '8px', display: 'flex' }}>
            <Clock size={18} />
          </div>
          <div>
            <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', fontWeight: 700, color: 'var(--text-muted)' }}>CI/CD Time Saved</div>
            <div style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--accent-blue)' }}>~{cicdMinutesSaved} mins / mo</div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)' }}>Faster pushes & runner pulls</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', background: 'var(--bg-card-secondary)', padding: '0.75rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          <div style={{ padding: '0.5rem', background: 'rgba(245, 158, 11, 0.15)', color: 'var(--accent-orange)', borderRadius: '8px', display: 'flex' }}>
            <TrendingUp size={18} />
          </div>
          <div>
            <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', fontWeight: 700, color: 'var(--text-muted)' }}>Monthly Bandwidth</div>
            <div style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--accent-orange)' }}>{monthlyBandwidthSavedGb.toFixed(0)} GB Saved</div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)' }}>Across {monthlyPulls.toLocaleString()} total pulls</div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border-color)', fontSize: '0.75rem', color: 'var(--text-dim)', flexWrap: 'wrap' }}>
        <span>Based on standard public cloud egress rates & empirical node pull models.</span>
        <button
          onClick={() => onOpenFeedback("cloud_roi")}
          style={{ color: 'var(--accent-blue)', background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '0.75rem', fontWeight: 500 }}
        >
          Share FinOps Feedback
        </button>
      </div>
    </div>
  );
};
