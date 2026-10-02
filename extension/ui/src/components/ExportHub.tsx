import React, { useState } from 'react';
import { Copy, Check, FileText, Code2, Download } from 'lucide-react';

interface ExportHubProps {
  onFetchExport: (format: string) => Promise<string>;
}

export const ExportHub: React.FC<ExportHubProps> = ({ onFetchExport }) => {
  const [activeFormat, setActiveFormat] = useState<'markdown' | 'github_action' | 'json'>('markdown');
  const [content, setContent] = useState<string>('');
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);

  const loadFormat = async (fmt: 'markdown' | 'github_action' | 'json') => {
    setActiveFormat(fmt);
    setLoading(true);
    try {
      const text = await onFetchExport(fmt);
      setContent(text);
    } catch {
      setContent('# Error loading export content');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    loadFormat('markdown');
  }, []);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const filename =
      activeFormat === 'markdown'
        ? 'rover-slim-summary.md'
        : activeFormat === 'github_action'
        ? 'rover-slim-ci.yml'
        : 'rover-slim-report.json';
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <div className="action-bar" style={{ justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            className={`btn ${activeFormat === 'markdown' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => loadFormat('markdown')}
          >
            <FileText size={16} /> GitHub PR Markdown
          </button>
          <button
            className={`btn ${activeFormat === 'github_action' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => loadFormat('github_action')}
          >
            <Code2 size={16} /> GitHub Action (CI/CD)
          </button>
          <button
            className={`btn ${activeFormat === 'json' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => loadFormat('json')}
          >
            <Code2 size={16} /> Raw Metrics JSON
          </button>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button className="btn btn-secondary" onClick={handleDownload} disabled={loading || !content}>
            <Download size={16} /> Download File
          </button>
          <button className="btn btn-success" onClick={handleCopy} disabled={loading || !content}>
            {copied ? <Check size={16} /> : <Copy size={16} />}
            {copied ? 'Copied to Clipboard!' : 'Copy to Clipboard'}
          </button>
        </div>
      </div>

      <div className="card">
        <div className="card-title">
          <span>
            {activeFormat === 'markdown' && 'GitHub Pull Request Summary (Markdown Preview)'}
            {activeFormat === 'github_action' && 'Automated GitHub Actions CI Workflow (.github/workflows/rover-slim.yml)'}
            {activeFormat === 'json' && 'Machine-Readable Optimization Metrics (.rover-slim/report.json)'}
          </span>
          <span className="badge badge-blue">{activeFormat.toUpperCase()}</span>
        </div>

        <pre className="code-view" style={{ maxHeight: '480px' }}>
          {loading ? 'Generating export payload...' : content}
        </pre>
      </div>
    </div>
  );
};
