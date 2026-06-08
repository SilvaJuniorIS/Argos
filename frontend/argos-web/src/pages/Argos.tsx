import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import ArgosLogo from '../components/brand/ArgosLogo'
import { apiDocsURL, getApiErrorMessage } from '../services/api'
import {
  obterDashboardProcessosLicitatorios,
  ProcessoDashboard,
  ProcessoDashboardStatus,
} from '../services/processosLicitatorios'

function formatDate(value: string) {
  return new Intl.DateTimeFormat('pt-BR').format(new Date(value))
}

export default function Argos() {
  const [dashboard, setDashboard] = useState<ProcessoDashboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function loadDashboard() {
    try {
      setError('')
      setLoading(true)
      setDashboard(await obterDashboardProcessosLicitatorios())
    } catch (error) {
      setError(getApiErrorMessage(error, 'Nao foi possivel carregar o dashboard.'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDashboard()
  }, [])

  const ultimosProcessos = dashboard?.ultimos_processos ?? []

  return (
    <div className="lite-shell">
      <aside className="lite-sidebar">
        <div>
          <div className="lite-brand-row">
            <ArgosLogo compact />
            <div>
              <h1>ARGOS</h1>
              <p>Inteligencia documental para a Lei 14.133/2021.</p>
            </div>
          </div>
        </div>

        <nav className="lite-menu" aria-label="Menu ARGOS">
          <a className="active" href="#dashboard">Visao Geral</a>
          <a href="#processos">Ultimos Processos</a>
          <a href="#documentos">Documentos</a>
          <a href={apiDocsURL}>API Docs</a>
        </nav>

        <div className="lite-sidebar-card">
          <span>Pronto para demo</span>
          <strong>Fluxo completo</strong>
          <small>Cadastro, IA, revisao humana e exportacao DOCX.</small>
        </div>
      </aside>

      <main className="lite-main">
        <header className="lite-hero" id="dashboard">
          <div>
            <span className="lite-eyebrow">AtlasNex GovTech</span>
            <h2>ARGOS</h2>
            <p>
              Inteligencia documental para a Lei 14.133/2021. Transforme dados basicos do processo
              em minutas estruturadas de ETP e Termo de Referencia, com revisao humana e exportacao
              em DOCX.
            </p>
            <div className="lite-hero-badges">
              <span>Lei 14.133/2021</span>
              <span>ETP e TR</span>
              <span>Exportacao DOCX</span>
            </div>
          </div>
          <Link to="/argos/processos/novo" className="lite-primary-button">
            Criar Novo Processo
          </Link>
        </header>

        <section className="lite-stats lite-dashboard-stats" aria-label="Resumo do ARGOS">
          <article>
            <span>Total de processos</span>
            <strong>{dashboard?.total_processos ?? 0}</strong>
            <small>Processos cadastrados</small>
          </article>
          <article>
            <span>Documentos gerados</span>
            <strong>{dashboard?.total_documentos_gerados ?? 0}</strong>
            <small>ETPs e Termos de Referencia</small>
          </article>
          <article>
            <span>Gerados</span>
            <strong>{dashboard?.total_gerado ?? 0}</strong>
            <small>Minutas aguardando revisao</small>
          </article>
          <article>
            <span>Revisados</span>
            <strong>{dashboard?.total_revisado ?? 0}</strong>
            <small>Minutas revisadas no editor</small>
          </article>
        </section>

        <section className="lite-status-row" aria-label="Status dos processos">
          {(['Rascunho', 'Gerado', 'Revisado'] as ProcessoDashboardStatus[]).map((status) => (
            <article key={status} className={`lite-status-card ${status.toLowerCase()}`}>
              <span>{status}</span>
              <strong>{dashboard?.por_status.find((item) => item.status === status)?.total ?? 0}</strong>
            </article>
          ))}
        </section>

        {error && <div className="lite-alert">{error}</div>}

        <section className="lite-panel" id="processos">
          <div className="lite-panel-header">
            <div>
              <span className="lite-eyebrow">Processos</span>
              <h3>Ultimos processos</h3>
            </div>
            <button type="button" className="lite-ghost-button" onClick={loadDashboard}>
              Atualizar dados
            </button>
          </div>

          {loading ? (
            <div className="lite-loading">
              <span className="lite-spinner" />
              <strong>Preparando sua visao geral</strong>
              <small>Carregando processos, documentos e status de revisao.</small>
            </div>
          ) : ultimosProcessos.length === 0 ? (
            <div className="lite-empty">
              <strong>Comece seu primeiro processo.</strong>
              <span>Cadastre os dados principais para gerar uma minuta de ETP ou Termo de Referencia.</span>
              <Link to="/argos/processos/novo" className="lite-primary-button">
                Criar primeiro processo
              </Link>
            </div>
          ) : (
            <div className="lite-table-wrap">
              <table className="lite-table">
                <thead>
                  <tr>
                    <th>Objeto</th>
                    <th>Secretaria</th>
                    <th>Tipo</th>
                    <th>Status</th>
                    <th>Modalidade</th>
                    <th>Criado em</th>
                    <th>Acoes</th>
                  </tr>
                </thead>
                <tbody>
                  {ultimosProcessos.map((processo) => (
                    <tr key={processo.id}>
                      <td>
                        <strong>{processo.objeto}</strong>
                        <span>{processo.total_documentos} documento(s) gerado(s)</span>
                      </td>
                      <td>{processo.secretaria}</td>
                      <td>
                        <span className="lite-chip">{processo.tipo_documento}</span>
                      </td>
                      <td>
                        <span className={`lite-status-pill ${processo.status.toLowerCase()}`}>
                          {processo.status}
                        </span>
                      </td>
                      <td>{processo.modalidade || 'A definir'}</td>
                      <td>{formatDate(processo.created_at)}</td>
                      <td>
                        <Link to={`/argos/processos/${processo.id}`} className="lite-link-button">
                          {processo.status === 'Rascunho' ? 'Continuar' : 'Abrir'}
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
