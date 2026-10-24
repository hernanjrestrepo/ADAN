import { useEffect } from 'react'
import { levelOf, useUniverso } from './store'

// Demo automática para presentar: encarga las tareas, convoca al Board, aprueba y sigue hasta el Nivel 7
export function useAutopilot(enabled: boolean, onFinish: () => void): void {
  useEffect(() => {
    if (!enabled) return
    const tick = window.setInterval(() => {
      const s = useUniverso.getState()
      if (!s.started) return
      if (s.celebration !== null) {
        if (s.closedLevels.includes(7)) {
          s.closeCelebration()
          onFinish()
        } else s.closeCelebration()
        return
      }
      if (s.report !== null) return
      if (s.board) {
        if (s.board.phase === 'decided') s.approveLevel()
        return
      }
      if (s.closedLevels.includes(s.level)) {
        onFinish()
        return
      }
      const level = levelOf(s.level)
      const pending = level.tasks.filter((t) => !s.doneTasks.includes(t.id))
      const free = pending.find((t) => !s.jobs[t.agent])
      if (free && Object.keys(s.jobs).length < 2) {
        s.assign(free.id)
        s.focus(free.zone)
      } else if (pending.length === 0 && Object.keys(s.jobs).length === 0) {
        s.convene()
      }
    }, 2600)
    return () => window.clearInterval(tick)
  }, [enabled, onFinish])
}
