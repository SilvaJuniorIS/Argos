import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate } from 'react-router-dom'
import Button from '../components/ui/Button'
import { useAuth } from '../hooks/useAuth'

export default function Login() {
  const { login, isAuthenticated } = useAuth()
  const [email, setEmail] = useState('admin@argos.gov.br')
  const [password, setPassword] = useState('argos123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (isAuthenticated) return <Navigate to="/dashboard" replace />

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await login(email, password)
    } catch {
      setError('Credenciais invalidas')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#F5F7FA] p-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-xl"
      >
        <h1 className="text-2xl font-bold text-[#0A2342]">ARGOS</h1>
        <p className="mt-1 text-sm text-slate-600">Fiscalizacao inteligente, clara e segura.</p>
        <div className="mt-6 space-y-3">
          <input
            className="input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="E-mail"
          />
          <input
            type="password"
            className="input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Senha"
          />
        </div>
        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
        <Button type="submit" disabled={loading} className="mt-4 w-full">
          {loading ? 'Entrando...' : 'Entrar'}
        </Button>
        <p className="mt-4 text-center text-xs text-slate-500">
          Ambiente de teste: admin@argos.gov.br / argos123
        </p>
        <Link to="/vitrine" className="mt-3 block text-center text-xs text-[#1D4ED8] hover:underline">
          Conhecer a vitrine do produto
        </Link>
      </form>
    </div>
  )
}

