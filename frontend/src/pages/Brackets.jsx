import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { tournamentAPI } from '../services/api'
import BracketVisualization from '../components/brackets/BracketVisualization'

export default function Brackets() {
  const { id } = useParams()
  const queryClient = useQueryClient()

  const { data: tournament, isLoading } = useQuery({
    queryKey: ['tournament', id],
    queryFn: () => tournamentAPI.getById(id).then(res => res.data)
  })

  const startTournamentMutation = useMutation({
    mutationFn: tournamentAPI.start,
    onSuccess: () => {
      queryClient.invalidateQueries(['tournament', id])
      queryClient.invalidateQueries(['matches', id])
    }
  })

  const handleStartTournament = () => {
    startTournamentMutation.mutate(id)
  }

  if (isLoading) {
    return (
      <div className="text-center text-white pixel-font">
        <div className="animate-pulse">🎮 Cargando torneo...</div>
      </div>
    )
  }

  if (!tournament) {
    return (
      <div className="text-center text-red-400 pixel-font">
        <div className="text-4xl mb-4">❌</div>
        <div>Torneo no encontrado</div>
        <Link to="/" className="text-accent hover:text-primary mt-4 inline-block">
          ← Volver al inicio
        </Link>
      </div>
    )
  }

  const getStatusColor = (status) => {
    const colors = {
      setup: 'text-gray-400',
      registration: 'text-blue-400', 
      active: 'text-green-400',
      completed: 'text-accent'
    }
    return colors[status] || 'text-gray-400'
  }

  const getStatusLabel = (status) => {
    const labels = {
      setup: '⚙️ Configuración',
      registration: '📝 Registro Abierto',
      active: '🎮 Activo',
      completed: '🏆 Completado'
    }
    return labels[status] || status
  }

  const canStartTournament = tournament.status === 'registration' && tournament.registered_teams_count >= 2

  return (
    <div className="min-h-screen bg-background text-white">
      {/* Header */}
      <div className="bg-surface/50 border-b border-primary/30 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <Link 
              to={`/tournaments/${id}`}
              className="text-accent hover:text-primary pixel-font text-sm transition-colors"
            >
              ← Volver al torneo
            </Link>
            <div className="flex items-center gap-4">
              <Link
                to={`/tournaments/${id}/teams`}
                className="bg-secondary/20 hover:bg-secondary/40 text-secondary px-4 py-2 rounded pixel-font text-sm transition-all duration-200 hover:scale-105"
              >
                👥 Equipos
              </Link>
            </div>
          </div>
          
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-accent pixel-font mb-2">
                🏆 {tournament.name}
              </h1>
              <div className="flex items-center gap-4 text-sm">
                <span className={`pixel-font ${getStatusColor(tournament.status)}`}>
                  {getStatusLabel(tournament.status)}
                </span>
                <span className="text-gray-400">
                  {tournament.tournament_type === 'single' ? '🎯 Eliminación Simple' : '⚔️ Eliminación Doble'}
                </span>
                <span className="text-gray-400">
                  👥 {tournament.registered_teams_count} equipos
                </span>
              </div>
            </div>
            
            {canStartTournament && (
              <button
                onClick={handleStartTournament}
                disabled={startTournamentMutation.isPending}
                className="bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white px-6 py-3 rounded-lg pixel-font text-sm hover:shadow-lg hover:shadow-green-500/50 transition-all duration-200 hover:scale-105 disabled:opacity-50"
              >
                {startTournamentMutation.isPending ? '⚡ Iniciando...' : '🚀 Iniciar Torneo'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto p-6">
        {tournament.status === 'setup' ? (
          <div className="text-center space-y-6 py-12">
            <div className="text-6xl">⚙️</div>
            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-accent pixel-font">
                Torneo en Configuración
              </h2>
              <p className="text-gray-400 pixel-font">
                Registra al menos 2 equipos para poder iniciar el torneo
              </p>
            </div>
            <Link
              to={`/tournaments/${id}/teams`}
              className="bg-gradient-to-r from-primary to-secondary text-white px-6 py-3 rounded-lg pixel-font text-sm hover:shadow-lg hover:shadow-primary/50 transition-all duration-200 hover:scale-105 inline-block"
            >
              👥 Registrar Equipos
            </Link>
          </div>
        ) : tournament.status === 'registration' ? (
          <div className="text-center space-y-6 py-12">
            <div className="text-6xl">📝</div>
            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-blue-400 pixel-font">
                Registro Abierto
              </h2>
              <p className="text-gray-400 pixel-font">
                {tournament.registered_teams_count} equipos registrados
              </p>
              {canStartTournament ? (
                <p className="text-green-400 pixel-font">
                  ✅ ¡Listo para iniciar el torneo!
                </p>
              ) : (
                <p className="text-yellow-400 pixel-font">
                  Se necesitan al menos 2 equipos para iniciar
                </p>
              )}
            </div>
            <div className="flex justify-center gap-4">
              <Link
                to={`/tournaments/${id}/teams`}
                className="bg-gradient-to-r from-secondary to-accent text-white px-6 py-3 rounded-lg pixel-font text-sm hover:shadow-lg hover:shadow-secondary/50 transition-all duration-200 hover:scale-105"
              >
                👥 Gestionar Equipos
              </Link>
              {canStartTournament && (
                <button
                  onClick={handleStartTournament}
                  disabled={startTournamentMutation.isPending}
                  className="bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white px-6 py-3 rounded-lg pixel-font text-sm hover:shadow-lg hover:shadow-green-500/50 transition-all duration-200 hover:scale-105 disabled:opacity-50"
                >
                  {startTournamentMutation.isPending ? '⚡ Iniciando...' : '🚀 Iniciar Torneo'}
                </button>
              )}
            </div>
          </div>
        ) : (
          <BracketVisualization tournamentId={id} />
        )}
      </div>
    </div>
  )
}
