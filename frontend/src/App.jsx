import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './hooks/useAuth.jsx'
import ProtectedRoute from './components/auth/ProtectedRoute'
import Login from './components/auth/Login'
import Register from './components/auth/Register'
import Dashboard from './pages/Dashboard'
import Tournament from './pages/Tournament'
import Teams from './pages/Teams'
import Brackets from './pages/Brackets'
import Chat from './pages/Chat'

function AppRoutes() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-orange-500 border-t-transparent mx-auto mb-4"></div>
          <p className="text-orange-400 pixel-font">🎮 CARGANDO...</p>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      {/* Rutas públicas */}
      <Route 
        path="/login" 
        element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" replace />} 
      />
      <Route 
        path="/register" 
        element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" replace />} 
      />
      
      {/* Rutas protegidas */}
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      } />
      
      <Route path="/tournaments/:id" element={
        <ProtectedRoute>
          <Tournament />
        </ProtectedRoute>
      } />
      
      <Route path="/tournaments/:id/teams" element={
        <ProtectedRoute requireAdmin>
          <Teams />
        </ProtectedRoute>
      } />
      
      <Route path="/tournaments/:id/teams" element={
        <ProtectedRoute adminOnly>
          <Teams />
        </ProtectedRoute>
      } />
      
      <Route path="/tournaments/:id/brackets" element={
        <ProtectedRoute>
          <Brackets />
        </ProtectedRoute>
      } />
      
      <Route path="/tournaments/:id/chat" element={
        <ProtectedRoute>
          <Chat />
        </ProtectedRoute>
      } />
      
      {/* Redirección por defecto */}
      <Route 
        path="/" 
        element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} 
      />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-dark">
        <AppRoutes />
      </div>
    </AuthProvider>
  )
}

export default App
