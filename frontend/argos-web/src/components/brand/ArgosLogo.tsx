type ArgosLogoProps = {
  compact?: boolean
  className?: string
}

export default function ArgosLogo({ compact = false, className = '' }: ArgosLogoProps) {
  return (
    <div className={`argos-logo ${compact ? 'compact' : ''} ${className}`.trim()} aria-label="ARGOS">
      <svg viewBox="0 0 96 96" role="img" aria-hidden="true">
        <defs>
          <linearGradient id="argos-gold" x1="22" y1="12" x2="74" y2="84" gradientUnits="userSpaceOnUse">
            <stop stopColor="#FDE68A" />
            <stop offset="0.48" stopColor="#F59E0B" />
            <stop offset="1" stopColor="#8A5A08" />
          </linearGradient>
          <filter id="argos-shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="8" stdDeviation="5" floodColor="#020617" floodOpacity="0.35" />
          </filter>
        </defs>
        <circle cx="48" cy="48" r="37" fill="none" stroke="#F59E0B" strokeWidth="1.8" opacity="0.58" />
        <path
          d="M22 71 48 14l26 57-12-7-14-31-14 31-12 7Z"
          fill="url(#argos-gold)"
          filter="url(#argos-shadow)"
        />
        <path
          d="M17 57c8-11 19-17 31-17s23 6 31 17c-8 11-19 17-31 17S25 68 17 57Z"
          fill="#07182D"
          stroke="url(#argos-gold)"
          strokeWidth="5"
          strokeLinejoin="round"
          filter="url(#argos-shadow)"
        />
        <circle cx="48" cy="57" r="13" fill="#07182D" stroke="url(#argos-gold)" strokeWidth="5" />
        <circle cx="54" cy="50" r="4.2" fill="#FFFFFF" />
        <circle cx="48" cy="10" r="3.4" fill="#FDE68A" />
        <circle cx="24" cy="25" r="3.2" fill="#F8C873" />
        <circle cx="72" cy="25" r="3.2" fill="#F8C873" />
      </svg>
      {!compact && (
        <span>
          <strong>ARGOS</strong>
          <small>Inteligencia documental</small>
        </span>
      )}
    </div>
  )
}
