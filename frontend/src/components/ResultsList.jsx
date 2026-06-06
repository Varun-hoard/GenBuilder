export default function ResultsList({ results, selectedId, onSelect }) {
  return (
    <div>
      {results.length === 0 ? (
        <div className="text-center py-12 text-slate-600">
          <p>No results yet</p>
        </div>
      ) : (
        <div className="space-y-2">
          {results.map(result => (
            <div
              key={result.id}
              onClick={() => onSelect(result)}
              className={`p-4 rounded-lg cursor-pointer transition-all ${
                selectedId === result.id
                  ? 'bg-primary-100 border-2 border-primary-500'
                  : 'bg-slate-50 border-2 border-slate-200 hover:border-slate-300'
              }`}
            >
              <h3 className="font-semibold text-slate-900">{result.projectName}</h3>
              <p className="text-sm text-slate-600 mt-1 line-clamp-2">{result.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
