// Una captura pegada con Ctrl+V llega como imagen sin nombre: se le pone uno para cargarla como documento
export function pastedFiles(e: ClipboardEvent | React.ClipboardEvent): File[] {
  const items = Array.from(e.clipboardData?.items ?? [])
  return items
    .filter((it) => it.kind === 'file')
    .map((it, i) => {
      const f = it.getAsFile()
      if (!f) return null
      if (f.name && f.name !== 'image.png') return f
      const ext = (f.type.split('/')[1] || 'png').replace('jpeg', 'jpg')
      const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')
      return new File([f], `captura-${stamp}${i ? `-${i}` : ''}.${ext}`, { type: f.type })
    })
    .filter((f): f is File => f !== null)
}

export const FILE_ICON = (name: string) => /\.(png|jpe?g|webp|gif)$/i.test(name) ? '🖼️'
  : /\.(mp3|m4a|wav|ogg|opus|aac|flac|amr)$/i.test(name) ? '🎙️'
    : /\.(mp4|mov|webm|mkv|avi|3gp)$/i.test(name) ? '🎬' : '📄'
