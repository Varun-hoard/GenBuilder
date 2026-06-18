import { useState } from 'react'
import axios from 'axios'
import { Zap, Loader, CheckCircle, AlertCircle, Download, Trash2, Clock, Code } from 'lucide-react'
import ParameterForm from './components/ParameterForm'
import ResultsList from './components/ResultsList'
import ResultViewer from './components/ResultViewer'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const [results, setResults] = useState([])
  const [selectedResult, setSelectedResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [mode, setMode] = useState('heuristic')
  const [stats, setStats] = useState({ total: 0, success: 0, failed: 0 })

  const handleGenerateParameters = async (formData) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await axios.post(
        `${API_URL}/api/generate-parameters?mode=${mode}`,
        {
          description: formData.description,
          project_name: formData.projectName,
          solver_type: formData.solverType || 'default',
        },
        {
          timeout: mode === 'crewai' ? 60000 : 10000,
        }
      )

      const newResult = {
        id: response.data.request_id,
        projectName: formData.projectName,
        timestamp: new Date().toISOString(),
        mode,
        description: formData.description,
        parameters: response.data.parameters,
        status: 'success',
      }

      setResults([newResult, ...results])
      setSelectedResult(newResult)
      setStats(s => ({ ...s, total: s.total + 1, success: s.success + 1 }))
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to generate parameters'
      setError(errorMsg)
      setStats(s => ({ ...s, total: s.total + 1, failed: s.failed + 1 }))
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteResult = (id) => {
    setResults(results.filter(r => r.id !== id))
    if (selectedResult?.id === id) {
      setSelectedResult(null)
    }
  }

  const handleDownloadResult = (result) => {
    const jsonString = JSON.stringify(result.parameters, null, 2)
    const blob = new Blob([jsonString], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${result.projectName}_${result.id}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  return (
    <div>
      {/* Header */}
      <header className="app-header">
        <div className="brand-logo">
          <div className="logo-icon">
            <Zap size={24} color="#fff" />
          </div>
          <div>
            <h1 className="brand-title">GenBuilder</h1>
            <p className="brand-subtitle">LLM-Driven Design Parameter Optimizer</p>
          </div>
        </div>
        <div className="stats-container">
          <p>Total: <span style={{ fontWeight: 600, color: '#f8fafc' }}>{stats.total}</span></p>
          <p className="stats-success">Success: <span style={{ fontWeight: 600 }}>{stats.success}</span></p>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-layout">
        
        {/* Form Section */}
        <div className="form-section">
          <div className="glass-panel" style={{ padding: '2rem' }}>
            <h2 className="form-title">Generate Parameters</h2>
            
            {/* Mode Selector */}
            <div className="form-group">
              <label className="form-label">Processing Mode</label>
              <div className="mode-selector">
                <div 
                  className={`mode-option ${mode === 'heuristic' ? 'active' : ''}`}
                  onClick={() => setMode('heuristic')}
                >
                  <input
                    type="radio"
                    name="mode"
                    value="heuristic"
                    checked={mode === 'heuristic'}
                    onChange={() => setMode('heuristic')}
                    style={{ accentColor: 'var(--accent-cyan)' }}
                  />
                  <div>
                    <p className="mode-title">Heuristic (Fast)</p>
                    <p className="mode-desc">No API key needed • ~10ms</p>
                  </div>
                </div>
                
                <div 
                  className={`mode-option ${mode === 'crewai' ? 'active' : ''}`}
                  onClick={() => setMode('crewai')}
                >
                  <input
                    type="radio"
                    name="mode"
                    value="crewai"
                    checked={mode === 'crewai'}
                    onChange={() => setMode('crewai')}
                    style={{ accentColor: 'var(--accent-cyan)' }}
                  />
                  <div>
                    <p className="mode-title">CrewAI (Smart)</p>
                    <p className="mode-desc">Requires OpenAI API key • ~15-30s</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Form */}
            <ParameterForm 
              onSubmit={handleGenerateParameters}
              loading={loading}
              error={error}
            />
          </div>
        </div>

        {/* Results Section */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          {/* Results List */}
          {results.length > 0 && (
            <div className="glass-panel">
              <div className="results-header">
                <h2 className="form-title" style={{ marginBottom: 0 }}>
                  Recent Results ({results.length})
                </h2>
              </div>
              <div style={{ maxHeight: '24rem', overflowY: 'auto' }}>
                <ResultsList 
                  results={results} 
                  selectedResult={selectedResult} 
                  onSelect={setSelectedResult}
                  onDownload={handleDownloadResult}
                  onDelete={handleDeleteResult}
                />
              </div>
            </div>
          )}

          {/* Selected Result Viewer */}
          {selectedResult && (
            <ResultViewer result={selectedResult} />
          )}

          {/* Empty State */}
          {results.length === 0 && !loading && (
            <div className="glass-panel empty-state">
              <div className="empty-icon">
                <Zap size={32} />
              </div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
                No Results Yet
              </h3>
              <p>Fill out the form and click "Generate Parameters" to get started</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
