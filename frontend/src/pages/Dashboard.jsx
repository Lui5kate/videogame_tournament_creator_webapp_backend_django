import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../hooks/useAuth.jsx'
import { tournamentAPI } from '../services/api'
import TournamentCard from '../components/tournament/TournamentCard'
import CreateTournamentModal from '../components/tournament/CreateTournamentModal'

export default function Dashboard() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const { user, isAdmin, logout } = useAuth()
  
  const { data: tournaments, isLoading } = useQuery({
    queryKey: ['tournaments'],
    queryFn: () => tournamentAPI.getAll().then(res => res.data)
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-orange-500 border-t-transparent mx-auto mb-4"></div>
          <p className="text-orange-400 pixel-font">🎮 CARGANDO TORNEOS...</p>
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
              🎮 Videogame Tournament Maker
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

      {/* Contenido principal */}
      <main className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-yellow-400 pixel-font">
              🏆 TORNEOS
            </h2>
            <p className="text-gray-400 mt-2">
              {isAdmin() 
                ? 'Gestiona y administra todos los torneos' 
                : 'Únete a los torneos disponibles'
              }
            </p>
          </div>
          
          {isAdmin() && (
            <button 
              onClick={() => setShowCreateModal(true)}
              className="bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600 text-white font-bold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-105 hover:shadow-lg hover:shadow-orange-500/25 pixel-font"
            >
              ✨ CREAR TORNEO
            </button>
          )}
        </div>

        {/* Grid de torneos */}
        {tournaments && tournaments.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tournaments.map(tournament => (
              <TournamentCard 
                key={tournament.id} 
                tournament={tournament}
                isAdmin={isAdmin()}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">🎮</div>
            <h3 className="text-2xl font-bold text-gray-400 mb-2 pixel-font">
              NO HAY TORNEOS
            </h3>
            <p className="text-gray-500 mb-6">
              {isAdmin() 
                ? 'Crea el primer torneo para comenzar' 
                : 'Aún no hay torneos disponibles'
              }
            </p>
            {isAdmin() && (
              <button 
                onClick={() => setShowCreateModal(true)}
                className="bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600 text-white font-bold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-105 pixel-font"
              >
                ✨ CREAR PRIMER TORNEO
              </button>
            )}
          </div>
        )}

        {/* Información adicional para jugadores */}
        {!isAdmin() && (
          <div className="mt-12 bg-slate-800/50 backdrop-blur-sm border-2 border-yellow-500/30 rounded-lg p-6">
            <h3 className="text-xl font-bold text-yellow-400 mb-4 pixel-font">
              🎯 INFORMACIÓN PARA JUGADORES
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-300">
              <div>
                <h4 className="font-semibold text-orange-400 mb-2">📋 Tu Perfil:</h4>
                <p>• Nombre: {user?.profile?.first_name} {user?.profile?.last_name}</p>
                <p>• ATTUID: {user?.attuid}</p>
                <p>• Experiencia: {user?.profile?.has_played_games ? 'Con experiencia' : 'Principiante'}</p>
              </div>
              <div>
                <h4 className="font-semibold text-orange-400 mb-2">🎮 Juegos Favoritos:</h4>
                {user?.profile?.favorite_game_types?.length > 0 ? (
                  <div className="text-sm space-y-1">
                    {user.profile.favorite_game_types.map((type, index) => {
                      const gameTypeLabels = {
                        'fighting': '🥊 Juegos de Pelea',
                        'racing': '🏎️ Carreras',
                        'sports': '⚽ Deportes',
                        'shooter': '🔫 Disparos',
                        'strategy': '🧠 Estrategia',
                        'rpg': '🗡️ RPG',
                        'platform': '🏃 Plataformas',
                        'puzzle': '🧩 Puzzle',
                        'arcade': '🕹️ Arcade',
                        'other': '🎮 Otros'
                      };
                      return (
                        <p key={index}>• {gameTypeLabels[type] || type}</p>
                      );
                    })}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">No especificados</p>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Modal de crear torneo (solo para admins) */}
      {isAdmin() && showCreateModal && (
        <CreateTournamentModal 
          onClose={() => setShowCreateModal(false)}
        />
      )}
    </div>
  )
}
