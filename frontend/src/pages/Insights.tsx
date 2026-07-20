import { useEffect, useState } from 'react'
import { monthlyInsights } from '../api'

type Insight = { title: string; description: string; type: 'warning' | 'info' | 'success' }
type Suggestion = { category: string; suggestion: string; estimated_savings: number }
type InsightsData = { summary: string; insights: Insight[]; savings_suggestions: Suggestion[] }

const TYPE_STYLES = {
  warning: 'border-amber-300 bg-amber-50 text-amber-800',
  info: 'border-blue-300 bg-blue-50 text-blue-800',
  success: 'border-green-300 bg-green-50 text-green-800',
}
const TYPE_ICON = { warning: '⚠️', info: 'ℹ️', success: '✅' }

export default function Insights() {
  const [data, setData] = useState<InsightsData | null>(null)
  const [loading, setLoading] = useState(true)
  const month = new Date().toISOString().slice(0, 7)

  useEffect(() => {
    monthlyInsights(month)
      .then(r => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [month])

  if (loading) return <div className="text-gray-400 py-16 text-center animate-pulse">Generating insights…</div>
  if (!data) return <div className="text-gray-400 py-16 text-center">No insights available</div>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Monthly Insights <span className="text-gray-400 text-base font-normal">{month}</span></h1>

      <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-5">
        <p className="text-indigo-900 font-medium">{data.summary}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {data.insights.map((ins, i) => (
          <div key={i} className={`border rounded-xl p-4 ${TYPE_STYLES[ins.type]}`}>
            <p className="font-semibold">{TYPE_ICON[ins.type]} {ins.title}</p>
            <p className="text-sm mt-1">{ins.description}</p>
          </div>
        ))}
      </div>

      {data.savings_suggestions.length > 0 && (
        <div>
          <h2 className="font-semibold text-lg mb-3">💰 Savings Opportunities</h2>
          <div className="space-y-3">
            {data.savings_suggestions.map((s, i) => (
              <div key={i} className="bg-white border rounded-xl p-4 flex justify-between items-start shadow-sm">
                <div>
                  <p className="font-medium text-sm">{s.category}</p>
                  <p className="text-gray-600 text-sm mt-0.5">{s.suggestion}</p>
                </div>
                {s.estimated_savings > 0 && (
                  <span className="text-green-600 font-semibold text-sm whitespace-nowrap ml-4">
                    Save ${s.estimated_savings.toFixed(0)}/mo
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
