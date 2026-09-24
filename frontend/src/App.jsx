import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { api } from './lib/api'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import Nivel1Page from './pages/Nivel1Page'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('adan_token')
    if (token) {
      api.setToken(token)
      api.getMe()
        .then(setUser)
        .catch(() => {
          api.logout()
          setUser(null)
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-adan-muted">Cargando...</div>
      </div>
    )
  }

  return (
    <Routes>
      <Route path="/login" element={
        user ? <Navigate to="/dashboard" /> : <LoginPage onLogin={setUser} />
      } />
      <Route path="/register" element={
        user ? <Navigate to="/dashboard" /> : <RegisterPage onRegister={setUser} />
      } />
      <Route path="/dashboard" element={
        user ? <DashboardPage user={user} /> : <Navigate to="/login" />
      } />
      <Route path="/nivel1/:companyId" element={
        user ? <Nivel1Page user={user} /> : <Navigate to="/login" />
      } />
      <Route path="*" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
    </Routes>
  )
}

export default App
