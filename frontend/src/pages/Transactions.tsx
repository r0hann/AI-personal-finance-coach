import { useEffect, useState, useRef } from 'react'
import { importCSV, listTransactions } from '../api'

export default function Transactions() {
  const [transactions, setTransactions] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)
  const month = new Date().toISOString().slice(0, 7)

  const load = () => {
    listTransactions(month).then(r => setTransactions(r.data)).catch(() => {})
  }

  useEffect(() => { load() }, [])

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    setStatus('')
    try {
      const res = await importCSV(file)
      setStatus(`✅ ${res.data.message}`)
      load()
    } catch (err: any) {
      setStatus(`❌ ${err.response?.data?.detail ?? 'Import failed'}`)
    } finally {
      setLoading(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Transactions</h1>
        <label className="cursor-pointer bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition">
          {loading ? 'Importing…' : '⬆️ Import CSV'}
          <input ref={fileRef} type="file" accept=".csv" className="hidden" onChange={handleUpload} disabled={loading} />
        </label>
      </div>

      {status && <p className="text-sm bg-gray-100 rounded-lg px-4 py-2">{status}</p>}

      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Date</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Description</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Category</th>
              <th className="text-right px-4 py-3 font-medium text-gray-500">Amount</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {transactions.length === 0 ? (
              <tr>
                <td colSpan={4} className="text-center py-12 text-gray-400">
                  No transactions — import a CSV to get started
                </td>
              </tr>
            ) : transactions.map((t: any) => (
              <tr key={t.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-gray-500">{t.date}</td>
                <td className="px-4 py-3 max-w-xs truncate">{t.description}</td>
                <td className="px-4 py-3">
                  {t.categories ? (
                    <span className="inline-flex items-center gap-1 text-xs bg-indigo-50 text-indigo-700 px-2 py-1 rounded-full">
                      {t.categories.icon} {t.categories.name}
                    </span>
                  ) : (
                    <span className="text-gray-400 text-xs">Uncategorized</span>
                  )}
                </td>
                <td className={`px-4 py-3 text-right font-medium ${t.amount < 0 ? 'text-red-500' : 'text-green-500'}`}>
                  {t.amount < 0 ? '-' : '+'}${Math.abs(t.amount).toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
