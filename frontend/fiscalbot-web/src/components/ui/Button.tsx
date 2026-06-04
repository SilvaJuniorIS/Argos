import type { ButtonHTMLAttributes } from 'react'

export default function Button({
  variant = 'primary',
  className = '',
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'ghost' | 'danger' }) {
  const base =
    'rounded-lg px-4 py-2 text-sm font-semibold shadow-sm transition disabled:opacity-50 disabled:cursor-not-allowed'
  const variants = {
    primary: 'bg-[#1D4ED8] text-white hover:bg-[#163EA8]',
    ghost: 'border border-slate-300 bg-white text-[#0A2342] hover:bg-slate-50',
    danger: 'bg-red-600 text-white hover:bg-red-700',
  }
  return <button className={`${base} ${variants[variant]} ${className}`} {...props} />
}
