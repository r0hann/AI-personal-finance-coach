import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { monthlySummary, listTransactions } from '../api'

const COLORS = ['#6366F1', '#F59E0B', '#10B981', '#3B82F6', '#EC4899', '#8B5CF6', '#EF4444', '#14B8A6']

export default function Dashboard() {
  const [summary, setSummary] = useState<Record<string, number>>({})
  const [recent, setRecent] = useState<any[]>([])
  const month = new Date().toISOString().slice(0, 7)

  useEffect(() => {
    monthlySummary(month).then(r => setSummary(r.data)).catch(() => {})
    listTransactions(month).then(r => setRecent(r.data.slice(0, 5))).catch(() => {})
  }, [month])

  const chartData = Object.entries(summary)
    .filter(([, v]) => v < 0)
    .map(([name, value]) => ({ name, value: Math.abs(value) }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 8)

  const totalExpenses = chartData.reduce((s, d) => s + d.value, 0)

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard <span className="text-gray-400 text-base font-normal">{month}</span></h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-5 shadow-sm border">
          <p className="text-sm text-gray-500">Total Expenses</p>
          <p className="text-3xl font-bold text-red-500 mt-1">${totalExpenses.toFixed(2)}</p>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border">
          <p className="text-sm text-gray-500">Top Category</p>
          <p className="text-2xl font-bold mt-1">{chartData[0]?.name ?? '—'}</p>
          <p className="text-gray-400 text-sm">${chartData[0]?.value.toFixed(2) ?? '0'}</p>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border">
          <p className="text-sm text-gray-500">Categories Tracked</p>
          <p className="text-3xl font-bold mt-1">{chartData.length}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-5 shadow-sm border">
          <h2 className="font-semibold mb-4">Spending Breakdown</h2>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100}>
                  {chartData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(v: number) => `$${v.toFixed(2)}`} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-center py-16">No data yet — import a CSV to get started</p>
          )}
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border">
          <h2 className="font-semibold mb-4">Recent Transactions</h2>
          {recent.length > 0 ? (
            <ul className="divide-y">
              {recent.map((t: any) => (
                <li key={t.id} className="py-2.5 flex justify-between items-center">
                  <div>
                    <p className="text-sm font-medium truncate max-w-[200px]">{t.description}</p>
                    <p className="text-xs text-gray-400">{t.date} · {t.categories?.name ?? 'Uncategorized'}</p>
                  </div>
                  <span className={`text-sm font-semibold ${t.amount < 0 ? 'text-red-500' : 'text-green-500'}`}>
                    {t.amount < 0 ? '-' : '+'}${Math.abs(t.amount).toFixed(2)}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-400 text-center py-8 text-sm">No transactions this month</p>
          )}
        </div>
      </div>
    </div>
  )
}
