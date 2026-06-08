import { lazy, Suspense } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/layout/Layout'
import { useAuth } from './hooks/useAuth'

const Alertas = lazy(() => import('./pages/Alertas'))
const ContratoDetalhe = lazy(() => import('./pages/ContratoDetalhe'))
const ContratoForm = lazy(() => import('./pages/ContratoForm'))
const Contratos = lazy(() => import('./pages/Contratos'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const DocumentoEditorLite = lazy(() => import('./pages/DocumentoEditorLite'))
const Fiscalizacao = lazy(() => import('./pages/Fiscalizacao'))
const Argos = lazy(() => import('./pages/Argos'))
const ImportacaoContratos = lazy(() => import('./pages/ImportacaoContratos'))
const Login = lazy(() => import('./pages/Login'))
const NovoProcessoLite = lazy(() => import('./pages/NovoProcessoLite'))
const Vitrine = lazy(() => import('./pages/Vitrine'))

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <Layout>{children}</Layout>
}

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div className="app-loading">Carregando ARGOS...</div>}>
        <Routes>
          <Route path="/argos" element={<Argos />} />
          <Route path="/argos/processos/novo" element={<NovoProcessoLite />} />
          <Route path="/argos/documentos/:id" element={<DocumentoEditorLite />} />
          <Route path="/lite" element={<Argos />} />
          <Route path="/lite/processos/novo" element={<NovoProcessoLite />} />
          <Route path="/lite/documentos/:id" element={<DocumentoEditorLite />} />
          <Route path="/" element={<Vitrine />} />
          <Route path="/vitrine" element={<Vitrine />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/contratos"
            element={
              <PrivateRoute>
                <Contratos />
              </PrivateRoute>
            }
          />
          <Route
            path="/atas"
            element={
              <PrivateRoute>
                <Contratos />
              </PrivateRoute>
            }
          />
          <Route
            path="/contratos/novo"
            element={
              <PrivateRoute>
                <ContratoForm />
              </PrivateRoute>
            }
          />
          <Route
            path="/contratos/:id/editar"
            element={
              <PrivateRoute>
                <ContratoForm />
              </PrivateRoute>
            }
          />
          <Route
            path="/contratos/:id"
            element={
              <PrivateRoute>
                <ContratoDetalhe />
              </PrivateRoute>
            }
          />
          <Route
            path="/importacao/contratos"
            element={
              <PrivateRoute>
                <ImportacaoContratos />
              </PrivateRoute>
            }
          />
          <Route
            path="/alertas"
            element={
              <PrivateRoute>
                <Alertas />
              </PrivateRoute>
            }
          />
          <Route
            path="/fiscalizacao"
            element={
              <PrivateRoute>
                <Fiscalizacao />
              </PrivateRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
