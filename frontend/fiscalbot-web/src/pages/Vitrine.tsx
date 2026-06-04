import { Link } from 'react-router-dom'

const metrics = [
  ['Risco 87', 'contrato com padrao atipico'],
  ['15 dias', 'vigencia critica detectada'],
  ['42%', 'concentracao por fornecedor'],
]

const signals = [
  ['Vencimento', 'Ata expira em 7 dias', 'critico'],
  ['Fornecedor', 'Recorrencia acima da media', 'alerta'],
  ['Valor', 'Crescimento atipico mensal', 'monitorar'],
]

const modules = [
  ['Monitoramento Inteligente', 'Contratos, atas, fornecedores, vigencias, valores e aditivos observados em fluxo continuo.'],
  ['Motor de Risco', 'Scores para contratos, fornecedores, orgaos e processos com sinais de recorrencia, concentracao e sobrepreco.'],
  ['Auditoria Automatizada', 'Verificacoes de publicacao, vigencia, duplicidade, ausencia documental e divergencias de valores.'],
]

export default function Vitrine() {
  return (
    <main className="min-h-screen bg-[#0B132B] text-slate-900">
      <section className="relative overflow-hidden border-b border-cyan-400/20">
        <div className="absolute inset-0 opacity-30">
          <div className="absolute left-1/2 top-1/2 h-[560px] w-[560px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-cyan-300/30" />
          <div className="absolute left-1/2 top-1/2 h-[360px] w-[360px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-cyan-300/30" />
          <div className="absolute left-1/2 top-1/2 h-[180px] w-[180px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[#F7931E]/40" />
        </div>

        <div className="relative mx-auto grid min-h-[86vh] max-w-7xl gap-10 px-6 py-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
          <div className="max-w-2xl">
            <p className="text-sm font-medium uppercase tracking-[0.22em] text-cyan-300">
              AtlasNex / Inteligencia Analitica
            </p>
            <h1 className="mt-4 text-6xl font-semibold leading-none text-white md:text-8xl">
              ARGOS
            </h1>
            <p className="mt-4 text-2xl font-medium text-[#00C2FF]">
              Vigilancia Inteligente em Compras Publicas
            </p>
            <p className="mt-5 max-w-xl text-lg leading-8 text-slate-700">
              O observador estrategico das contratacoes publicas: monitora riscos, revela
              padroes ocultos e transforma dados dispersos em fiscalizacao preventiva.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/login"
                className="rounded-lg bg-[#00C2FF] px-5 py-3 text-sm font-semibold text-[#0B132B] transition hover:bg-cyan-300"
              >
                Acessar demo
              </Link>
              <a
                href="#modulos"
                className="rounded-lg border border-slate-500 px-5 py-3 text-sm font-semibold text-slate-900 transition hover:border-[#F7931E] hover:text-[#F7931E]"
              >
                Ver inteligencia
              </a>
            </div>
          </div>

          <div className="relative">
            <div className="rounded-lg border border-cyan-300/30 bg-[#101B33] shadow-2xl shadow-cyan-950/60">
              <div className="flex items-center justify-between border-b border-cyan-300/20 px-5 py-4">
                <div>
                  <p className="text-xs uppercase text-slate-600">Radar inteligente</p>
                  <p className="font-semibold text-white">Contratacoes sob vigilancia</p>
                </div>
                <span className="rounded-full bg-[#F7931E]/15 px-3 py-1 text-xs text-[#F7931E]">
                  Observando
                </span>
              </div>
              <div className="grid gap-3 p-5 sm:grid-cols-3">
                {metrics.map(([value, label]) => (
                  <div key={label} className="rounded-lg border border-cyan-300/20 bg-[#0B132B] p-4">
                    <p className="text-2xl font-semibold text-[#00C2FF]">{value}</p>
                    <p className="mt-1 text-xs text-slate-600">{label}</p>
                  </div>
                ))}
              </div>
              <div className="px-5 pb-5">
                <div className="overflow-hidden rounded-lg border border-cyan-300/20">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-[#0B132B] text-xs uppercase text-slate-600">
                      <tr>
                        <th className="px-4 py-3">Sinal</th>
                        <th className="px-4 py-3">Achado</th>
                        <th className="px-4 py-3">Acao</th>
                      </tr>
                    </thead>
                    <tbody>
                      {signals.map(([signal, finding, action]) => (
                        <tr key={signal} className="border-t border-cyan-300/15">
                          <td className="px-4 py-3 text-cyan-300">{signal}</td>
                          <td className="px-4 py-3 text-slate-700">{finding}</td>
                          <td className="px-4 py-3">
                            <span className="rounded-full bg-white px-2 py-1 text-xs text-[#F7931E]">
                              {action}
                            </span>
                          </td>
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

      <section id="modulos" className="mx-auto max-w-7xl px-6 py-14">
        <div className="mb-8 max-w-3xl">
          <p className="text-sm uppercase tracking-[0.22em] text-[#F7931E]">Hermes corre. Icaro planeja. Argos observa.</p>
          <h2 className="mt-3 text-3xl font-semibold text-white">
            Infraestrutura de vigilancia para a administracao publica orientada por dados.
          </h2>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {modules.map(([title, text]) => (
            <article key={title} className="rounded-lg border border-cyan-300/20 bg-[#101B33] p-5">
              <h3 className="text-lg font-semibold text-white">{title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{text}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  )
}

