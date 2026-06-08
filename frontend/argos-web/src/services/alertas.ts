import api from './api'
import type { Alerta, AlertaGeracaoResultado, AlertaResumo } from '../types'

export async function fetchAlertas(params?: {
  lido?: boolean
  resolvido?: boolean
  limit?: number
  offset?: number
}) {
  const { data } = await api.get<Alerta[]>('/api/v1/alertas', { params })
  return data
}

export async function fetchResumo() {
  const { data } = await api.get<AlertaResumo>('/api/v1/alertas/resumo')
  return data
}

export async function marcarLido(id: number) {
  await api.put(`/api/v1/alertas/${id}/lido`)
}

export async function resolver(id: number) {
  await api.put(`/api/v1/alertas/${id}/resolver`)
}

export async function gerarAlertas() {
  const { data } = await api.post<AlertaGeracaoResultado>('/api/v1/alertas/gerar')
  return data
}
