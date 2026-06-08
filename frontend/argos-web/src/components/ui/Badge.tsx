const colors: Record<string, string> = {
  ativo: 'bg-green-50 text-green-700 ring-green-200',
  alerta: 'bg-amber-50 text-amber-700 ring-amber-200',
  critico: 'bg-red-50 text-red-700 ring-red-200',
  encerrado: 'bg-slate-100 text-slate-600 ring-slate-200',
  pendente: 'bg-orange-50 text-orange-700 ring-orange-200',
  lido: 'bg-slate-100 text-slate-600 ring-slate-200',
  resolvido: 'bg-green-50 text-green-700 ring-green-200',
}

export default function Badge({ label }: { label: string }) {
  const cls = colors[label] || 'bg-blue-50 text-blue-700 ring-blue-200'
  return (
    <span className={`inline-block rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${cls}`}>
      {label}
    </span>
  )
}
