import React, { useState } from 'react';
import { Package, ArrowLeftRight, CheckCircle2, ShieldAlert, Search, Sparkles } from 'lucide-react';

export interface PrunedDependency {
  package: string;
  action: string;
  reason: string;
  estimated_size_mb: number;
}

interface DependencyMatrixProps {
  initialProd: string[];
  initialDev: string[];
  prunedList: PrunedDependency[];
  onClassificationChange: (prod: string[], dev: string[]) => void;
}

export const DependencyMatrix: React.FC<DependencyMatrixProps> = ({
  initialProd,
  initialDev,
  prunedList,
  onClassificationChange,
}) => {
  const [prodList, setProdList] = useState<string[]>(initialProd);
  const [devList, setDevList] = useState<string[]>(initialDev);
  const [searchQuery, setSearchQuery] = useState('');

  const moveToDev = (pkg: string) => {
    const nextProd = prodList.filter(p => p !== pkg);
    const nextDev = [...devList, pkg];
    setProdList(nextProd);
    setDevList(nextDev);
    onClassificationChange(nextProd, nextDev);
  };

  const moveToProd = (pkg: string) => {
    const nextDev = devList.filter(p => p !== pkg);
    const nextProd = [...prodList, pkg];
    setProdList(nextProd);
    setDevList(nextDev);
    onClassificationChange(nextProd, nextDev);
  };

  const getPackageMeta = (pkg: string) => {
    const found = prunedList.find(p => p.package === pkg || pkg.startsWith(p.package.split('==')[0]));
    return found || {
      reason: 'Detected in Python AST imports',
      estimated_size_mb: 18.5,
    };
  };

  const totalDevSavingsMb = devList.reduce((acc, p) => acc + (getPackageMeta(p).estimated_size_mb || 15.0), 0);

  const filterList = (list: string[]) =>
    list.filter(p => p.toLowerCase().includes(searchQuery.toLowerCase()));

  return (
    <div>
      {/* Search & Live Savings Bar */}
      <div className="action-bar" style={{ justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flex: 1, maxWidth: '400px' }}>
          <Search size={18} color="var(--text-muted)" />
          <input
            type="text"
            className="input-field"
            placeholder="Search dependencies..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(16, 185, 129, 0.1)', padding: '0.4rem 0.8rem', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
            <Sparkles size={16} color="#34d399" />
            <span style={{ fontSize: '0.85rem', color: '#34d399', fontWeight: 600 }}>
              Live Pruned Savings: ~{totalDevSavingsMb.toFixed(1)} MB
            </span>
          </div>
        </div>
      </div>

      {/* Two Column Workbench */}
      <div className="grid-2">
        {/* Production Column */}
        <div className="card" style={{ borderTop: '4px solid #10b981' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle2 size={18} color="#10b981" /> Production Runtime ({prodList.length})
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                Included in minimal container image (requirements-prod.txt)
              </p>
            </div>
            <span className="badge badge-green">Runtime Lean</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', maxHeight: '420px', overflowY: 'auto', paddingRight: '0.3rem' }}>
            {filterList(prodList).length === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
                No production packages matching search.
              </div>
            ) : (
              filterList(prodList).map(pkg => {
                const meta = getPackageMeta(pkg);
                return (
                  <div
                    key={pkg}
                    style={{
                      background: 'var(--bg-card-secondary)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '8px',
                      padding: '0.75rem 1rem',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600, color: '#f1f5f9' }}>
                        <Package size={14} color="#38bdf8" />
                        <code>{pkg}</code>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                        {meta.reason}
                      </div>
                    </div>

                    <button
                      className="btn btn-secondary"
                      style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }}
                      onClick={() => moveToDev(pkg)}
                      title="Exclude from production container"
                    >
                      <ArrowLeftRight size={12} /> Move to Dev
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Development / Pruned Column */}
        <div className="card" style={{ borderTop: '4px solid #f59e0b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <ShieldAlert size={18} color="#f59e0b" /> Dev & Tooling Dependencies ({devList.length})
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                Pruned from Docker image; kept in requirements-dev.txt
              </p>
            </div>
            <span className="badge badge-orange">Pruned Bloat</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', maxHeight: '420px', overflowY: 'auto', paddingRight: '0.3rem' }}>
            {filterList(devList).length === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
                No dev packages found.
              </div>
            ) : (
              filterList(devList).map(pkg => {
                const meta = getPackageMeta(pkg);
                return (
                  <div
                    key={pkg}
                    style={{
                      background: 'var(--bg-card-secondary)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '8px',
                      padding: '0.75rem 1rem',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600, color: '#f1f5f9' }}>
                        <Package size={14} color="#f59e0b" />
                        <code>{pkg}</code>
                        <span className="badge badge-green" style={{ fontSize: '0.7rem', padding: '0.1rem 0.4rem' }}>
                          ~{meta.estimated_size_mb} MB
                        </span>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                        {meta.reason}
                      </div>
                    </div>

                    <button
                      className="btn btn-secondary"
                      style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }}
                      onClick={() => moveToProd(pkg)}
                      title="Include in production container"
                    >
                      <ArrowLeftRight size={12} /> Move to Prod
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
