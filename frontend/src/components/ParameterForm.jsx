import { useState } from 'react'
import { Loader, AlertCircle } from 'lucide-react'

export default function ParameterForm({ onSubmit, loading, error }) {
  const [formData, setFormData] = useState({
    projectName: '',
    description: '',
    solverType: 'default',
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (formData.projectName.trim() && formData.description.trim()) {
      onSubmit(formData)
      setFormData({ projectName: '', description: '', solverType: 'default' })
    }
  }

  const isValid = formData.projectName.trim() && formData.description.trim()

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div className="error-box">
          <AlertCircle size={20} className="error-icon" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <p className="error-title">Error</p>
            <p className="error-desc">{error}</p>
          </div>
        </div>
      )}

      <div className="form-group">
        <label className="form-label">Project Name *</label>
        <input
          type="text"
          name="projectName"
          value={formData.projectName}
          onChange={handleChange}
          placeholder="e.g., bracket-v1, heatsink-test"
          className="custom-input"
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label className="form-label">Design Description *</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Describe your design constraints: loads, materials, boundary conditions, safety factors, etc."
          rows="6"
          className="custom-input"
          style={{ resize: 'vertical', minHeight: '120px' }}
          disabled={loading}
        />
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
          Be specific about engineering constraints
        </p>
      </div>

      <div className="form-group">
        <label className="form-label">Solver Type</label>
        <select
          name="solverType"
          value={formData.solverType}
          onChange={handleChange}
          className="custom-input"
          disabled={loading}
        >
          <option value="default" style={{ background: '#131b2f' }}>Default</option>
          <option value="topology" style={{ background: '#131b2f' }}>Topology Optimization</option>
          <option value="structural" style={{ background: '#131b2f' }}>Structural Analysis</option>
          <option value="thermal" style={{ background: '#131b2f' }}>Thermal Analysis</option>
        </select>
      </div>

      <button
        type="submit"
        disabled={!isValid || loading}
        className="btn-primary"
      >
        {loading ? (
          <>
            <Loader size={18} className="animate-spin" />
            Processing...
          </>
        ) : (
          'Generate Parameters'
        )}
      </button>

      <div style={{ paddingTop: '1.5rem', marginTop: '1.5rem', borderTop: '1px solid var(--border-glass)' }}>
        <p className="form-label" style={{ marginBottom: '0.75rem' }}>Example Input:</p>
        <p style={{ 
          fontSize: '0.8rem', 
          color: 'var(--text-secondary)', 
          background: 'rgba(0,0,0,0.2)', 
          padding: '1rem', 
          borderRadius: '8px', 
          border: '1px solid var(--border-glass)',
          fontFamily: 'monospace',
          lineHeight: '1.6'
        }}>
          Design a lightweight aluminum bracket that can withstand 500N of tensile load. The part is fixed at two bolt holes on the left face and the load is applied on the right edge. Minimum safety factor of 2.0.
        </p>
      </div>
    </form>
  )
}
