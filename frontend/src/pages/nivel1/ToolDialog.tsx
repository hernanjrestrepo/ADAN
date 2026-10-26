import { useState, type FormEvent } from 'react'
import Button from '../../components/ui/Button'

// Pedirle al equipo un recorrido con clics por una página (con la cuenta del fundador si hace falta) o la revisión del
// código del producto en GitHub. Usuario, clave y token se usan solo para esa tarea: no se guardan en ADÁN.

export type Tool = 'recorrido' | 'repositorio'

const FIELD = 'w-full rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm'

export default function ToolDialog({ tool, onCancel, onStart }: {
  tool: Tool
  onCancel: () => void
  onStart: (tool: Tool, data: Record<string, string>) => void
}) {
  const [data, setData] = useState<Record<string, string>>({})
  const set = (k: string) => (e: { target: { value: string } }) => setData((d) => ({ ...d, [k]: e.target.value }))
  const walk = tool === 'recorrido'
  const ready = walk ? (data.url ?? '').trim().length > 3 && (data.objetivo ?? '').trim().length > 2
    : /github\.com\/[\w.-]+\/[\w.-]+/i.test(data.url ?? '')
  const submit = (e: FormEvent) => {
    e.preventDefault()
    if (ready) onStart(tool, Object.fromEntries(Object.entries(data).map(([k, v]) => [k, v.trim()])))
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/60 p-3" role="dialog"
      aria-label={walk ? 'Recorrer una página' : 'Revisar código'}>
      <form onSubmit={submit} className="mt-10 w-full max-w-lg space-y-3 rounded-2xl border border-adan-border bg-adan-bg p-5">
        <div className="flex items-center justify-between">
          <p className="text-lg font-bold">{walk ? '🧭 Recorrer una página' : '💻 Revisar código'}</p>
          <button type="button" onClick={onCancel} aria-label="Cerrar" className="text-adan-muted hover:text-adan-text">✕</button>
        </div>
        <p className="text-sm text-adan-muted">
          {walk
            ? 'Andrés abre la página en un navegador real y hace clics como un usuario hasta cumplir el objetivo. Nunca paga ni escribe datos de tarjeta: se detiene en la pantalla de pago y te la describe.'
            : 'Mateo, el CTO, lee el repositorio (estructura, archivos clave, pagos, datos, seguridad) y te deja su revisión en la Sala y en la Biblioteca.'}
        </p>
        <label className="block text-sm">
          {walk ? 'Dirección de la página' : 'Enlace del repositorio de GitHub'}
          <input value={data.url ?? ''} onChange={set('url')} className={FIELD} autoFocus
            placeholder={walk ? 'https://xmartravel.com' : 'https://github.com/usuario/repositorio'} />
        </label>
        <label className="block text-sm">
          {walk ? 'Objetivo del recorrido' : 'Qué revisar (opcional)'}
          <input value={data.objetivo ?? ''} onChange={set('objetivo')} className={FIELD}
            placeholder={walk ? 'Pedirle a Aura un viaje a Cartagena y llegar hasta el pago' : 'El flujo de pago con Wompi y la seguridad'} />
        </label>
        {walk ? (
          <details className="text-sm">
            <summary className="cursor-pointer text-adan-muted">¿La página pide iniciar sesión? Dale una cuenta de prueba</summary>
            <div className="mt-2 grid gap-2 sm:grid-cols-2">
              <input value={data.usuario ?? ''} onChange={set('usuario')} className={FIELD} placeholder="Usuario o correo" autoComplete="off" />
              <input value={data.clave ?? ''} onChange={set('clave')} className={FIELD} placeholder="Clave" type="password" autoComplete="new-password" />
            </div>
            <p className="mt-1 text-xs text-adan-muted">Usa una cuenta de prueba. La clave solo se escribe en el navegador de este recorrido: no se guarda ni la ve la IA.</p>
          </details>
        ) : (
          <label className="block text-sm">
            Token de solo lectura (solo si el repositorio es privado)
            <input value={data.token ?? ''} onChange={set('token')} className={FIELD} type="password" autoComplete="off"
              placeholder="github_pat_…" />
            <span className="mt-1 block text-xs text-adan-muted">Crea un «fine-grained token» con permiso de solo lectura de contenido para ese repositorio. Se usa para esta revisión y no se guarda.</span>
          </label>
        )}
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onCancel}>Cancelar</Button>
          <Button type="submit" disabled={!ready}>{walk ? 'Recorrer' : 'Revisar'}</Button>
        </div>
      </form>
    </div>
  )
}
