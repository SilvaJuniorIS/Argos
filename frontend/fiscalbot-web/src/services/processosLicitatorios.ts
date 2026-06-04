import api from './api'

export type TipoDocumento = 'ETP' | 'TR'

export type ProcessoLicitatorio = {
  id: number
  objeto: string
  secretaria: string
  justificativa: string
  quantidade?: string | number | null
  unidade_medida?: string | null
  modalidade?: string | null
  prazo_execucao?: string | null
  observacoes?: string | null
  tipo_documento: TipoDocumento
  itens: ProcessoLicitatorioItem[]
  created_at: string
  updated_at: string
}

export type ProcessoLicitatorioItem = {
  id?: number
  ordem?: number
  descricao: string
  quantidade: string | number
  unidade_medida: string
  observacoes?: string | null
}

export type ProcessoLicitatorioPayload = {
  objeto: string
  secretaria: string
  justificativa: string
  quantidade?: string | number | null
  unidade_medida?: string | null
  modalidade?: string | null
  prazo_execucao?: string | null
  observacoes?: string | null
  tipo_documento: TipoDocumento
  itens?: ProcessoLicitatorioItem[]
}

export type ProcessoDashboardStatus = 'Rascunho' | 'Gerado' | 'Revisado'

export type ProcessoDashboardItem = {
  id: number
  objeto: string
  secretaria: string
  tipo_documento: TipoDocumento
  modalidade?: string | null
  created_at: string
  status: ProcessoDashboardStatus
  total_documentos: number
}

export type ProcessoDashboard = {
  total_processos: number
  total_documentos_gerados: number
  total_rascunho: number
  total_gerado: number
  total_revisado: number
  por_status: Array<{ status: ProcessoDashboardStatus; total: number }>
  ultimos_processos: ProcessoDashboardItem[]
}

const endpoint = '/api/v1/processos-licitatorios/'

export async function listarProcessosLicitatorios() {
  const { data } = await api.get<ProcessoLicitatorio[]>(endpoint)
  return data
}

export async function obterDashboardProcessosLicitatorios() {
  const { data } = await api.get<ProcessoDashboard>(`${endpoint}dashboard`)
  return data
}

export async function criarProcessoLicitatorio(payload: ProcessoLicitatorioPayload) {
  const { data } = await api.post<ProcessoLicitatorio>(endpoint, payload)
  return data
}
