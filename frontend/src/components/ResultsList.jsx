import { Clock, CheckCircle, Download, Trash2 } from 'lucide-react'

export default function ResultsList({ results, selectedResult, onSelect, onDownload, onDelete }) {
  if (results.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {results.map((result) => (
        <div
          key={result.id}
          onClick={() => onSelect(result)}
          className={`result-item ${selectedResult?.id === result.id ? 'active' : ''}`}
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
            <div style={{ flex: 1 }}>
              <h3 style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{result.projectName}</h3>
              <p style={{ 
                fontSize: '0.875rem', 
                color: 'var(--text-secondary)', 
                marginTop: '0.25rem',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden'
              }}>
                {result.description}
              </p>
              <div className="result-meta">
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Clock size={12} />
                  {new Date(result.timestamp).toLocaleTimeString()}
                </span>
                <span className="badge">{result.mode}</span>
                <CheckCircle size={14} style={{ color: '#10b981' }} />
              </div>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', marginLeft: '1rem' }}>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onDownload(result)
                }}
                className="action-btn"
                title="Download JSON"
              >
                <Download size={18} />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onDelete(result.id)
                }}
                className="action-btn danger"
                title="Delete"
              >
                <Trash2 size={18} />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
