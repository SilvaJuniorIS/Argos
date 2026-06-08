import { ChangeEvent, FormEvent, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import ArgosLogo from '../components/brand/ArgosLogo'
import { apiDocsURL, getApiErrorMessage } from '../services/api'
import {
  InstitucionalPayload,
  obterInstitucional,
  salvarInstitucional,
} from '../services/institucional'

const emptyForm: InstitucionalPayload = {
  nome_orgao: 'Prefeitura Municipal',
  nome_municipio: '',
  uf: '',
  cnpj: '',
  endereco: '',
  telefone: '',
  email: '',
  site: '',
  autoridade_nome: '',
  autoridade_cargo: '',
  responsavel_tecnico: '',
  rodape_documentos:
    'Documento gerado pelo ARGOS para apoio a elaboracao de minutas. Revise tecnicamente, juridicamente e administrativamente antes do uso oficial.',
  logo_base64: '',
}

function normalizeForm(form: InstitucionalPayload): InstitucionalPayload {
  return {
    ...form,
    nome_orgao: form.nome_orgao.trim(),
    nome_municipio: form.nome_municipio?.trim() || null,
    uf: form.uf?.trim().toUpperCase() || null,
    cnpj: form.cnpj?.trim() || null,
    endereco: form.endereco?.trim() || null,
    telefone: form.telefone?.trim() || null,
    email: form.email?.trim() || null,
    site: form.site?.trim() || null,
    autoridade_nome: form.autoridade_nome?.trim() || null,
    autoridade_cargo: form.autoridade_cargo?.trim() || null,
    responsavel_tecnico: form.responsavel_tecnico?.trim() || null,
    rodape_documentos: form.rodape_documentos?.trim() || null,
    logo_base64: form.logo_base64 || null,
  }
}

function fileToDataUrl(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result || ''))
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })
}

export default function Institucional() {
  const [form, setForm] = useState<InstitucionalPayload>(emptyForm)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState<'success' | 'error'>('success')

  useEffect(() => {
    async function loadConfig() {
      try {
        setLoading(true)
        const data = await obterInstitucional()
        setForm({
          nome_orgao: data.nome_orgao,
          nome_municipio: data.nome_municipio ?? '',
          uf: data.uf ?? '',
          cnpj: data.cnpj ?? '',
          endereco: data.endereco ?? '',
          telefone: data.telefone ?? '',
          email: data.email ?? '',
          site: data.site ?? '',
          autoridade_nome: data.autoridade_nome ?? '',
          autoridade_cargo: data.autoridade_cargo ?? '',
          responsavel_tecnico: data.responsavel_tecnico ?? '',
          rodape_documentos: data.rodape_documentos ?? '',
          logo_base64: data.logo_base64 ?? '',
        })
      } catch (error) {
        setMessageType('error')
        setMessage(getApiErrorMessage(error, 'Nao foi possivel carregar os dados institucionais.'))
      } finally {
        setLoading(false)
      }
    }

    loadConfig()
  }, [])

  function updateField(field: keyof InstitucionalPayload, value: string) {
    setForm((current) => ({ ...current, [field]: value }))
    setMessage('')
  }

  async function handleLogoChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) return
    try {
      const dataUrl = await fileToDataUrl(file)
      updateField('logo_base64', dataUrl)
    } catch {
      setMessageType('error')
      setMessage('Nao foi possivel carregar a imagem selecionada.')
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!form.nome_orgao.trim()) {
      setMessageType('error')
      setMessage('Informe o nome do orgao antes de salvar.')
      return
    }

    try {
      setSaving(true)
      const saved = await salvarInstitucional(normalizeForm(form))
      setForm({
        nome_orgao: saved.nome_orgao,
        nome_municipio: saved.nome_municipio ?? '',
        uf: saved.uf ?? '',
        cnpj: saved.cnpj ?? '',
        endereco: saved.endereco ?? '',
        telefone: saved.telefone ?? '',
        email: saved.email ?? '',
        site: saved.site ?? '',
        autoridade_nome: saved.autoridade_nome ?? '',
        autoridade_cargo: saved.autoridade_cargo ?? '',
        responsavel_tecnico: saved.responsavel_tecnico ?? '',
        rodape_documentos: saved.rodape_documentos ?? '',
        logo_base64: saved.logo_base64 ?? '',
      })
      setMessageType('success')
      setMessage('Dados institucionais salvos. Os proximos documentos ja usarao este padrao.')
    } catch (error) {
      setMessageType('error')
      setMessage(getApiErrorMessage(error, 'Nao foi possivel salvar os dados institucionais.'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="lite-shell">
      <aside className="lite-sidebar">
        <div>
          <div className="lite-brand-row">
            <ArgosLogo compact />
            <div>
              <h1>ARGOS</h1>
              <p>Padronizacao institucional dos documentos.</p>
            </div>
          </div>
        </div>

        <nav className="lite-menu" aria-label="Menu ARGOS">
          <Link to="/argos">Dashboard</Link>
          <Link to="/argos/processos/novo">Novo Processo</Link>
          <Link className="active" to="/argos/institucional">Institucional</Link>
          <a href={apiDocsURL}>API Docs</a>
        </nav>

        <div className="lite-sidebar-card">
          <span>Papel timbrado</span>
          <strong>Dados oficiais</strong>
          <small>Usados nos prompts, cabecalho, identificacao e rodape do DOCX.</small>
        </div>
      </aside>

      <main className="lite-main">
        <header className="lite-page-header">
          <div>
            <span className="lite-eyebrow">Configuracao</span>
            <h2>Dados Institucionais</h2>
            <p>Cadastre as informacoes oficiais do cliente para padronizar os documentos.</p>
          </div>
          <Link to="/argos" className="lite-ghost-button">Voltar para visao geral</Link>
        </header>

        {message && <div className={`lite-message ${messageType}`}>{message}</div>}

        <section className="lite-panel">
          {loading ? (
            <div className="lite-loading">
              <span className="lite-spinner" />
              <strong>Carregando dados</strong>
              <small>Preparando configuracao institucional.</small>
            </div>
          ) : (
            <form className="lite-form" onSubmit={handleSubmit}>
              <div className="lite-form-grid two">
                <label>
                  Nome do orgao
                  <input
                    value={form.nome_orgao}
                    maxLength={220}
                    onChange={(event) => updateField('nome_orgao', event.target.value)}
                  />
                </label>
                <label>
                  Municipio
                  <input
                    value={form.nome_municipio ?? ''}
                    maxLength={160}
                    onChange={(event) => updateField('nome_municipio', event.target.value)}
                  />
                </label>
              </div>

              <div className="lite-form-grid three">
                <label>
                  UF
                  <input
                    value={form.uf ?? ''}
                    maxLength={2}
                    onChange={(event) => updateField('uf', event.target.value)}
                  />
                </label>
                <label>
                  CNPJ
                  <input
                    value={form.cnpj ?? ''}
                    maxLength={30}
                    onChange={(event) => updateField('cnpj', event.target.value)}
                  />
                </label>
                <label>
                  Telefone
                  <input
                    value={form.telefone ?? ''}
                    maxLength={80}
                    onChange={(event) => updateField('telefone', event.target.value)}
                  />
                </label>
              </div>

              <label>
                Endereco
                <input
                  value={form.endereco ?? ''}
                  maxLength={300}
                  onChange={(event) => updateField('endereco', event.target.value)}
                />
              </label>

              <div className="lite-form-grid two">
                <label>
                  E-mail institucional
                  <input
                    value={form.email ?? ''}
                    maxLength={160}
                    onChange={(event) => updateField('email', event.target.value)}
                  />
                </label>
                <label>
                  Site
                  <input
                    value={form.site ?? ''}
                    maxLength={160}
                    onChange={(event) => updateField('site', event.target.value)}
                  />
                </label>
              </div>

              <div className="lite-form-grid three">
                <label>
                  Autoridade
                  <input
                    value={form.autoridade_nome ?? ''}
                    maxLength={180}
                    onChange={(event) => updateField('autoridade_nome', event.target.value)}
                  />
                </label>
                <label>
                  Cargo da autoridade
                  <input
                    value={form.autoridade_cargo ?? ''}
                    maxLength={120}
                    onChange={(event) => updateField('autoridade_cargo', event.target.value)}
                  />
                </label>
                <label>
                  Responsavel tecnico
                  <input
                    value={form.responsavel_tecnico ?? ''}
                    maxLength={180}
                    onChange={(event) => updateField('responsavel_tecnico', event.target.value)}
                  />
                </label>
              </div>

              <label>
                Rodape dos documentos
                <textarea
                  value={form.rodape_documentos ?? ''}
                  maxLength={1200}
                  onChange={(event) => updateField('rodape_documentos', event.target.value)}
                />
              </label>

              <div className="lite-logo-upload">
                <div>
                  <span className="lite-eyebrow">Brasao ou logomarca</span>
                  <strong>Imagem do timbre</strong>
                  <small>Use PNG ou JPG. A imagem sera aplicada no cabecalho do DOCX.</small>
                </div>
                {form.logo_base64 ? (
                  <img src={form.logo_base64} alt="Logo institucional" />
                ) : (
                  <div className="lite-logo-placeholder">Sem imagem</div>
                )}
                <label className="lite-secondary-button">
                  Selecionar imagem
                  <input type="file" accept="image/png,image/jpeg" onChange={handleLogoChange} />
                </label>
                {form.logo_base64 && (
                  <button
                    type="button"
                    className="lite-link-button"
                    onClick={() => updateField('logo_base64', '')}
                  >
                    Remover imagem
                  </button>
                )}
              </div>

              <div className="lite-form-actions">
                <button type="submit" className="lite-primary-button" disabled={saving}>
                  {saving ? 'Salvando...' : 'Salvar dados institucionais'}
                </button>
              </div>
            </form>
          )}
        </section>
      </main>
    </div>
  )
}
