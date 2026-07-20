import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { getForecast } from '../api'

type Alert = { category: string; average_spend: number; budget: number; pct_used: number }
type ForecastData = {
  month_year: string
  rolling_averages: Record<string, number>
  budget_limits: Record<string, number>
  over_budget_alerts: Alert[]
  narrative: string
}

export default function Budget() {
  const [data, setData] = useState<ForecastData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getForecast().then(r => setData(r.data)).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-gray-400 py-16 text-center animate-pulse">Loading forecast…</div>
  if (!data) return <div className="text-gray-400 py-16 text-center">No forecast data</div>

  const chartData = Object.entries(data.rolling_averages).map(([name, avg]) => ({
    name,
    avg: Math.round(avg),
    budget: Math.round(data.budget_limits[name] ?? 0),
  })).sort((a, b) => b.avg - a.avg).slice(0, 10)

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Budget Forecast</h1>

      {data.narrative && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-blue-900 text-sm">
          {data.narrative}
        </div>
      )}

      {data.over_budget_alerts.length > 0 && (
        <div>
          <h2 className="font-semibold mb-3 text-red-600">⚠️ Over-Budget Alerts</h2>
          <div className="space-y-2">
            {data.over_budget_alerts.map((a, i) => (
              <div key={i} className="bg-red-50 border border-red-200 rounded-xl p-4 flex justify-between items-center">
                <div>
                  <p className="font-medium text-red-800">{a.category}</p>
                  <p className="text-xs text-red-600">${a.average_spend}/mo avg · ${a.budget} budget</p>
                </div>
                <div className="text-right">
                  <p className="text-red-700 font-bold text-lg">{a.pct_used}%</p>
                  <p className="text-xs text-red-500">of budget</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl p-5 shadow-sm border">
        <h2 className="font-semibold mb-4">Spend vs Budget (3-month avg)</h2>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={chartData}>
              <XAxis dataKey="name" tick={{ fontSize: 11 }} angle={-30} textAnchor="end" height={60} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => `$${v}`} />
              <Legend />
              <Bar dataKey="avg" name="Avg Spend" fill="#6366F1" radius={[4, 4, 0, 0]} />
              <Bar dataKey="budget" name="Budget" fill="#10B981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-gray-400 text-center py-12 text-sm">No spending data available yet</p>
        )}
      </div>
    </div>
  )
}
