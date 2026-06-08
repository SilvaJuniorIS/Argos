import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import ConfirmModal from '../components/ui/ConfirmModal'
import { useAuth } from '../hooks/useAuth'
import { useToast } from '../hooks/useToast'
import { deleteContract, fetchContract } from '../services/contracts'
import { deleteDocumento, downloadDocumento, listDocumentos, uploadDocumento } from '../services/documentos'
import { createOcorrencia, listOcorrencias, updateOcorrenciaStatus } from '../services/fiscalizacao'
import type { Anexo, Contract, Ocorrencia } from '../types'

const labels: Record<keyof Contract, string> = {
  id: 'ID',
  tipo_instrumento: 'Tipo',
  status: 'Status',
  numero_contrato: 'Contrato',
  numero_aditivo: 'Aditivo',
  fornecedor: 'Fornecedor',
  cnpj: 'CNPJ',
  secretaria: 'Secretaria',
  secretario: 'Secretario',
  gestor: 'Gestor',
  gestor_cpf: 'CPF do gestor',
  fiscal: 'Fiscal',
  fiscal_cpf: 'CPF do fiscal',
  objeto: 'Objeto',
  vigencia_texto: 'Vigencia original',
  inicio_vigencia: 'Inicio da vigencia',
  fim_vigencia: 'Fim da vigencia',
  data_os: 'Data OS',
  processo_administrativo: 'Processo administrativo',
  processo_execucao: 'Processo de execucao',
  audesp_licitacao: 'Audesp licitacao',
  audesp_ajuste: 'Audesp ajuste',
  modalidade: 'Modalidade',
  valor_total: 'Valor total',
  data_assinatura: 'Data de assinatura',
  data_publicacao: 'Data de publicacao',
  observacao: 'Observacao',
  dias_para_vencimento: 'Dias para vencimento',
  alerta_30: 'Alerta 30',
  alerta_15: 'Alerta 15',
  alerta_07: 'Alerta 7',
  alerta_01: 'Alerta 1',
  created_at: 'Criado em',
  updated_at: 'Atualizado em',
}

export default function ContratoDetalhe() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { hasRole } = useAuth()
  const { showToast, ToastView } = useToast()
  const [contract, setContract] = useState<Contract | null>(null)
  const [documentos, setDocumentos] = useState<Anexo[]>([])
  const [documentoFile, setDocumentoFile] = useState<File | null>(null)
  const [documentoTipo, setDocumentoTipo] = useState('contrato')
  const [documentoVersao, setDocumentoVersao] = useState(1)
  const [ocorrencias, setOcorrencias] = useState<Ocorrencia[]>([])
  const [ocorrenciaTipo, setOcorrenciaTipo] = useState('vistoria')
  const [ocorrenciaTitulo, setOcorrenciaTitulo] = useState('')
  const [ocorrenciaDescricao, setOcorrenciaDescricao] = useState('')
  const [ocorrenciaPlano, setOcorrenciaPlano] = useState('')
  const [uploadingDocumento, setUploadingDocumento] = useState(false)
  const [savingOcorrencia, setSavingOcorrencia] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    if (!id) return
    const contratoId = Number(id)
    fetchContract(contratoId).then(setContract)
    listDocumentos(contratoId).then(setDocumentos)
    listOcorrencias(contratoId).then(setOcorrencias)
  }, [id])

  if (!contract) return <p className="text-slate-600">Carregando...</p>

  async function onDelete() {
    if (!contract) return
    setDeleting(true)
    try {
      await deleteContract(contract.id)
      showToast('success', 'Contrato excluido.')
      navigate('/contratos')
    } catch {
      showToast('error', 'Nao foi possivel excluir o contrato.')
      setDeleting(false)
      setConfirmDelete(false)
    }
  }

  async function onUploadDocumento() {
    if (!id || !documentoFile) {
      showToast('error', 'Selecione um arquivo para anexar.')
      return
    }
    setUploadingDocumento(true)
    try {
      const novo = await uploadDocumento(Number(id), documentoFile, documentoTipo, documentoVersao)
      setDocumentos((atuais) => [novo, ...atuais])
      setDocumentoFile(null)
      setDocumentoVersao(1)
      showToast('success', 'Arquivo anexado ao registro.')
    } catch {
      showToast('error', 'Nao foi possivel anexar o arquivo.')
    } finally {
      setUploadingDocumento(false)
    }
  }

  async function onDeleteDocumento(anexoId: number) {
    try {
      await deleteDocumento(anexoId, 'contratos')
      setDocumentos((atuais) => atuais.filter((item) => item.id !== anexoId))
      showToast('success', 'Arquivo removido.')
    } catch {
      showToast('error', 'Nao foi possivel remover o arquivo.')
    }
  }

  async function onCreateOcorrencia() {
    if (!id || !ocorrenciaTitulo.trim() || !ocorrenciaDescricao.trim()) {
      showToast('error', 'Informe titulo e descricao da ocorrencia.')
      return
    }
    setSavingOcorrencia(true)
    try {
      const nova = await createOcorrencia(Number(id), {
        tipo: ocorrenciaTipo,
        titulo: ocorrenciaTitulo.trim(),
        descricao: ocorrenciaDescricao.trim(),
        plano_acao: ocorrenciaPlano.trim() || null,
      })
      setOcorrencias((atuais) => [nova, ...atuais])
      setOcorrenciaTitulo('')
      setOcorrenciaDescricao('')
      setOcorrenciaPlano('')
      showToast('success', 'Ocorrencia registrada.')
    } catch {
      showToast('error', 'Nao foi possivel registrar a ocorrencia.')
    } finally {
      setSavingOcorrencia(false)
    }
  }

  async function onResolveOcorrencia(ocorrenciaId: number) {
    try {
      const atualizada = await updateOcorrenciaStatus(ocorrenciaId, 'resolvida')
      setOcorrencias((atuais) =>
        atuais.map((item) => (item.id === ocorrenciaId ? atualizada : item)),
      )
      showToast('success', 'Ocorrencia resolvida.')
    } catch {
      showToast('error', 'Nao foi possivel resolver a ocorrencia.')
    }
  }

  return (
    <div className="space-y-6">
      <ToastView />
      <Link to="/contratos" className="text-sm text-[#1D4ED8] hover:underline">
        &larr; Voltar
      </Link>

      <section className="rounded-lg border border-slate-200 bg-white p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-semibold">{contract.numero_contrato || 'Contrato'}</h1>
            <Badge label={contract.status || 'sem_status'} />
          </div>
          <div className="flex gap-2">
            {hasRole('admin', 'gestor') && (
              <Link to={`/contratos/${contract.id}/editar`}>
                <Button type="button" variant="ghost">Editar</Button>
              </Link>
            )}
            <Button type="button" variant="ghost" onClick={() => window.print()}>
              Exportar PDF
            </Button>
            {hasRole('admin') && (
              <Button type="button" variant="danger" onClick={() => setConfirmDelete(true)}>
                Excluir
              </Button>
            )}
          </div>
        </div>
        <p className="mt-3 text-slate-700">{contract.objeto}</p>
      </section>

      <section className="space-y-4 rounded-lg border border-slate-200 bg-white p-6">
        <div>
          <h2 className="text-lg font-semibold">Arquivos do registro</h2>
          <p className="text-sm text-slate-600">Contrato, AFs, aditamentos, notas, fotos e documentos relacionados.</p>
        </div>

        {hasRole('admin', 'gestor') && (
          <div className="grid gap-3 lg:grid-cols-[1fr_180px_120px_auto]">
            <input
              className="input"
              type="file"
              accept=".pdf,.jpg,.jpeg,.png,.zip,.doc,.docx,.xls,.xlsx,.odt"
              onChange={(event) => setDocumentoFile(event.target.files?.[0] || null)}
            />
            <select className="input" value={documentoTipo} onChange={(event) => setDocumentoTipo(event.target.value)}>
              <option value="contrato">Contrato</option>
              <option value="af">AF</option>
              <option value="aditivo">Aditamento</option>
              <option value="nota_fiscal">Nota fiscal</option>
              <option value="relatorio">Relatorio</option>
              <option value="foto">Foto</option>
              <option value="outro">Outro</option>
            </select>
            <input
              className="input"
              type="number"
              min={1}
              value={documentoVersao}
              onChange={(event) => setDocumentoVersao(Number(event.target.value) || 1)}
            />
            <Button type="button" onClick={onUploadDocumento} disabled={uploadingDocumento}>
              {uploadingDocumento ? 'Anexando...' : 'Anexar'}
            </Button>
          </div>
        )}

        <div className="overflow-x-auto rounded-lg border border-slate-200">
          <table className="w-full min-w-[720px] text-sm">
            <thead className="bg-white text-slate-600">
              <tr>
                <th className="px-4 py-3 text-left">Arquivo</th>
                <th className="px-4 py-3 text-left">Tipo</th>
                <th className="px-4 py-3 text-left">Versao</th>
                <th className="px-4 py-3 text-left">Enviado em</th>
                <th className="px-4 py-3 text-right">Acoes</th>
              </tr>
            </thead>
            <tbody>
              {documentos.map((documento) => (
                <tr key={documento.id} className="border-t border-slate-200">
                  <td className="px-4 py-3 text-slate-800">{documento.nome_arquivo}</td>
                  <td className="px-4 py-3 text-slate-700">{documento.tipo}</td>
                  <td className="px-4 py-3 text-slate-700">{documento.versao}</td>
                  <td className="px-4 py-3 text-slate-600">
                    {new Date(documento.created_at).toLocaleString('pt-BR')}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end gap-2">
                      <Button type="button" variant="ghost" onClick={() => downloadDocumento(documento, 'contratos')}>
                        Baixar
                      </Button>
                      {hasRole('admin', 'gestor') && (
                        <Button type="button" variant="danger" onClick={() => onDeleteDocumento(documento.id)}>
                          Remover
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {documentos.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                    Nenhum arquivo anexado a este registro.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-4 rounded-lg border border-slate-200 bg-white p-6">
        <div>
          <h2 className="text-lg font-semibold">Fiscalizacao</h2>
          <p className="text-sm text-slate-600">
            Registre vistorias, notificacoes, pendencias e planos de acao deste contrato.
          </p>
        </div>

        {hasRole('admin', 'gestor', 'fiscal') && (
          <div className="grid gap-3 lg:grid-cols-[180px_1fr]">
            <select
              className="input"
              value={ocorrenciaTipo}
              onChange={(event) => setOcorrenciaTipo(event.target.value)}
            >
              <option value="vistoria">Vistoria</option>
              <option value="notificacao">Notificacao</option>
              <option value="pendencia">Pendencia</option>
              <option value="aceite_parcial">Aceite parcial</option>
            </select>
            <input
              className="input"
              placeholder="Titulo da ocorrencia"
              value={ocorrenciaTitulo}
              onChange={(event) => setOcorrenciaTitulo(event.target.value)}
            />
            <textarea
              className="input min-h-24 lg:col-span-2"
              placeholder="Descricao"
              value={ocorrenciaDescricao}
              onChange={(event) => setOcorrenciaDescricao(event.target.value)}
            />
            <textarea
              className="input min-h-20 lg:col-span-2"
              placeholder="Plano de acao ou providencias"
              value={ocorrenciaPlano}
              onChange={(event) => setOcorrenciaPlano(event.target.value)}
            />
            <div className="lg:col-span-2">
              <Button type="button" onClick={onCreateOcorrencia} disabled={savingOcorrencia}>
                {savingOcorrencia ? 'Registrando...' : 'Registrar ocorrencia'}
              </Button>
            </div>
          </div>
        )}

        <div className="space-y-3">
          {ocorrencias.map((ocorrencia) => (
            <div key={ocorrencia.id} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="flex flex-wrap gap-2">
                    <Badge label={ocorrencia.tipo || 'ocorrencia'} />
                    <Badge label={ocorrencia.status} />
                  </div>
                  <h3 className="mt-2 font-medium">{ocorrencia.titulo}</h3>
                  <p className="text-sm text-slate-600">{ocorrencia.descricao}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    {new Date(`${ocorrencia.data_ocorrencia}T00:00:00`).toLocaleDateString('pt-BR')}
                  </p>
                </div>
                {hasRole('admin', 'gestor') && ocorrencia.status !== 'resolvida' && (
                  <Button type="button" variant="ghost" onClick={() => onResolveOcorrencia(ocorrencia.id)}>
                    Resolver
                  </Button>
                )}
              </div>
            </div>
          ))}
          {ocorrencias.length === 0 && (
            <div className="rounded-lg border border-slate-200 p-4 text-sm text-slate-500">
              Nenhuma ocorrencia registrada para este contrato.
            </div>
          )}
        </div>
      </section>

      <section className="grid gap-3 md:grid-cols-2">
        {(Object.keys(labels) as (keyof Contract)[]).map((key) => (
          <div key={key} className="rounded-lg border border-slate-200 bg-white p-4">
            <p className="text-xs uppercase text-slate-500">{labels[key]}</p>
            <p className="mt-1 break-words text-sm text-slate-800">{String(contract[key] ?? '-')}</p>
          </div>
        ))}
      </section>

      <ConfirmModal
        open={confirmDelete}
        title="Excluir contrato"
        message={`Confirma a exclusao do contrato ${contract.numero_contrato || contract.id}?`}
        confirmLabel="Excluir"
        loading={deleting}
        onConfirm={onDelete}
        onClose={() => setConfirmDelete(false)}
      />
    </div>
  )
}

