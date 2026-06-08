import { lazy, Suspense } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

const DocumentoEditorLite = lazy(() => import('./pages/DocumentoEditorLite'))
const Argos = lazy(() => import('./pages/Argos'))
const Institucional = lazy(() => import('./pages/Institucional'))
const Login = lazy(() => import('./pages/Login'))
const NovoProcessoLite = lazy(() => import('./pages/NovoProcessoLite'))
const Vitrine = lazy(() => import('./pages/Vitrine'))

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div className="app-loading">Carregando ARGOS...</div>}>
        <Routes>
          <Route path="/argos" element={<Argos />} />
          <Route path="/argos/processos/novo" element={<NovoProcessoLite />} />
          <Route path="/argos/processos/:id" element={<NovoProcessoLite />} />
          <Route path="/argos/institucional" element={<Institucional />} />
          <Route path="/argos/documentos/:id" element={<DocumentoEditorLite />} />
          <Route path="/lite" element={<Argos />} />
          <Route path="/lite/processos/novo" element={<NovoProcessoLite />} />
          <Route path="/lite/documentos/:id" element={<DocumentoEditorLite />} />
          <Route path="/" element={<Vitrine />} />
          <Route path="/vitrine" element={<Vitrine />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Navigate to="/argos" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
