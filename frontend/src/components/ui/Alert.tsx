interface AlertProps {
  message: string | null
  onClose?: () => void
}

// Reemplaza los alert() del navegador: el error queda visible en la página y se puede cerrar
export default function Alert({ message, onClose }: AlertProps) {
  if (!message) return null
  return (
    <div role="alert" className="flex items-start justify-between gap-4 rounded-lg border border-adan-danger/50 bg-adan-danger/10 px-4 py-3 text-sm text-red-300">
      <span>{message}</span>
      {onClose && (
        <button type="button" onClick={onClose} aria-label="Cerrar" className="text-red-300 hover:text-white">×</button>
      )}
    </div>
  )
}
