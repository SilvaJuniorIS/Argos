import { Link } from 'react-router-dom'
import heroAsset from '../assets/hero.png'
import ArgosLogo from '../components/brand/ArgosLogo'

const indicators = [
  { value: '87', label: 'score de risco', tone: 'text-amber-300' },
  { value: '15d', label: 'vigencia critica', tone: 'text-cyan-200' },
  { value: '42%', label: 'concentracao', tone: 'text-emerald-200' },
]

const signals = [
  { type: 'Vigencia', finding: 'Ata expira em 7 dias', action: 'Priorizar renovacao', level: 'Critico' },
  { type: 'Fornecedor', finding: 'Recorrencia acima da media', action: 'Revisar historico', level: 'Alerta' },
  { type: 'Valor', finding: 'Crescimento mensal atipico', action: 'Abrir trilha', level: 'Monitorar' },
]

const modules = [
  {
    title: 'Gestao contratual',
    text: 'Contratos, atas, anexos, vigencias, fiscais, gestores e fornecedores organizados em uma unica base operacional.',
  },
  {
    title: 'Alertas preventivos',
    text: 'Sinais de vencimento, risco documental e acompanhamento por secretaria antes que o problema vire urgencia.',
  },
  {
    title: 'Inteligencia documental',
    text: 'Apoio de IA para estruturar ETP, Termo de Referencia e minutas revisaveis, sem tirar o controle da equipe.',
  },
]

const flow = [
  'Cadastrar processo',
  'Gerar minuta',
  'Revisar documento',
  'Acompanhar alertas',
]

const evidence = [
  'Lei 14.133/2021 como contexto operacional',
  'Exportacao DOCX para revisao institucional',
  'Auditoria de acoes sensiveis',
  'Deploy preparado para Render',
]

export default function Vitrine() {
  return (
    <main className="min-h-screen bg-[#F5F7FA] text-[#0A2342]">
      <header className="fixed inset-x-0 top-0 z-30 border-b border-white/10 bg-[#07182D]/92 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-3">
          <Link to="/" className="flex items-center gap-3 text-white">
            <ArgosLogo compact />
            <span className="hidden text-sm font-semibold uppercase tracking-[0.18em] text-blue-100 sm:inline">
              AtlasNex GovTech
            </span>
          </Link>
          <nav className="flex items-center gap-2">
            <a href="#modulos" className="hidden rounded-lg px-3 py-2 text-sm font-semibold text-blue-50 hover:bg-white/10 md:inline-flex">
              Modulos
            </a>
            <a href="#implantacao" className="hidden rounded-lg px-3 py-2 text-sm font-semibold text-blue-50 hover:bg-white/10 md:inline-flex">
              Implantacao
            </a>
            <Link
              to="/login"
              className="rounded-lg bg-[#F59E0B] px-4 py-2 text-sm font-bold text-[#07182D] shadow-sm transition hover:bg-[#FBBF24]"
            >
              Entrar
            </Link>
          </nav>
        </div>
      </header>

      <section className="relative min-h-[92vh] overflow-hidden bg-[#07182D] pt-20 text-white">
        <img
          src={heroAsset}
          alt=""
          className="pointer-events-none absolute right-[4%] top-24 hidden w-[360px] opacity-35 lg:block"
        />
        <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(7,24,45,0.98)_0%,rgba(10,35,66,0.94)_48%,rgba(20,55,93,0.9)_100%)]" />
        <div className="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-[#F5F7FA] to-transparent" />

        <div className="relative mx-auto grid max-w-7xl gap-10 px-5 pb-20 pt-14 lg:grid-cols-[minmax(0,0.95fr)_minmax(420px,1.05fr)] lg:items-center">
          <div className="max-w-3xl">
            <p className="text-sm font-bold uppercase tracking-[0.22em] text-[#F8C873]">
              Vigilancia inteligente em compras publicas
            </p>
            <h1 className="mt-5 max-w-4xl text-5xl font-black leading-[0.96] tracking-normal text-white md:text-7xl">
              ARGOS
            </h1>
            <p className="mt-5 max-w-2xl text-xl font-semibold leading-8 text-cyan-100 md:text-2xl">
              Plataforma para estruturar processos, gerar minutas e acompanhar contratos com alertas acionaveis.
            </p>
            <p className="mt-5 max-w-2xl text-base leading-7 text-blue-100">
              O Argos ajuda equipes publicas a sair de planilhas dispersas para um ciclo rastreavel de cadastro,
              revisao documental, fiscalizacao e tomada de decisao.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/login"
                className="rounded-lg bg-[#F59E0B] px-5 py-3 text-sm font-extrabold text-[#07182D] shadow-lg shadow-amber-950/20 transition hover:bg-[#FBBF24]"
              >
                Acessar ambiente
              </Link>
              <a
                href="#modulos"
                className="rounded-lg border border-cyan-200/40 px-5 py-3 text-sm font-bold text-white transition hover:border-cyan-100 hover:bg-white/10"
              >
                Ver capacidades
              </a>
            </div>
          </div>

          <div className="rounded-lg border border-cyan-200/20 bg-white/10 p-4 shadow-2xl shadow-black/30 backdrop-blur">
            <div className="rounded-lg border border-white/10 bg-[#081E38]">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 px-5 py-4">
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.18em] text-cyan-200">Painel de vigilancia</p>
                  <h2 className="mt-1 text-xl font-black text-white">Contratacoes sob observacao</h2>
                </div>
                <span className="rounded-lg bg-emerald-400/15 px-3 py-2 text-xs font-black uppercase tracking-[0.12em] text-emerald-200">
                  Online
                </span>
              </div>

              <div className="grid gap-3 p-5 sm:grid-cols-3">
                {indicators.map((item) => (
                  <div key={item.label} className="rounded-lg border border-white/10 bg-[#0F2C4F] p-4">
                    <strong className={`block text-3xl font-black ${item.tone}`}>{item.value}</strong>
                    <span className="mt-2 block text-xs font-bold uppercase tracking-[0.08em] text-blue-100">
                      {item.label}
                    </span>
                  </div>
                ))}
              </div>

              <div className="px-5 pb-5">
                <div className="overflow-hidden rounded-lg border border-white/10">
                  <table className="w-full min-w-[520px] text-left text-sm">
                    <thead className="bg-[#0A2342] text-xs uppercase tracking-[0.08em] text-blue-100">
                      <tr>
                        <th className="px-4 py-3">Sinal</th>
                        <th className="px-4 py-3">Achado</th>
                        <th className="px-4 py-3">Resposta</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/10">
                      {signals.map((signal) => (
                        <tr key={signal.type}>
                          <td className="px-4 py-4">
                            <span className="block font-bold text-cyan-100">{signal.type}</span>
                            <span className="mt-1 inline-flex rounded-lg bg-[#F59E0B]/16 px-2 py-1 text-[11px] font-black uppercase tracking-[0.08em] text-[#F8C873]">
                              {signal.level}
                            </span>
                          </td>
                          <td className="px-4 py-4 text-blue-50">{signal.finding}</td>
                          <td className="px-4 py-4 text-white">{signal.action}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="modulos" className="mx-auto max-w-7xl px-5 py-16">
        <div className="grid gap-8 lg:grid-cols-[0.7fr_1.3fr] lg:items-end">
          <div>
            <p className="text-sm font-black uppercase tracking-[0.2em] text-[#B76E00]">Capacidades do MVP</p>
            <h2 className="mt-3 text-3xl font-black leading-tight text-[#0A2342] md:text-4xl">
              Uma base operacional para compras publicas com menos improviso.
            </h2>
          </div>
          <p className="max-w-3xl text-base leading-7 text-[#405B78]">
            A vitrine resume o que ja esta no projeto: contratos, alertas, importacao, documentos, dashboard,
            auditoria e geracao assistida de ETP e Termo de Referencia.
          </p>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {modules.map((module) => (
            <article key={module.title} className="rounded-lg border border-[#DCE6F2] bg-white p-6 shadow-sm">
              <h3 className="text-xl font-black text-[#0A2342]">{module.title}</h3>
              <p className="mt-3 text-sm leading-6 text-[#526B86]">{module.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="bg-white py-16">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 lg:grid-cols-[1fr_0.85fr]">
          <div>
            <p className="text-sm font-black uppercase tracking-[0.2em] text-[#1D4ED8]">Fluxo de trabalho</p>
            <h2 className="mt-3 max-w-2xl text-3xl font-black leading-tight md:text-4xl">
              Do planejamento ao acompanhamento, sem perder a trilha.
            </h2>
            <div className="mt-8 grid gap-3 sm:grid-cols-2">
              {flow.map((step, index) => (
                <div key={step} className="rounded-lg border border-[#DCE6F2] bg-[#F8FBFF] p-5">
                  <span className="text-xs font-black uppercase tracking-[0.16em] text-[#B76E00]">
                    Etapa {index + 1}
                  </span>
                  <strong className="mt-2 block text-lg text-[#0A2342]">{step}</strong>
                </div>
              ))}
            </div>
          </div>

          <aside id="implantacao" className="rounded-lg bg-[#0A2342] p-6 text-white shadow-xl">
            <p className="text-sm font-black uppercase tracking-[0.2em] text-[#F8C873]">Pronto para evoluir</p>
            <h2 className="mt-3 text-2xl font-black">Implantacao com base tecnica ja organizada.</h2>
            <ul className="mt-6 grid gap-3">
              {evidence.map((item) => (
                <li key={item} className="rounded-lg border border-white/10 bg-white/10 px-4 py-3 text-sm font-semibold text-blue-50">
                  {item}
                </li>
              ))}
            </ul>
            <Link
              to="/login"
              className="mt-7 inline-flex rounded-lg bg-[#F59E0B] px-5 py-3 text-sm font-extrabold text-[#07182D] transition hover:bg-[#FBBF24]"
            >
              Entrar no Argos
            </Link>
          </aside>
        </div>
      </section>
    </main>
  )
}
