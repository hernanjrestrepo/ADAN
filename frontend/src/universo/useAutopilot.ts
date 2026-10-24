import { useEffect } from 'react'
import { levelOf, tasksOf, useUniverso } from './store'

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
      if (s.arena) {
        if (s.arena.phase === 'decided') {
          if (s.arena.passed) s.approveLevel()
          else s.leaveArena()
        }
        return
      }
      if (s.board) {
        if (s.board.phase !== 'decided') return
        if (s.board.recommendation === 'PROCEED') s.approveLevel()
        else s.dismissBoard()
        return
      }
      if (s.closedLevels.includes(s.level)) {
        onFinish()
        return
      }
      const level = levelOf(s.level)
      const pending = tasksOf(level, s.revealed).filter((t) => !s.doneTasks.includes(t.id))
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
