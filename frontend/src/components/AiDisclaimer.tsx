// Aviso de IA (AD-DEC-0002, decisión 6): visible en todo momento. El mismo texto vive en
// backend/app/core/disclaimer.py.
export const AI_DISCLAIMER =
  'ADÁN es una inteligencia artificial. Sus análisis y recomendaciones no reemplazan ' +
  'la asesoría de profesionales (legal, tributaria, financiera u otra), y Paradixe no se ' +
  'hace responsable por los resultados de las decisiones que se tomen con base en ellos.'

export default function AiDisclaimer({ className = '' }: { className?: string }) {
  return (
    <p className={`text-xs text-adan-muted ${className}`}>
      ⚠️ {AI_DISCLAIMER}
    </p>
  )
}
