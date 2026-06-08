import api from './api'
import type { Ocorrencia } from '../types'

export type OcorrenciaPayload = {
  tipo: string
  titulo: string
  descricao: string
  data_ocorrencia?: string
  plano_acao?: string | null
}

export async function listOcorrencias(contratoId: number) {
  const { data } = await api.get<Ocorrencia[]>(
    `/api/v1/fiscalizacao/contratos/${contratoId}/ocorrencias`,
  )
  return data
}

export async function createOcorrencia(contratoId: number, payload: OcorrenciaPayload) {
  const { data } = await api.post<Ocorrencia>(
    `/api/v1/fiscalizacao/contratos/${contratoId}/ocorrencias`,
    payload,
  )
  return data
}

export async function updateOcorrenciaStatus(id: number, status: string) {
  const { data } = await api.put<Ocorrencia>(`/api/v1/fiscalizacao/ocorrencias/${id}`, {
    status,
  })
  return data
}
