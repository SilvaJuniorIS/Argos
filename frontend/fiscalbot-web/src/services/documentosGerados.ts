import api from './api'
import { TipoDocumento } from './processosLicitatorios'

export type DocumentoGerado = {
  id: number
  processo_id: number
  tipo_documento: string
  modelo: string
  conteudo: string
  created_at: string
  revisado_em?: string | null
}

export async function gerarDocumento(processoId: number, tipoDocumento?: TipoDocumento) {
  const { data } = await api.post<DocumentoGerado>('/api/v1/documentos/gerar', {
    processo_id: processoId,
    tipo_documento: tipoDocumento,
  })
  return data
}

export async function obterDocumentoGerado(documentoId: number) {
  const { data } = await api.get<DocumentoGerado>(`/api/v1/documentos/gerados/${documentoId}`)
  return data
}

export async function atualizarDocumentoGerado(documentoId: number, conteudo: string) {
  const { data } = await api.patch<DocumentoGerado>(`/api/v1/documentos/gerados/${documentoId}`, {
    conteudo,
  })
  return data
}

export async function exportarDocumentoGeradoDocx(documentoId: number) {
  const response = await api.get<Blob>(`/api/v1/documentos/gerados/${documentoId}/exportar-docx`, {
    responseType: 'blob',
  })
  return response.data
}
