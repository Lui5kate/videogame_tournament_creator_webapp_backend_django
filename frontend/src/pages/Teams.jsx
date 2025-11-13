import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../hooks/useAuth.jsx'
import { tournamentAPI, teamAPI } from '../services/api'
import TeamManagement from '../components/team/TeamManagement'

export default function Teams() {
  const { id: tournamentId } = useParams()
  const { isAdmin, user, logout } = useAuth()

  const { data: tournament, isLoading } = useQuery({
    queryKey: ['tournament', tournamentId],
    queryFn: () => tournamentAPI.getById(tournamentId).then(res => res.data)
  })

  const { data: teams = [] } = useQuery({
    queryKey: ['teams', tournamentId],
    queryFn: () => teamAPI.getByTournament(tournamentId).then(res => res.data || []),
    enabled: !isAdmin()
  })

  // Encontrar el equipo del jugador actual
  const userTeam = teams.find(team => 
    team.players?.some(player => player.user_info?.id === user?.id)
  )

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-orange-500 border-t-transparent mx-auto mb-4"></div>
          <p className="text-orange-400 pixel-font">🎮 CARGANDO...</p>
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
                {isAdmin() ? '👥 GESTIÓN DE EQUIPOS' : '🎯 MI PARTICIPACIÓN'}
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
          <PlayerView 
            tournament={tournament} 
            teams={teams} 
            userTeam={userTeam} 
            user={user} 
          />
        )}
      </main>
    </div>
  )
}

// Componente para vista de jugador
function PlayerView({ tournament, teams, userTeam, user }) {
  return (
    <div className="space-y-6">
      {/* Estado del jugador */}
      <div className="bg-slate-800/50 backdrop-blur-sm border-2 border-orange-500/30 rounded-lg p-6">
        <h3 className="text-xl font-bold text-orange-400 mb-4 pixel-font">
          🎯 TU ESTADO EN EL TORNEO
        </h3>
        
        {userTeam ? (
          <div className="bg-green-900/20 border-2 border-green-500/30 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-lg font-bold text-green-400 pixel-font">
                  ✅ ASIGNADO AL EQUIPO: {userTeam.name}
                </h4>
                <p className="text-gray-300 mt-2">
                  Ya tienes equipo asignado. ¡Prepárate para competir!
                </p>
              </div>
              <div className="text-4xl">🎮</div>
            </div>
            
            {/* Información del equipo */}
            <div className="mt-4 pt-4 border-t border-green-500/30">
              <h5 className="text-green-300 font-bold mb-2">Compañeros de equipo:</h5>
              <div className="space-y-2">
                {userTeam.players?.map(player => (
                  <div key={player.id} className="flex items-center space-x-3">
                    <span className="text-lg">
                      {player.is_captain ? '👑' : '🎮'}
                    </span>
                    <div>
                      <p className="text-white font-medium">
                        {player.user_info?.full_name || player.name}
                        {player.user_info?.id === user?.id && ' (Tú)'}
                      </p>
                      <p className="text-xs text-gray-400">
                        {player.user_info?.attuid}
                        {player.is_captain && ' • Capitán'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-yellow-900/20 border-2 border-yellow-500/30 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-lg font-bold text-yellow-400 pixel-font">
                  ⏳ ESPERANDO ASIGNACIÓN
                </h4>
                <p className="text-gray-300 mt-2">
                  Aún no tienes equipo asignado. El administrador te asignará pronto.
                </p>
              </div>
              <div className="text-4xl">⏰</div>
            </div>
          </div>
        )}
      </div>

      {/* Todos los equipos participantes */}
      <div className="bg-slate-800/50 backdrop-blur-sm border-2 border-blue-500/30 rounded-lg p-6">
        <h3 className="text-xl font-bold text-blue-400 mb-4 pixel-font">
          👥 EQUIPOS PARTICIPANTES ({teams.length}/{tournament.max_teams})
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {teams.map(team => (
            <div 
              key={team.id} 
              className={`bg-slate-700/50 rounded-lg p-4 border-2 ${
                team.id === userTeam?.id 
                  ? 'border-green-500/50 bg-green-900/10' 
                  : 'border-slate-600'
              }`}
            >
              <div className="flex justify-between items-center mb-3">
                <h4 className="text-lg font-bold text-white pixel-font">
                  {team.name}
                  {team.id === userTeam?.id && (
                    <span className="ml-2 text-green-400">✅</span>
                  )}
                </h4>
                <span className="text-sm text-gray-400">
                  {team.players?.length || 0}/2
                </span>
              </div>

              <div className="space-y-2">
                {team.players?.length > 0 ? (
                  team.players.map(player => (
                    <div key={player.id} className="flex items-center space-x-2">
                      <span className="text-sm">
                        {player.is_captain ? '👑' : '🎮'}
                      </span>
                      <div className="flex-1">
                        <p className="text-white text-sm">
                          {player.user_info?.full_name || player.name}
                          {player.user_info?.id === user?.id && (
                            <span className="ml-1 text-green-400">(Tú)</span>
                          )}
                        </p>
                        {player.is_captain && (
                          <p className="text-xs text-yellow-400">Capitán</p>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-2 text-gray-400 text-sm">
                    🚫 Sin jugadores
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {teams.length === 0 && (
          <div className="text-center py-8 text-gray-400">
            <div className="text-4xl mb-2">📝</div>
            <p>Aún no hay equipos registrados en este torneo</p>
          </div>
        )}
      </div>
    </div>
  )
}
