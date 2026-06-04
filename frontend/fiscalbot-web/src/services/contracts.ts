import api from './api'
import type {
  Contract,
  ContractDashboard,
  ContractImportResult,
  ContractListResult,
  Contrato,
  ContratoDashboard,
  ContratoListResult,
  ContratoPayload,
} from '../types'

function daysToExpiration(value: string) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const end = new Date(`${value}T00:00:00`)
  return Math.round((end.getTime() - today.getTime()) / 86400000)
}

function toContract(item: Contrato): Contract {
  return {
    id: item.id,
    tipo_instrumento: item.tipo_instrumento,
    status: item.status,
    numero_contrato: item.numero,
    fornecedor: item.fornecedor?.razao_social || String(item.fornecedor_id),
    cnpj: item.fornecedor?.cnpj || null,
    secretaria: item.secretaria?.nome || String(item.secretaria_id),
    gestor: item.gestor?.nome || null,
    fiscal: item.fiscal?.nome || null,
    objeto: item.objeto,
    inicio_vigencia: item.inicio,
    fim_vigencia: item.termino,
    valor_total: item.valor,
    observacao: item.tags || null,
    dias_para_vencimento: daysToExpiration(item.termino),
    alerta_30: false,
    alerta_15: false,
    alerta_07: false,
    alerta_01: false,
    created_at: '',
    updated_at: '',
  }
}

export async function importContracts(file: File) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<ContractImportResult>('/api/v1/contracts/import', form)
  return data
}

export async function fetchContracts(params?: Record<string, string | number | boolean | undefined>) {
  const { data } = await api.get<ContratoListResult>('/api/v1/contratos', {
    params: {
      tipo_instrumento: params?.tipo_instrumento,
      status: params?.status,
      vencendo_em_dias: params?.vencendo_em_30 ? 30 : undefined,
      page: params?.page,
      limit: params?.limit,
      formato: 'pagina',
      order_by: 'termino',
      order_dir: 'asc',
    },
  })
  return {
    items: data.items.map(toContract),
    total: data.total,
    page: data.page,
    limit: data.limit,
    pages: data.pages || Math.max(1, Math.ceil(data.total / data.limit)),
  } satisfies ContractListResult
}

export async function fetchContractsDashboard() {
  const { data } = await api.get<ContratoDashboard>('/api/v1/contratos/dashboard')
  return {
    contratos_ativos: data.ativos,
    vencendo_em_30: data.vencendo_30,
    vencendo_em_15: 0,
    vencidos: 0,
    valor_total_contratado: data.valor_total,
  } satisfies ContractDashboard
}

export async function fetchContract(id: string | number) {
  const { data } = await api.get<Contrato>(`/api/v1/contratos/${id}`)
  return toContract(data)
}

export async function updateContract(
  id: string | number,
  payload: Partial<ContratoPayload> | Partial<Contract>,
) {
  const { data } = await api.put<Contrato>(`/api/v1/contratos/${id}`, payload)
  return toContract(data)
}

export async function deleteContract(id: string | number) {
  await api.delete(`/api/v1/contratos/${id}`)
}

export async function downloadContractsExport(
  format: 'csv' | 'xlsx' | 'pdf',
  params?: Record<string, string | number | boolean | undefined>,
) {
  const { data } = await api.get<Blob>(`/api/v1/contracts/export/${format}`, {
    params,
    responseType: 'blob',
  })
  const url = URL.createObjectURL(data)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `contratos.${format}`
  anchor.click()
  URL.revokeObjectURL(url)
}
