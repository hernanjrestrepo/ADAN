import { api } from './api'
import type { Message } from '../types'

// ADÁN responde de una vez y, si anunció una búsqueda en internet, los hallazgos llegan después en otro mensaje
export async function waitForResearch(companyId: string, afterId: string, timeoutMs = 150_000): Promise<Message[] | null> {
  const started = Date.now()
  while (Date.now() - started < timeoutMs) {
    await new Promise((r) => setTimeout(r, 5000))
    try {
      const status = await api.getNivel1Status(companyId)
      const i = status.messages.findIndex((m) => m.id === afterId)
      if (i >= 0 && status.messages.slice(i + 1).some((m) => m.role === 'assistant')) return status.messages
    } catch {
      // un fallo de red momentáneo no corta la espera
    }
  }
  return null
}
