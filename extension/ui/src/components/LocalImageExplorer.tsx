import React, { useState } from 'react';
import { HardDrive, Search, RefreshCw, Zap, Layers, AlertCircle, ArrowRight, CheckCircle2 } from 'lucide-react';

export interface LocalDockerImage {
  id: string;
  tag: string;
  size_mb: number;
  created: string;
}

interface LocalImageExplorerProps {
  images: LocalDockerImage[];
  selectedImage: string;
  onSelectAndAudit: (imageTag: string) => void;
  onRefresh: () => Promise<void>;
  isLoading: boolean;
}

export const LocalImageExplorer: React.FC<LocalImageExplorerProps> = ({
  images,
  selectedImage,
  onSelectAndAudit,
  onRefresh,
  isLoading,
}) => {
  const [search, setSearch] = useState('');

  const filteredImages = images.filter(img =>
    img.tag.toLowerCase().includes(search.toLowerCase()) || img.id.toLowerCase().includes(search.toLowerCase())
  );

  const totalDiskMb = images.reduce((acc, img) => acc + (img.size_mb || 0), 0);

  const getSizeBadge = (sizeMb: number) => {
    if (sizeMb > 1000) {
      return <span className="badge badge-red">{sizeMb >= 1024 ? `${(sizeMb / 1024).toFixed(2)} GB` : `${sizeMb.toFixed(1)} MB`} (High Bloat)</span>;
    } else if (sizeMb > 400) {
      return <span className="badge badge-orange">{sizeMb.toFixed(1)} MB (Slimmable)</span>;
    }
    return <span className="badge badge-green">{sizeMb.toFixed(1)} MB (Lean)</span>;
  };

  return (
    <div>
      {/* Search & Top Action Bar */}
      <div className="action-bar" style={{ justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flex: 1, maxWidth: '450px' }}>
          <Search size={18} color="var(--text-muted)" />
          <input
            type="text"
            className="input-field"
            placeholder="Search local images by repo or tag..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(14, 165, 233, 0.1)', padding: '0.4rem 0.8rem', borderRadius: '8px', border: '1px solid rgba(14, 165, 233, 0.3)' }}>
            <HardDrive size={16} color="#38bdf8" />
            <span style={{ fontSize: '0.85rem', color: '#38bdf8', fontWeight: 600 }}>
              {images.length} Local Images ({totalDiskMb > 1024 ? `${(totalDiskMb / 1024).toFixed(2)} GB` : `${totalDiskMb.toFixed(0)} MB`} Total)
            </span>
          </div>

          <button className="btn btn-secondary" onClick={onRefresh} disabled={isLoading}>
            <RefreshCw size={14} className={isLoading ? 'spin' : ''} />
            Refresh Docker Images
          </button>
        </div>
      </div>

      {/* Images Grid / Table */}
      <div className="card">
        <div className="card-title">
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Layers size={18} color="#0ea5e9" /> Local Docker Desktop Image Library
          </span>
          <span className="badge badge-blue">{filteredImages.length} Discovered</span>
        </div>

        {filteredImages.length === 0 ? (
          <div style={{ padding: '3rem 1rem', textAlign: 'center', color: 'var(--text-dim)' }}>
            <AlertCircle size={32} color="var(--text-dim)" style={{ margin: '0 auto 0.75rem' }} />
            <p style={{ fontSize: '0.95rem', color: 'var(--text-muted)' }}>No local Docker images found matching "{search}".</p>
            <p style={{ fontSize: '0.8rem', marginTop: '0.35rem' }}>Build or pull an image in Docker Desktop, or click Refresh.</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Image Tag / Repository</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Image ID</th>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Image Size</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Created</th>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Optimization Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredImages.map((img) => {
                  const isSelected = selectedImage === img.tag;
                  return (
                    <tr
                      key={img.id + img.tag}
                      style={{
                        borderBottom: '1px solid var(--border-color)',
                        background: isSelected ? 'rgba(14, 165, 233, 0.08)' : 'transparent',
                        transition: 'background 0.2s',
                      }}
                    >
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: '#f8fafc' }}>
                          <HardDrive size={16} color={isSelected ? '#38bdf8' : 'var(--text-dim)'} />
                          <code>{img.tag}</code>
                          {isSelected && <span className="badge badge-blue" style={{ fontSize: '0.65rem' }}>Active</span>}
                        </div>
                      </td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-dim)', fontFamily: 'monospace' }}>
                        {img.id.slice(0, 12)}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>
                        {getSizeBadge(img.size_mb)}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-dim)', fontSize: '0.8rem' }}>
                        {img.created ? new Date(img.created).toLocaleDateString() : 'Local build'}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>
                        <button
                          className={`btn ${isSelected ? 'btn-success' : 'btn-primary'}`}
                          style={{ padding: '0.4rem 0.85rem', fontSize: '0.8rem' }}
                          onClick={() => onSelectAndAudit(img.tag)}
                        >
                          {isSelected ? (
                            <>
                              <CheckCircle2 size={14} /> Selected
                            </>
                          ) : (
                            <>
                              <Zap size={14} /> Audit & Slim <ArrowRight size={14} />
                            </>
                          )}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
