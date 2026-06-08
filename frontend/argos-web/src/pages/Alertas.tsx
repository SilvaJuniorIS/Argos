import { useEffect, useState } from 'react'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import { useAuth } from '../hooks/useAuth'
import { fetchAlertas, fetchResumo, gerarAlertas, marcarLido, resolver } from '../services/alertas'
import type { Alerta, AlertaResumo } from '../types'

type Filtro = 'pendentes' | 'lidos' | 'resolvidos' | 'todos'

const filtroParams: Record<Filtro, { lido?: boolean; resolvido?: boolean }> = {
  pendentes: { lido: false, resolvido: false },
  lidos: { lido: true },
  resolvidos: { resolvido: true },
  todos: {},
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(new Date(`${value}T00:00:00`))
}

function severity(alerta: Alerta) {
  if (alerta.tipo === 'contract_expiration') return 'Urgente'
  if (['vencimento_30', 'vencimento_15', 'vencimento_7', 'vencimento_1'].includes(alerta.tipo)) return 'Urgente'
  if (alerta.tipo === 'vencimento_90' || alerta.tipo === 'reajuste_anual') return 'Atencao'
  return 'Informativo'
}

export default function Alertas() {
  const { hasRole } = useAuth()
  const [alertas, setAlertas] = useState<Alerta[]>([])
  const [resumo, setResumo] = useState<AlertaResumo | null>(null)
  const [filtro, setFiltro] = useState<Filtro>('pendentes')
  const [loading, setLoading] = useState(true)
  const [actionId, setActionId] = useState<number | null>(null)
  const [gerando, setGerando] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const [list, sum] = await Promise.all([
        fetchAlertas({ ...filtroParams[filtro], limit: 100 }),
        fetchResumo(),
      ])
      setAlertas(list)
      setResumo(sum)
    } catch {
      setError('Nao foi possivel carregar os alertas agora.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [filtro])

  async function onLido(id: number) {
    setActionId(id)
    try {
      await marcarLido(id)
      await load()
    } finally {
      setActionId(null)
    }
  }

  async function onResolver(id: number) {
    setActionId(id)
    try {
      await resolver(id)
      await load()
    } finally {
      setActionId(null)
    }
  }

  async function onGerarAlertas() {
    setGerando(true)
    setFeedback(null)
    setError(null)
    try {
      const result = await gerarAlertas()
      setFeedback(
        result.total === 0
          ? 'Nenhum novo alerta encontrado na varredura.'
          : `${result.total} novo(s) alerta(s): ${result.vencimentos} vencimento(s), ${result.reajustes} reajuste(s) e ${result.contratos_importados || 0} contrato(s) importado(s).`,
      )
      await load()
    } catch {
      setError('Nao foi possivel gerar alertas. Verifique suas permissoes e tente novamente.')
    } finally {
      setGerando(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Alertas</h1>
          <p className="mt-1 text-sm text-slate-600">
            Central de acompanhamento de vencimentos, reajustes e pendencias operacionais.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="ghost" onClick={load} disabled={loading}>
            Atualizar
          </Button>
          {hasRole('admin') && (
            <Button onClick={onGerarAlertas} disabled={gerando}>
              {gerando ? 'Gerando...' : 'Gerar alertas'}
            </Button>
          )}
        </div>
      </div>
      {resumo && (
        <div className="grid gap-4 sm:grid-cols-4">
          <Card title="Urgentes" value={resumo.urgentes} />
          <Card title="Atencao" value={resumo.atencao} />
          <Card title="Informativos" value={resumo.info} />
          <Card title="Nao lidos" value={resumo.total_nao_lidos} />
        </div>
      )}
      <div className="flex flex-wrap gap-2 rounded-xl border border-slate-200 bg-white p-2">
        {(['pendentes', 'lidos', 'resolvidos', 'todos'] as Filtro[]).map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setFiltro(item)}
            className={`rounded-lg px-3 py-2 text-sm font-medium capitalize transition ${
              filtro === item ? 'bg-[#1D4ED8] text-white' : 'text-slate-700 hover:bg-slate-100'
            }`}
          >
            {item}
          </button>
        ))}
      </div>
      {feedback && (
        <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">
          {feedback}
        </div>
      )}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}
      <div className="space-y-3">
        {loading &&
          Array.from({ length: 3 }).map((_, index) => (
            <div
              key={index}
              className="h-32 animate-pulse rounded-xl border border-slate-200 bg-white"
            />
          ))}
        {!loading && alertas.map((a) => (
          <div
            key={a.id}
            className="flex flex-wrap items-start justify-between gap-3 rounded-xl border border-slate-200 bg-white p-4"
          >
            <div className="max-w-3xl">
              <div className="flex flex-wrap items-center gap-2">
                <Badge label={severity(a)} />
                <Badge label={a.tipo} />
                <Badge label={a.status} />
              </div>
              <h3 className="mt-1 font-medium">{a.titulo}</h3>
              <p className="text-sm text-slate-600">{a.mensagem}</p>
              <p className="mt-1 text-xs text-slate-500">
                Contrato #{a.contrato_id} - Referencia {formatDate(a.data_referencia)}
              </p>
            </div>
            <div className="flex gap-2">
              {a.origem !== 'notification' && a.status !== 'lido' && a.status !== 'resolvido' && (
                <Button variant="ghost" onClick={() => onLido(a.id)} disabled={actionId === a.id}>
                Marcar lido
              </Button>
              )}
              {a.origem !== 'notification' && a.status !== 'resolvido' && (
                <Button onClick={() => onResolver(a.id)} disabled={actionId === a.id}>
                  Resolver
                </Button>
              )}
            </div>
          </div>
        ))}
        {!loading && alertas.length === 0 && (
          <div className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-600">
            Nenhum alerta encontrado para este filtro.
          </div>
        )}
      </div>
    </div>
  )
}

