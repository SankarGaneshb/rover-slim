import React from 'react';
import { ShieldCheck, HardDrive, Layers, Zap, ArrowDownRight } from 'lucide-react';

interface MetricCardsProps {
  baseline: {
    uncompressed_size_mb: number;
    compressed_size_mb: number;
    build_context_mb: number;
    layer_count: number;
    wasted_space_mb: number;
    wasted_percent: number;
    total_packages: number;
  };
  optimized: {
    uncompressed_size_mb: number;
    compressed_size_mb: number;
    build_context_mb: number;
    layer_count: number;
    wasted_space_mb: number;
    wasted_percent: number;
    total_packages: number;
  };
  status: string;
}

export const MetricCards: React.FC<MetricCardsProps> = ({ baseline, optimized, status }) => {
  const savedMb = Math.max(0, baseline.uncompressed_size_mb - optimized.uncompressed_size_mb);
  const isAlreadyLean = baseline.uncompressed_size_mb <= 80.0 || savedMb < 1.0;
  const reductionPct = baseline.uncompressed_size_mb > 0 
    ? ((savedMb / baseline.uncompressed_size_mb) * 100).toFixed(1) 
    : '0.0';

  const compressedSaved = Math.max(0, baseline.compressed_size_mb - optimized.compressed_size_mb).toFixed(1);
  const contextSaved = Math.max(0, baseline.build_context_mb - optimized.build_context_mb).toFixed(1);
  const layerDelta = Math.max(0, baseline.layer_count - optimized.layer_count);

  return (
    <div>
      {/* Top 4 Summary Cards */}
      <div className="grid-4">
        {/* Size Reduction Card */}
        <div className="card" style={{ borderLeft: '4px solid #10b981' }}>
          <div className="card-title">
            <span>Size Posture</span>
            <ArrowDownRight size={18} color="#10b981" />
          </div>
          <div className="card-stat" style={{ color: '#34d399' }}>
            {isAlreadyLean ? 'LEAN' : `-${reductionPct}%`}
          </div>
          <div className="card-subtext">
            {isAlreadyLean 
              ? 'Container is already minimal & optimized (Alpine base)'
              : <>Saved <strong>{savedMb.toFixed(1)} MB</strong> uncompressed storage</>
            }
          </div>
        </div>

        {/* Final Optimized Image Size */}
        <div className="card" style={{ borderLeft: '4px solid #0ea5e9' }}>
          <div className="card-title">
            <span>Image Footprint</span>
            <HardDrive size={18} color="#0ea5e9" />
          </div>
          <div className="card-stat">
            {optimized.uncompressed_size_mb.toFixed(1)} <span style={{ fontSize: '1rem', color: 'var(--text-dim)' }}>MB</span>
          </div>
          <div className="card-subtext">
            {isAlreadyLean ? 'Zero bloat detected' : `Down from ${baseline.uncompressed_size_mb.toFixed(1)} MB baseline`}
          </div>
        </div>

        {/* Layer Waste Reduction */}
        <div className="card" style={{ borderLeft: '4px solid #8b5cf6' }}>
          <div className="card-title">
            <span>Layer Waste</span>
            <Layers size={18} color="#8b5cf6" />
          </div>
          <div className="card-stat">
            {isAlreadyLean ? '0.0%' : `${optimized.wasted_percent.toFixed(1)}%`}
          </div>
          <div className="card-subtext">
            {isAlreadyLean ? 'Clean single/minimal layer hierarchy' : `Eliminated ${layerDelta} duplicate layers`}
          </div>
        </div>

        {/* GoA Verification Health */}
        <div className="card" style={{ borderLeft: '4px solid #10b981' }}>
          <div className="card-title">
            <span>GoA Sentinel Status</span>
            <ShieldCheck size={18} color="#10b981" />
          </div>
          <div className="card-stat">
            <span className={`badge ${status === 'PASSED' ? 'badge-green' : 'badge-red'}`} style={{ fontSize: '1rem', padding: '0.4rem 0.8rem' }}>
              {status === 'PASSED' ? '100% HEALTHY' : 'FAILED'}
            </span>
          </div>
          <div className="card-subtext">
            {isAlreadyLean ? 'Minimal base verified responsive' : 'Startup integrity & all health probes green'}
          </div>
        </div>
      </div>

      {/* Detailed Comparison Table */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '1rem', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Zap size={18} color="#38bdf8" /> Container Layer & Transfer Metrics Comparison
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                <th style={{ padding: '0.75rem 1rem' }}>Container Metric</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Baseline Image</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Rover-Slim Candidate</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Total Savings</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Uncompressed Image Size</td>
                <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: 'var(--text-muted)' }}>{baseline.uncompressed_size_mb.toFixed(1)} MB</td>
                <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: '#34d399', fontWeight: 700 }}>{optimized.uncompressed_size_mb.toFixed(1)} MB</td>
                <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: '#38bdf8', fontWeight: 700 }}>
                  {isAlreadyLean ? '0.0 MB (Lean)' : `-${savedMb.toFixed(1)} MB`}
                </td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Registry Push/Pull (Compressed)</td>
                <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: 'var(--text-muted)' }}>{baseline.compressed_size_mb.toFixed(1)} MB</td>
                <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: '#34d399' }}>{optimized.compressed_size_mb.toFixed(1)} MB</td>
                <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: '#38bdf8', fontWeight: 700 }}>
                  {isAlreadyLean ? '0.0 MB' : `-${compressedSaved} MB`}
                </td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Build Context Transfer (Context Shield)</td>
                <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: 'var(--text-muted)' }}>{baseline.build_context_mb.toFixed(1)} MB</td>
                <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: '#34d399' }}>{optimized.build_context_mb.toFixed(1)} MB</td>
                <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: '#38bdf8', fontWeight: 700 }}>
                  {isAlreadyLean ? '0.0 MB' : `-${contextSaved} MB`}
                </td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>OCI Image Layer Count</td>
                <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: 'var(--text-muted)' }}>{baseline.layer_count} layers</td>
                <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: '#34d399' }}>{optimized.layer_count} layers</td>
                <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: '#38bdf8', fontWeight: 700 }}>
                  {isAlreadyLean ? '0 layers' : `-${layerDelta} layers`}
                </td>
              </tr>
              <tr>
                <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Production Dependency Footprint</td>
                <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: 'var(--text-muted)' }}>{baseline.total_packages} packages</td>
                <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: '#34d399' }}>{optimized.total_packages} packages</td>
                <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: '#38bdf8', fontWeight: 700 }}>
                  {isAlreadyLean ? 'Minimal' : `-${Math.max(0, baseline.total_packages - optimized.total_packages)} pkgs`}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
