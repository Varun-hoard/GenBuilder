import { Code, Copy, Check } from 'lucide-react'
import { useState } from 'react'

export default function ResultViewer({ result }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    const jsonString = JSON.stringify(result.parameters, null, 2)
    navigator.clipboard.writeText(jsonString)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const formatValue = (value) => {
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2)
    }
    return String(value)
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden">
      <div className="p-6 border-b border-slate-200 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Generated Parameters</h2>
          <p className="text-sm text-slate-600 mt-1">{result.projectName}</p>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-2 px-4 py-2 bg-primary-50 text-primary-600 rounded-lg hover:bg-primary-100 transition-colors font-medium text-sm"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4" />
              Copied!
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              Copy JSON
            </>
          )}
        </button>
      </div>

      <div className="p-6 max-h-96 overflow-y-auto">
        <div className="bg-slate-900 rounded-lg p-4 font-mono text-sm text-slate-100 overflow-x-auto">
          <pre>{JSON.stringify(result.parameters, null, 2)}</pre>
        </div>

        {/* Parameters Summary */}
        {result.parameters && Object.keys(result.parameters).length > 0 && (
          <div className="mt-6">
            <h3 className="font-semibold text-slate-900 mb-4">Parameter Summary</h3>
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(result.parameters).slice(0, 6).map(([key, value]) => (
                <div key={key} className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <p className="text-xs text-slate-600 font-medium uppercase tracking-wide">{key}</p>
                  <p className="text-sm font-semibold text-slate-900 mt-1 truncate">
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
