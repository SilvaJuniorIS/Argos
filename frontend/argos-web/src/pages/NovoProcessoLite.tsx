import { FormEvent, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import ArgosLogo from '../components/brand/ArgosLogo'
import { apiDocsURL, getApiErrorMessage } from '../services/api'
import { gerarDocumento } from '../services/documentosGerados'
import {
  criarProcessoLicitatorio,
  atualizarProcessoLicitatorio,
  obterProcessoLicitatorio,
  ProcessoLicitatorio,
  ProcessoLicitatorioItem,
  ProcessoLicitatorioPayload,
} from '../services/processosLicitatorios'

type FormErrors = Partial<Record<keyof ProcessoLicitatorioPayload, string>>
type ItemErrors = Record<string, string>
type ProcessoItemDraft = Omit<ProcessoLicitatorioItem, 'id' | 'ordem'>

const emptyForm: ProcessoLicitatorioPayload = {
  objeto: '',
  secretaria: '',
  justificativa: '',
  quantidade: '',
  unidade_medida: '',
  modalidade: '',
  prazo_execucao: '',
  observacoes: '',
  tipo_documento: 'ETP',
  itens: [
    {
      descricao: '',
      quantidade: '',
      unidade_medida: '',
      observacoes: '',
    },
  ],
}

function validate(form: ProcessoLicitatorioPayload) {
  const errors: FormErrors = {}
  const itemErrors: ItemErrors = {}
  if (!form.objeto.trim()) errors.objeto = 'Descreva o objeto da contratacao.'
  if (!form.secretaria.trim()) errors.secretaria = 'Informe a secretaria ou area requisitante.'
  if (!form.justificativa.trim()) errors.justificativa = 'Explique a necessidade que motiva a contratacao.'
  if (!form.modalidade?.trim()) errors.modalidade = 'Informe a modalidade prevista.'
  if (!form.prazo_execucao?.trim()) errors.prazo_execucao = 'Informe o prazo estimado.'
  if (!form.itens?.length) {
    itemErrors.itens = 'Inclua pelo menos um item.'
  }
  form.itens?.forEach((item, index) => {
    if (!item.descricao.trim()) itemErrors[`itens.${index}.descricao`] = 'Informe o item.'
    if (String(item.quantidade ?? '').trim() === '') {
      itemErrors[`itens.${index}.quantidade`] = 'Informe a quantidade.'
    }
    if (String(item.quantidade ?? '').trim() !== '' && Number.isNaN(Number(item.quantidade))) {
      itemErrors[`itens.${index}.quantidade`] = 'Informe uma quantidade numerica.'
    }
    if (Number(item.quantidade) < 0) {
      itemErrors[`itens.${index}.quantidade`] = 'A quantidade nao pode ser negativa.'
    }
    if (!item.unidade_medida.trim()) itemErrors[`itens.${index}.unidade_medida`] = 'Informe a unidade.'
  })
  return { errors, itemErrors }
}

function processoToForm(processo: ProcessoLicitatorio): ProcessoLicitatorioPayload {
  return {
    objeto: processo.objeto,
    secretaria: processo.secretaria,
    justificativa: processo.justificativa,
    quantidade: processo.quantidade ?? '',
    unidade_medida: processo.unidade_medida ?? '',
    modalidade: processo.modalidade ?? '',
    prazo_execucao: processo.prazo_execucao ?? '',
    observacoes: processo.observacoes ?? '',
    tipo_documento: processo.tipo_documento,
    itens:
      processo.itens.length > 0
        ? processo.itens.map((item) => ({
            descricao: item.descricao,
            quantidade: item.quantidade,
            unidade_medida: item.unidade_medida,
            observacoes: item.observacoes ?? '',
          }))
        : emptyForm.itens,
  }
}

function normalizePayload(form: ProcessoLicitatorioPayload): ProcessoLicitatorioPayload {
  const firstItem = form.itens?.[0]
  return {
    ...form,
    quantidade: firstItem?.quantidade === '' ? null : firstItem?.quantidade,
    unidade_medida: firstItem?.unidade_medida || null,
    modalidade: form.modalidade || null,
    prazo_execucao: form.prazo_execucao || null,
    observacoes: form.observacoes || null,
    itens: form.itens?.map((item) => ({
      ...item,
      quantidade: item.quantidade === '' ? 0 : item.quantidade,
      observacoes: item.observacoes || null,
    })),
  }
}

export default function NovoProcessoLite() {
  const { id } = useParams()
  const processoId = id ? Number(id) : null
  const [form, setForm] = useState<ProcessoLicitatorioPayload>(emptyForm)
  const [errors, setErrors] = useState<FormErrors>({})
  const [itemErrors, setItemErrors] = useState<ItemErrors>({})
  const [loadingProcesso, setLoadingProcesso] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState<'success' | 'warning' | 'error'>('success')
  const [savedProcesso, setSavedProcesso] = useState<ProcessoLicitatorio | null>(null)
  const [generating, setGenerating] = useState(false)
  const navigate = useNavigate()

  const hasErrors = useMemo(
    () => Object.keys(errors).length > 0 || Object.keys(itemErrors).length > 0,
    [errors, itemErrors],
  )

  useEffect(() => {
    if (!processoId || Number.isNaN(processoId)) return
    const currentProcessoId = processoId

    async function loadProcesso() {
      try {
        setLoadingProcesso(true)
        setMessage('')
        const processo = await obterProcessoLicitatorio(currentProcessoId)
        setForm(processoToForm(processo))
        setSavedProcesso(processo)
      } catch (error) {
        setMessageType('error')
        setMessage(getApiErrorMessage(error, 'Nao foi possivel carregar este processo.'))
      } finally {
        setLoadingProcesso(false)
      }
    }

    loadProcesso()
  }, [processoId])

  function updateField(field: keyof ProcessoLicitatorioPayload, value: string) {
    setForm((current) => ({ ...current, [field]: value }))
    setSavedProcesso(null)
    setErrors((current) => {
      const next = { ...current }
      delete next[field]
      return next
    })
    setMessage('')
  }

  function updateItemField(index: number, field: keyof ProcessoItemDraft, value: string) {
    setForm((current) => ({
      ...current,
      itens: (current.itens ?? []).map((item, itemIndex) =>
        itemIndex === index ? { ...item, [field]: value } : item,
      ),
    }))
    setSavedProcesso(null)
    setItemErrors((current) => {
      const next = { ...current }
      delete next[`itens.${index}.${field}`]
      return next
    })
    setMessage('')
  }

  function addItem() {
    setForm((current) => ({
      ...current,
      itens: [
        ...(current.itens ?? []),
        { descricao: '', quantidade: '', unidade_medida: '', observacoes: '' },
      ],
    }))
    setSavedProcesso(null)
    setMessage('')
  }

  function removeItem(index: number) {
    setForm((current) => ({
      ...current,
      itens:
        current.itens && current.itens.length > 1
          ? current.itens.filter((_, itemIndex) => itemIndex !== index)
          : current.itens,
    }))
    setSavedProcesso(null)
    setItemErrors({})
    setMessage('')
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const { errors: validationErrors, itemErrors: validationItemErrors } = validate(form)
    setErrors(validationErrors)
    setItemErrors(validationItemErrors)
    if (Object.keys(validationErrors).length > 0 || Object.keys(validationItemErrors).length > 0) {
      setMessageType('warning')
      setMessage('Alguns dados essenciais ainda precisam ser preenchidos para salvar o processo.')
      return
    }

    try {
      setSaving(true)
      setMessage('')
      const payload = normalizePayload(form)
      const saved =
        processoId && !Number.isNaN(processoId)
          ? await atualizarProcessoLicitatorio(processoId, payload)
          : await criarProcessoLicitatorio(payload)
      setSavedProcesso(saved)
      setMessageType('success')
      setMessage('Processo salvo. Agora voce pode gerar a minuta para revisao ou continuar editando.')
    } catch (error) {
      setMessageType('error')
      setMessage(getApiErrorMessage(error, 'Nao foi possivel salvar agora. Tente novamente.'))
    } finally {
      setSaving(false)
    }
  }

  async function handleGerarDocumento() {
    if (!savedProcesso) {
      const { errors: validationErrors, itemErrors: validationItemErrors } = validate(form)
      setErrors(validationErrors)
      setItemErrors(validationItemErrors)
      setMessageType('warning')
      setMessage(
        Object.keys(validationErrors).length > 0 || Object.keys(validationItemErrors).length > 0
          ? 'Preencha os campos destacados e salve o processo antes de gerar a minuta.'
          : 'Salve o processo antes de gerar a minuta.',
      )
      return
    }
    try {
      setGenerating(true)
      setMessageType('warning')
      setMessage('Gerando minuta com IA. Mantenha esta tela aberta por alguns instantes.')
      const documento = await gerarDocumento(savedProcesso.id, savedProcesso.tipo_documento)
      navigate(`/argos/documentos/${documento.id}`)
    } catch (error) {
      setMessageType('error')
      setMessage(
        getApiErrorMessage(
          error,
          'Nao foi possivel gerar o documento. Verifique a configuracao de IA no backend e tente novamente.',
        ),
      )
    } finally {
      setGenerating(false)
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
              <p>Cadastro guiado para ETP e Termo de Referencia.</p>
            </div>
          </div>
        </div>

        <nav className="lite-menu" aria-label="Menu ARGOS">
          <Link to="/argos">Dashboard</Link>
          <Link className="active" to="/argos/processos/novo">Novo Processo</Link>
          <a href={apiDocsURL}>API Docs</a>
        </nav>

        <div className="lite-sidebar-card">
          <span>Cadastro guiado</span>
          <strong>Entrada qualificada</strong>
          <small>Quanto melhores os dados, melhor a primeira minuta.</small>
        </div>
      </aside>

      <main className="lite-main">
        <header className="lite-page-header">
          <div>
            <span className="lite-eyebrow">Processos licitatorios</span>
            <h2>{processoId ? 'Continuar Processo' : 'Novo Processo'}</h2>
            <p>Informe os dados essenciais para gerar uma minuta consistente e pronta para revisao.</p>
          </div>
          <Link to="/argos" className="lite-ghost-button">Voltar para visao geral</Link>
        </header>

        {message && <div className={`lite-message ${messageType}`}>{message}</div>}

        <section className="lite-panel">
          {loadingProcesso && (
            <div className="lite-loading">
              <span className="lite-spinner" />
              <strong>Carregando processo</strong>
              <small>Recuperando os dados salvos para continuar o preenchimento.</small>
            </div>
          )}

          <div className="lite-step-strip" aria-label="Etapas do fluxo">
            <span className="active">1. Dados gerais</span>
            <span>2. Itens</span>
            <span>3. Geracao IA</span>
            <span>4. Revisao</span>
          </div>

          <form className="lite-form" onSubmit={handleSubmit} noValidate>
            <label>
              Objeto da contratacao
              <textarea
                className={errors.objeto ? 'invalid' : ''}
                maxLength={2000}
                value={form.objeto}
                onChange={(event) => updateField('objeto', event.target.value)}
                placeholder="Ex.: Aquisicao de notebooks para equipes tecnicas"
              />
              {errors.objeto && <span className="lite-field-error">{errors.objeto}</span>}
            </label>

            <div className="lite-form-grid two">
              <label>
                Secretaria / area requisitante
                <input
                  className={errors.secretaria ? 'invalid' : ''}
                  maxLength={160}
                  value={form.secretaria}
                  onChange={(event) => updateField('secretaria', event.target.value)}
                  placeholder="Ex.: Secretaria de Administracao"
                />
                {errors.secretaria && <span className="lite-field-error">{errors.secretaria}</span>}
              </label>
              <label>
                Modalidade prevista
                <input
                  className={errors.modalidade ? 'invalid' : ''}
                  maxLength={120}
                  value={form.modalidade ?? ''}
                  onChange={(event) => updateField('modalidade', event.target.value)}
                  placeholder="Ex.: pregao eletronico"
                />
                {errors.modalidade && <span className="lite-field-error">{errors.modalidade}</span>}
              </label>
            </div>

            <label>
              Justificativa da necessidade
              <textarea
                className={errors.justificativa ? 'invalid' : ''}
                maxLength={4000}
                value={form.justificativa}
                onChange={(event) => updateField('justificativa', event.target.value)}
                placeholder="Explique a necessidade publica que fundamenta a contratacao"
              />
              {errors.justificativa && (
                <span className="lite-field-error">{errors.justificativa}</span>
              )}
            </label>

            <label>
              Prazo estimado
              <input
                className={errors.prazo_execucao ? 'invalid' : ''}
                maxLength={120}
                value={form.prazo_execucao ?? ''}
                onChange={(event) => updateField('prazo_execucao', event.target.value)}
                placeholder="Ex.: 30 dias"
              />
              {errors.prazo_execucao && (
                <span className="lite-field-error">{errors.prazo_execucao}</span>
              )}
            </label>

            <div className="lite-items-section">
              <div className="lite-items-header">
                <div>
                  <span className="lite-eyebrow">Itens do processo</span>
                  <strong>Inclua os bens ou servicos previstos</strong>
                </div>
                <button type="button" className="lite-ghost-button" onClick={addItem}>
                  Adicionar item
                </button>
              </div>

              {itemErrors.itens && <span className="lite-field-error">{itemErrors.itens}</span>}

              {(form.itens ?? []).map((item, index) => (
                <div className="lite-item-card" key={index}>
                  <div className="lite-item-title">
                    <strong>Item {index + 1}</strong>
                    <button
                      type="button"
                      className="lite-link-button"
                      onClick={() => removeItem(index)}
                      disabled={(form.itens ?? []).length === 1}
                    >
                      Remover
                    </button>
                  </div>
                  <label>
                    Descricao do item
                    <input
                      className={itemErrors[`itens.${index}.descricao`] ? 'invalid' : ''}
                      maxLength={500}
                      value={item.descricao}
                      onChange={(event) => updateItemField(index, 'descricao', event.target.value)}
                      placeholder="Ex.: notebook corporativo"
                    />
                    {itemErrors[`itens.${index}.descricao`] && (
                      <span className="lite-field-error">
                        {itemErrors[`itens.${index}.descricao`]}
                      </span>
                    )}
                  </label>
                  <div className="lite-form-grid two">
                    <label>
                      Quantidade
                      <input
                        className={itemErrors[`itens.${index}.quantidade`] ? 'invalid' : ''}
                        min="0"
                        type="number"
                        value={item.quantidade}
                        onChange={(event) => updateItemField(index, 'quantidade', event.target.value)}
                        placeholder="Ex.: 10"
                      />
                      {itemErrors[`itens.${index}.quantidade`] && (
                        <span className="lite-field-error">
                          {itemErrors[`itens.${index}.quantidade`]}
                        </span>
                      )}
                    </label>
                    <label>
                      Unidade
                      <input
                        className={itemErrors[`itens.${index}.unidade_medida`] ? 'invalid' : ''}
                        maxLength={60}
                        value={item.unidade_medida}
                        onChange={(event) =>
                          updateItemField(index, 'unidade_medida', event.target.value)
                        }
                        placeholder="Ex.: unidade"
                      />
                      {itemErrors[`itens.${index}.unidade_medida`] && (
                        <span className="lite-field-error">
                          {itemErrors[`itens.${index}.unidade_medida`]}
                        </span>
                      )}
                    </label>
                  </div>
                  <label>
                    Observacoes tecnicas do item
                    <input
                      maxLength={1000}
                      value={item.observacoes ?? ''}
                      onChange={(event) => updateItemField(index, 'observacoes', event.target.value)}
                      placeholder="Caracteristicas, restricoes ou detalhes tecnicos"
                    />
                  </label>
                </div>
              ))}
            </div>

            <label>
              Observacoes complementares
              <textarea
                maxLength={4000}
                value={form.observacoes ?? ''}
                onChange={(event) => updateField('observacoes', event.target.value)}
                placeholder="Inclua pontos de atencao, restricoes ou informacoes complementares"
              />
            </label>

            <div className="lite-form-actions">
              <button type="submit" className="lite-primary-button" disabled={saving}>
                {saving ? 'Salvando processo...' : 'Salvar processo'}
              </button>
              <button
                type="button"
                className="lite-secondary-button"
                onClick={handleGerarDocumento}
                disabled={generating}
              >
                {generating ? 'Gerando minuta...' : 'Gerar minuta'}
              </button>
              {hasErrors && <span className="lite-action-hint">Complete os campos destacados para avancar.</span>}
            </div>
          </form>
        </section>
      </main>
    </div>
  )
}
