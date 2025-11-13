import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../hooks/useAuth.jsx'
import { tournamentAPI } from '../services/api'
import TeamManagement from '../components/team/TeamManagement'

export default function Teams() {
  const { id: tournamentId } = useParams()
  const { isAdmin, user, logout } = useAuth()

  const { data: tournament, isLoading } = useQuery({
    queryKey: ['tournament', tournamentId],
    queryFn: () => tournamentAPI.getById(tournamentId).then(res => res.data)
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-orange-500 border-t-transparent mx-auto mb-4"></div>
          <p className="text-orange-400 pixel-font">🎮 CARGANDO EQUIPOS...</p>
        </div>
      </div>
    )
  }

  if (!tournament) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-400 pixel-font mb-4">❌ TORNEO NO ENCONTRADO</h1>
          <Link to="/" className="text-orange-400 hover:text-orange-300 pixel-font">
            ← Volver al Dashboard
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header con información del usuario */}
      <header className="bg-slate-800/80 backdrop-blur-sm border-b-2 border-orange-500/30 p-4">
        <div className="container mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-yellow-400 pixel-font">
              🎮 TORNEO GAMING
            </h1>
            <p className="text-gray-300 text-sm mt-1">
              Bienvenido, {user?.profile?.first_name || user?.username} 
              <span className="ml-2 px-2 py-1 bg-orange-500/20 text-orange-300 rounded text-xs pixel-font">
                {isAdmin() ? '👑 ADMIN' : '🎯 JUGADOR'}
              </span>
            </p>
          </div>
          
          <button
            onClick={logout}
            className="bg-slate-700/50 hover:bg-red-600/50 border-2 border-slate-600 hover:border-red-500/50 text-gray-300 hover:text-red-400 font-semibold py-2 px-4 rounded-lg transition-all duration-200 pixel-font"
          >
            🚪 SALIR
          </button>
        </div>
      </header>

      {/* Header */}
      <header className="bg-slate-800/80 backdrop-blur-sm border-b-2 border-orange-500/30 p-4">
        <div className="container mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link 
                to={`/tournaments/${tournamentId}`}
                className="text-orange-400 hover:text-orange-300 transition-colors pixel-font flex items-center gap-2"
              >
                <span>←</span>
                <span>Volver al Torneo</span>
              </Link>
              <div className="h-6 w-px bg-orange-500/30"></div>
              <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-yellow-400 pixel-font">
                👥 GESTIÓN DE EQUIPOS
              </h1>
            </div>
            
            <div className="flex items-center gap-4">
              <Link
                to={`/tournaments/${tournamentId}/brackets`}
                className="bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 text-white font-bold py-2 px-4 rounded-lg transition-all duration-200 pixel-font flex items-center gap-2"
              >
                🏆 Ver Brackets
              </Link>
              <div className="text-right">
                <h2 className="text-lg font-bold text-orange-400 pixel-font">
                  {tournament.name}
                </h2>
                <p className="text-sm text-gray-400">
                  {tournament.max_teams} equipos máximo
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Contenido principal */}
      <main className="container mx-auto px-4 py-8">
        {isAdmin() ? (
          <TeamManagement tournamentId={tournamentId} />
        ) : (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">🚫</div>
            <h3 className="text-2xl font-bold text-gray-400 mb-2 pixel-font">
              ACCESO RESTRINGIDO
            </h3>
            <p className="text-gray-500 mb-6">
              Solo los administradores pueden gestionar equipos
            </p>
            <Link 
              to={`/tournaments/${tournamentId}`}
              className="bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600 text-white font-bold py-3 px-6 rounded-lg transition-all duration-200 pixel-font"
            >
              ← Volver al Torneo
            </Link>
          </div>
        )}
      </main>
    </div>
  )
}
