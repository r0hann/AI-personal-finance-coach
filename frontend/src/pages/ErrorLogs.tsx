import { useEffect, useState } from 'react'
import { listErrorLogs, clearErrorLogs } from '../api'

interface ErrorLog {
  id: string
  timestamp: string
  source: string
  error_type: string
  message: string
  details: Record<string, unknown> | null
}

const SOURCE_COLORS: Record<string, string> = {
  csv_import: 'bg-yellow-100 text-yellow-800',
  csv_import_db: 'bg-orange-100 text-orange-800',
  ai_provider: 'bg-red-100 text-red-800',
}

function formatLog(log: ErrorLog): string {
  return [
    `[${new Date(log.timestamp).toLocaleString()}] ${log.source} — ${log.error_type}`,
    `Message: ${log.message}`,
    log.details ? `Details:\n${JSON.stringify(log.details, null, 2)}` : '',
  ].filter(Boolean).join('\n')
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation()
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <button
      onClick={handleCopy}
      className="px-2 py-1 text-xs rounded bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
    >
      {copied ? 'Copied!' : 'Copy'}
    </button>
  )
}

export function ErrorLogs() {
  const [logs, setLogs] = useState<ErrorLog[]>([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<string | null>(null)

  const fetchLogs = () => {
    setLoading(true)
    listErrorLogs()
      .then(r => setLogs(r.data))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchLogs() }, [])

  const handleClear = () => { clearErrorLogs().then(fetchLogs) }

  const handleCopyAll = () => {
    navigator.clipboard.writeText(logs.map(formatLog).join('\n\n---\n\n'))
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Error Logs</h1>
        <div className="flex gap-3">
          <button onClick={fetchLogs} className="px-4 py-2 text-sm bg-gray-100 rounded-lg hover:bg-gray-200">
            Refresh
          </button>
          <button onClick={handleCopyAll} className="px-4 py-2 text-sm bg-gray-100 rounded-lg hover:bg-gray-200" disabled={logs.length === 0}>
            Copy All
          </button>
          <button onClick={handleClear} className="px-4 py-2 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200">
            Clear All
          </button>
        </div>
      </div>

      {loading && <p className="text-gray-500">Loading...</p>}

      {!loading && logs.length === 0 && (
        <div className="text-center py-16 text-gray-400">No errors logged.</div>
      )}

      <div className="space-y-3">
        {logs.map(log => (
          <div key={log.id} className="border border-gray-200 rounded-lg overflow-hidden">
            <button
              className="w-full text-left px-4 py-3 flex items-start gap-4 hover:bg-gray-50"
              onClick={() => setExpanded(expanded === log.id ? null : log.id)}
            >
              <span className={`mt-0.5 px-2 py-0.5 rounded text-xs font-medium shrink-0 ${SOURCE_COLORS[log.source] ?? 'bg-gray-100 text-gray-700'}`}>
                {log.source}
              </span>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-800 truncate">{log.error_type}: {log.message}</p>
                <p className="text-xs text-gray-400 mt-0.5">{new Date(log.timestamp).toLocaleString()}</p>
              </div>
              <span className="text-gray-400 text-sm">{expanded === log.id ? '▲' : '▼'}</span>
            </button>

            {expanded === log.id && (
              <div className="bg-gray-900">
                <div className="flex justify-end gap-2 px-4 pt-3">
                  <CopyButton text={formatLog(log)} />
                </div>
                <pre className="text-green-300 text-xs p-4 overflow-x-auto">
                  {JSON.stringify(log.details, null, 2) ?? 'No details'}
                </pre>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
