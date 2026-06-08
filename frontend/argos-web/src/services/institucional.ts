import api from './api'

export type InstitucionalConfig = {
  id: number
  nome_orgao: string
  nome_municipio?: string | null
  uf?: string | null
  cnpj?: string | null
  endereco?: string | null
  telefone?: string | null
  email?: string | null
  site?: string | null
  autoridade_nome?: string | null
  autoridade_cargo?: string | null
  responsavel_tecnico?: string | null
  rodape_documentos?: string | null
  logo_base64?: string | null
  created_at: string
  updated_at: string
}

export type InstitucionalPayload = Omit<InstitucionalConfig, 'id' | 'created_at' | 'updated_at'>

export async function obterInstitucional() {
  const { data } = await api.get<InstitucionalConfig>('/api/v1/institucional')
  return data
}

export async function salvarInstitucional(payload: InstitucionalPayload) {
  const { data } = await api.put<InstitucionalConfig>('/api/v1/institucional', payload)
  return data
}
