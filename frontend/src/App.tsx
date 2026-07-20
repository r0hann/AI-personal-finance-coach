import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Transactions from './pages/Transactions'
import Insights from './pages/Insights'
import Chat from './pages/Chat'
import Budget from './pages/Budget'

const NAV = [
  { to: '/', label: '📊 Dashboard' },
  { to: '/transactions', label: '🧾 Transactions' },
  { to: '/insights', label: '💡 Insights' },
  { to: '/chat', label: '💬 Ask AI' },
  { to: '/budget', label: '🎯 Budget' },
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        <nav className="bg-white border-b border-gray-200 px-6 py-3 flex gap-6 sticky top-0 z-10 shadow-sm">
          <span className="font-bold text-indigo-600 mr-4 text-lg">💰 Finance Coach</span>
          {NAV.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `text-sm font-medium transition-colors ${isActive ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-800'}`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <main className="flex-1 p-6 max-w-6xl mx-auto w-full">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/insights" element={<Insights />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/budget" element={<Budget />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
