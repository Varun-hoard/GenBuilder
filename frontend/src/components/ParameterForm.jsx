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
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-900">Error</p>
            <p className="text-sm text-red-800 mt-1">{error}</p>
          </div>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Project Name *
        </label>
        <input
          type="text"
          name="projectName"
          value={formData.projectName}
          onChange={handleChange}
          placeholder="e.g., bracket-v1, heatsink-test"
          className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          disabled={loading}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Design Description *
        </label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Describe your design constraints: loads, materials, boundary conditions, safety factors, etc."
          rows="6"
          className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none"
          disabled={loading}
        />
        <p className="mt-1 text-xs text-slate-500">
          Be specific about engineering constraints
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Solver Type
        </label>
        <select
          name="solverType"
          value={formData.solverType}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none bg-white"
          disabled={loading}
        >
          <option value="default">Default</option>
          <option value="topology">Topology Optimization</option>
          <option value="structural">Structural Analysis</option>
          <option value="thermal">Thermal Analysis</option>
        </select>
      </div>

      <button
        type="submit"
        disabled={!isValid || loading}
        className={`w-full py-2 px-4 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
          isValid && !loading
            ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white hover:shadow-lg'
            : 'bg-slate-300 text-slate-500 cursor-not-allowed'
        }`}
      >
        {loading ? (
          <>
            <Loader className="w-4 h-4 animate-spin" />
            Processing...
          </>
        ) : (
          'Generate Parameters'
        )}
      </button>

      <div className="pt-4 border-t border-slate-200">
        <p className="text-xs text-slate-600 mb-3 font-medium">Example Input:</p>
        <p className="text-xs text-slate-600 bg-slate-50 p-3 rounded border border-slate-200 font-mono leading-relaxed">
          Design a lightweight aluminum bracket that can withstand 500N of tensile load. The part is fixed at two bolt holes on the left face and the load is applied on the right edge. Minimum safety factor of 2.0.
        </p>
      </div>
    </form>
  )
}
