import { Copy, Check } from 'lucide-react'
import { useState } from 'react'

export default function ResultViewer({ result }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    const jsonString = JSON.stringify(result.parameters, null, 2)
    navigator.clipboard.writeText(jsonString)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Syntax highlighting for JSON
  const syntaxHighlight = (json) => {
    if (typeof json != 'string') {
      json = JSON.stringify(json, undefined, 2);
    }
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
      let cls = 'json-number';
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = 'json-key';
        } else {
          cls = 'json-string';
        }
      } else if (/true|false/.test(match)) {
        cls = 'json-boolean';
      } else if (/null/.test(match)) {
        cls = 'json-null';
      }
      return '<span class="' + cls + '">' + match + '</span>';
    });
  }

  return (
    <div className="glass-panel">
      <div className="results-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 className="form-title" style={{ marginBottom: '0.25rem' }}>Generated Parameters</h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{result.projectName}</p>
        </div>
        <button
          onClick={handleCopy}
          className="btn-primary"
          style={{ width: 'auto', padding: '0.5rem 1rem', fontSize: '0.875rem' }}
        >
          {copied ? (
            <>
              <Check size={16} />
              Copied!
            </>
          ) : (
            <>
              <Copy size={16} />
              Copy JSON
            </>
          )}
        </button>
      </div>

      <div style={{ padding: '1.5rem', maxHeight: '32rem', overflowY: 'auto' }}>
        <div className="json-viewer" dangerouslySetInnerHTML={{ __html: `<pre>${syntaxHighlight(result.parameters)}</pre>` }} />

        {/* Parameters Summary */}
        {result.parameters && Object.keys(result.parameters).length > 0 && (
          <div style={{ marginTop: '1.5rem' }}>
            <h3 style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '1rem' }}>Parameter Summary</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              {Object.entries(result.parameters).slice(0, 6).map(([key, value]) => (
                <div key={key} style={{ padding: '0.75rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    {key}
                  </p>
                  <p style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '0.25rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
