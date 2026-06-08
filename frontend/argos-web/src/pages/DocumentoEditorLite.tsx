import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import ArgosLogo from '../components/brand/ArgosLogo'
import { apiDocsURL, getApiErrorMessage } from '../services/api'
import {
  atualizarDocumentoGerado,
  DocumentoGerado,
  exportarDocumentoGeradoDocx,
  obterDocumentoGerado,
} from '../services/documentosGerados'

function formatDate(value: string) {
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

function downloadBlob(documento: DocumentoGerado, blob: Blob) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `argos-${documento.tipo_documento.toLowerCase()}-${documento.id}.docx`
  link.click()
  URL.revokeObjectURL(url)
}

export default function DocumentoEditorLite() {
  const { id } = useParams()
  const documentoId = Number(id)
  const [documento, setDocumento] = useState<DocumentoGerado | null>(null)
  const [conteudo, setConteudo] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState<'success' | 'warning' | 'error'>('success')

  useEffect(() => {
    async function loadDocumento() {
      try {
        setLoading(true)
        setMessage('')
        const data = await obterDocumentoGerado(documentoId)
        setDocumento(data)
        setConteudo(data.conteudo)
      } catch (error) {
        setMessageType('error')
        setMessage(getApiErrorMessage(error, 'Nao foi possivel carregar o documento gerado.'))
      } finally {
        setLoading(false)
      }
    }

    if (!Number.isFinite(documentoId)) {
      setLoading(false)
      setMessageType('error')
      setMessage('Identificador do documento invalido.')
      return
    }

    loadDocumento()
  }, [documentoId])

  async function handleSave(): Promise<boolean> {
    if (!conteudo.trim()) {
      setMessageType('warning')
      setMessage('O documento precisa ter conteudo antes de salvar.')
      return false
    }
    try {
      setSaving(true)
      const updated = await atualizarDocumentoGerado(documentoId, conteudo)
      setDocumento(updated)
      setConteudo(updated.conteudo)
      setMessageType('success')
      setMessage('Revisao salva. Esta versao ja sera usada na exportacao DOCX.')
      return true
    } catch (error) {
      setMessageType('error')
      setMessage(getApiErrorMessage(error, 'Nao foi possivel salvar as alteracoes.'))
      return false
    } finally {
      setSaving(false)
    }
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(conteudo)
      setMessageType('success')
      setMessage('Texto copiado. Voce pode colar a minuta em outro editor.')
    } catch {
      setMessageType('warning')
      setMessage('Nao foi possivel copiar automaticamente. Selecione o texto e copie manualmente.')
    }
  }

  async function handleExport() {
    if (!documento) return
    try {
      const saved = await handleSave()
      if (!saved) return
      const blob = await exportarDocumentoGeradoDocx(documento.id)
      downloadBlob(documento, blob)
      setMessageType('success')
      setMessage('DOCX exportado com a versao revisada do documento.')
    } catch (error) {
      setMessageType('error')
      setMessage(getApiErrorMessage(error, 'Nao foi possivel exportar o DOCX.'))
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
              <p>Revisao humana antes da versao final.</p>
            </div>
          </div>
        </div>

        <nav className="lite-menu" aria-label="Menu ARGOS">
          <Link to="/argos">Dashboard</Link>
          <Link to="/argos/processos/novo">Novo Processo</Link>
          <a href={apiDocsURL}>API Docs</a>
        </nav>

        <div className="lite-sidebar-card">
          <span>Revisao humana</span>
          <strong>Controle humano</strong>
          <small>Revise, salve e exporte uma versao apresentavel em DOCX.</small>
        </div>
      </aside>

      <main className="lite-main">
        <header className="lite-page-header">
          <div>
            <span className="lite-eyebrow">Documento gerado</span>
            <h2>{documento ? `${documento.tipo_documento} em revisao` : 'Editor de documento'}</h2>
            {documento && (
              <p>
                Processo #{documento.processo_id} - Modelo {documento.modelo} - Criado em{' '}
                {formatDate(documento.created_at)}
              </p>
            )}
          </div>
          <Link to="/argos" className="lite-ghost-button">Voltar para visao geral</Link>
        </header>

        {message && <div className={`lite-message ${messageType}`}>{message}</div>}

        <section className="lite-panel">
          {loading ? (
            <div className="lite-loading">
              <span className="lite-spinner" />
              <strong>Preparando editor de revisao</strong>
              <small>Carregando a minuta gerada e os dados do processo.</small>
            </div>
          ) : !documento ? (
            <div className="lite-empty">
              <strong>Documento nao encontrado.</strong>
              <span>Volte para a visao geral e selecione um documento valido.</span>
            </div>
          ) : (
            <div className="lite-editor">
              <div className="lite-editor-toolbar">
                <div>
                  <span className="lite-eyebrow">Revisao da minuta</span>
                  <strong>Ajuste o texto antes de exportar</strong>
                </div>
                <div className="lite-editor-actions">
                  <button type="button" className="lite-ghost-button" onClick={handleCopy}>
                    Copiar texto
                  </button>
                  <button
                    type="button"
                    className="lite-secondary-button"
                    onClick={handleExport}
                    disabled={saving}
                  >
                    Exportar DOCX
                  </button>
                  <button
                    type="button"
                    className="lite-primary-button"
                    onClick={handleSave}
                    disabled={saving}
                  >
                    {saving ? 'Salvando revisao...' : 'Salvar revisao'}
                  </button>
                </div>
              </div>

              <textarea
                className="lite-document-editor"
                value={conteudo}
                onChange={(event) => {
                  setConteudo(event.target.value)
                  setMessage('')
                }}
                aria-label="Editor do documento gerado"
              />
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
