import { useEffect, useMemo, useState } from 'react'
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Link } from 'react-router-dom'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import { fetchContracts, fetchContractsDashboard } from '../services/contracts'
import type { Contract, ContractDashboard } from '../types'

const PIE_COLORS = ['#1D4ED8', '#16A34A', '#F59E0B', '#EF4444', '#64748B']

function money(value?: string | number | null) {
  return Number(value ?? 0).toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  })
}

export default function Dashboard() {
  const [dash, setDash] = useState<ContractDashboard | null>(null)
  const [contracts, setContracts] = useState<Contract[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    Promise.all([
      fetchContractsDashboard(),
      fetchContracts({ limit: 100, page: 1 }),
    ])
      .then(([dashboard, result]) => {
        setDash(dashboard)
        setContracts(result.items)
        setError('')
      })
      .catch(() => {
        setError('Nao foi possivel carregar o dashboard. Verifique se a API esta em execucao.')
      })
      .finally(() => setLoading(false))
  }, [])

  const porSecretaria = useMemo(() => {
    const totals = new Map<string, number>()
    contracts.forEach((contract) => {
      const key = contract.secretaria || 'Sem secretaria'
      totals.set(key, (totals.get(key) || 0) + 1)
    })
    return Array.from(totals, ([nome, total]) => ({ nome, total }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 8)
  }, [contracts])

  const porStatus = useMemo(() => {
    const totals = new Map<string, number>()
    contracts.forEach((contract) => {
      const key = contract.status || 'sem_status'
      totals.set(key, (totals.get(key) || 0) + 1)
    })
    return Array.from(totals, ([status, total]) => ({ status, total }))
  }, [contracts])

  if (loading) return <p className="text-slate-600">Carregando dashboard...</p>

  if (error || !dash) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-semibold">Dashboard gerencial</h1>
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error || 'Dashboard indisponivel.'}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Dashboard gerencial</h1>
        <Link to="/importacao/contratos">
          <Button type="button">Incluir arquivo no banco</Button>
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <Card title="Contratos ativos" value={dash.contratos_ativos} />
        <Card title="Vencendo em 30 dias" value={dash.vencendo_em_30} />
        <Card title="Vencendo em 15 dias" value={dash.vencendo_em_15} />
        <Card title="Vencidos" value={dash.vencidos} />
        <Card title="Valor contratado" value={money(dash.valor_total_contratado)} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <h2 className="mb-3 text-sm font-medium text-slate-700">Por secretaria</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={porSecretaria}>
              <XAxis dataKey="nome" tick={{ fill: '#64748B', fontSize: 11 }} />
              <YAxis tick={{ fill: '#64748B', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0A2342' }} />
              <Bar dataKey="total" fill="#1D4ED8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <h2 className="mb-3 text-sm font-medium text-slate-700">Por status</h2>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={porStatus} dataKey="total" nameKey="status" cx="50%" cy="50%" outerRadius={80}>
                {porStatus.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0A2342' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-4">
        <h2 className="mb-3 text-sm font-medium text-slate-700">Ultimos instrumentos importados</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500">
              <th className="pb-2">Numero</th>
              <th>Fornecedor</th>
              <th>Status</th>
              <th>Termino</th>
            </tr>
          </thead>
          <tbody>
            {contracts.slice(0, 5).map((contract) => (
              <tr key={contract.id} className="border-t border-slate-200">
                <td className="py-2">
                  <Link className="text-[#1D4ED8] hover:underline" to={`/contratos/${contract.id}`}>
                    {contract.numero_contrato || 'Sem numero'}
                  </Link>
                </td>
                <td className="text-slate-700">{contract.fornecedor || '-'}</td>
                <td>
                  <Badge label={contract.status || 'sem_status'} />
                </td>
                <td className="text-slate-600">{contract.fim_vigencia || '-'}</td>
              </tr>
            ))}
            {contracts.length === 0 && (
              <tr>
                <td colSpan={4} className="border-t border-slate-200 py-6 text-center text-slate-500">
                  Nenhum arquivo importado ainda.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

