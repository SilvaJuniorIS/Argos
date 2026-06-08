import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

const nav = [
  { to: '/argos', label: 'ARGOS' },
  { to: '/contratos/dashboard', label: 'Painel contratos' },
  { to: '/contratos', label: 'Contratos' },
  { to: '/atas', label: 'Atas de Registro' },
  { to: '/importacao/contratos', label: 'Incluir Arquivo' },
  { to: '/alertas', label: 'Alertas' },
  { to: '/fiscalizacao', label: 'Fiscalizacao' },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation()
  const { user, logout } = useAuth()

  return (
    <div className="flex min-h-screen bg-[#F5F7FA]">
      <aside className="flex w-60 flex-col bg-[#0A2342] p-4 text-white shadow-xl">
        <div className="mb-6">
          <div className="text-xl font-bold">ARGOS</div>
          <p className="mt-1 text-xs text-blue-100">Fiscalizacao inteligente, clara e segura.</p>
        </div>
        <nav className="flex flex-col gap-1">
          {nav.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className={`rounded-lg px-3 py-2 text-sm ${
                pathname === to || (to !== '/' && pathname.startsWith(to))
                  ? 'bg-[#1D4ED8] text-white shadow-sm'
                  : 'text-blue-50 hover:bg-white/10'
              }`}
            >
              {label}
            </Link>
          ))}
        </nav>
        <div className="mt-auto border-t border-white/15 pt-4 text-xs text-blue-100">
          <p className="font-medium text-white">{user?.nome}</p>
          <p>{user?.role}</p>
          <button type="button" onClick={logout} className="mt-2 text-orange-200 hover:underline">
            Sair
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto p-6">{children}</main>
    </div>
  )
}
