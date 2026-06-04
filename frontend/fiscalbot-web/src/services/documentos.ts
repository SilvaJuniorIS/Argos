import api from './api'
import type { Anexo } from '../types'

export async function listDocumentos(contratoId: string | number) {
  const base = typeof contratoId === 'string' ? '/api/v1/contracts' : '/api/v1/contratos'
  const { data } = await api.get<Anexo[]>(`${base}/${contratoId}/documentos`)
  return data
}

export async function uploadDocumento(
  contratoId: string | number,
  file: File,
  tipo: string,
  versao?: number,
) {
  const form = new FormData()
  form.append('file', file)
  form.append('tipo', tipo)
  if (versao) form.append('versao', String(versao))
  const base = typeof contratoId === 'string' ? '/api/v1/contracts' : '/api/v1/contratos'
  const { data } = await api.post<Anexo>(`${base}/${contratoId}/documentos`, form)
  return data
}

export async function downloadDocumento(anexo: Anexo, origem: 'contracts' | 'contratos' = 'contracts') {
  const endpoint =
    origem === 'contracts'
      ? `/api/v1/contracts/documentos/${anexo.id}/download`
      : `/api/v1/documentos/${anexo.id}/download`
  const { data } = await api.get<Blob>(endpoint, { responseType: 'blob' })
  const url = URL.createObjectURL(data)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = anexo.nome_arquivo
  anchor.click()
  URL.revokeObjectURL(url)
}

export async function deleteDocumento(anexoId: number, origem: 'contracts' | 'contratos' = 'contracts') {
  const endpoint =
    origem === 'contracts'
      ? `/api/v1/contracts/documentos/${anexoId}`
      : `/api/v1/documentos/${anexoId}`
  await api.delete(endpoint)
}
