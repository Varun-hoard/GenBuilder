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
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-slate-900">GenBuilder</h1>
                <p className="text-sm text-slate-500">LLM-Driven Design Parameter Optimizer</p>
              </div>
            </div>
            <div className="text-right text-sm text-slate-600">
              <p>Total: <span className="font-semibold">{stats.total}</span></p>
              <p className="text-green-600">Success: <span className="font-semibold">{stats.success}</span></p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Form Section */}
          <div className="lg:col-span-1">
            <div className="sticky top-8">
              <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6">
                <h2 className="text-xl font-bold text-slate-900 mb-4">Generate Parameters</h2>
                
                {/* Mode Selector */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-slate-700 mb-3">
                    Processing Mode
                  </label>
                  <div className="space-y-2">
                    <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-slate-50"
                      style={{ borderColor: mode === 'heuristic' ? '#0284c7' : '#e2e8f0' }}>
                      <input
                        type="radio"
                        name="mode"
                        value="heuristic"
                        checked={mode === 'heuristic'}
                        onChange={(e) => setMode(e.target.value)}
                        className="w-4 h-4"
                      />
                      <div>
                        <p className="font-medium text-slate-900">Heuristic (Fast)</p>
                        <p className="text-xs text-slate-500">No API key needed • ~10ms</p>
                      </div>
                    </label>
                    <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-slate-50"
                      style={{ borderColor: mode === 'crewai' ? '#0284c7' : '#e2e8f0' }}>
                      <input
                        type="radio"
                        name="mode"
                        value="crewai"
                        checked={mode === 'crewai'}
                        onChange={(e) => setMode(e.target.value)}
                        className="w-4 h-4"
                      />
                      <div>
                        <p className="font-medium text-slate-900">CrewAI (Smart)</p>
                        <p className="text-xs text-slate-500">Requires OpenAI API key • ~15-30s</p>
                      </div>
                    </label>
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
          </div>

          {/* Results Section */}
          <div className="lg:col-span-2 space-y-6">
            {/* Results List */}
            {results.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden">
                <div className="p-6 border-b border-slate-200">
                  <h2 className="text-xl font-bold text-slate-900">
                    Recent Results ({results.length})
                  </h2>
                </div>
                <div className="divide-y divide-slate-200 max-h-96 overflow-y-auto">
                  {results.map((result) => (
                    <div
                      key={result.id}
                      onClick={() => setSelectedResult(result)}
                      className={`p-4 cursor-pointer transition-colors hover:bg-slate-50 border-l-4 ${
                        selectedResult?.id === result.id
                          ? 'bg-primary-50 border-primary-500'
                          : 'border-transparent'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-slate-900">{result.projectName}</h3>
                          <p className="text-sm text-slate-500 mt-1 line-clamp-2">
                            {result.description}
                          </p>
                          <div className="flex items-center gap-4 mt-2 text-xs text-slate-600">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {new Date(result.timestamp).toLocaleTimeString()}
                            </span>
                            <span className="px-2 py-1 bg-slate-100 rounded text-slate-700 font-medium">
                              {result.mode}
                            </span>
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          </div>
                        </div>
                        <div className="flex gap-2 ml-4">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDownloadResult(result)
                            }}
                            className="p-2 text-slate-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                            title="Download JSON"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDeleteResult(result.id)
                            }}
                            className="p-2 text-slate-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Selected Result Viewer */}
            {selectedResult && (
              <ResultViewer result={selectedResult} />
            )}

            {/* Empty State */}
            {results.length === 0 && !loading && (
              <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-12 text-center">
                <div className="flex justify-center mb-4">
                  <div className="p-3 bg-slate-100 rounded-lg">
                    <Zap className="w-8 h-8 text-slate-400" />
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">No Results Yet</h3>
                <p className="text-slate-600">
                  Fill out the form and click "Generate Parameters" to get started
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
