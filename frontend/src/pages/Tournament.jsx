import { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { tournamentAPI } from '../services/api'
import TournamentEditModal from '../components/tournament/TournamentEditModal'

export default function Tournament() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [showEditModal, setShowEditModal] = useState(false)
  const queryClient = useQueryClient()
  
  const { data: tournament, isLoading } = useQuery({
    queryKey: ['tournament', id],
    queryFn: () => tournamentAPI.getById(id).then(res => res.data)
  })

  const updateTournamentMutation = useMutation({
    mutationFn: ({ id, data }) => tournamentAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['tournament', id])
      setShowEditModal(false)
    }
  })

  const deleteTournamentMutation = useMutation({
    mutationFn: tournamentAPI.delete,
    onSuccess: () => {
      navigate('/')
    }
  })

  if (isLoading) {
    return <div className="text-center text-white">Cargando torneo...</div>
  }

  if (!tournament) {
    return <div className="text-center text-red-400">Torneo no encontrado</div>
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

  const getStatusText = (status) => {
    const texts = {
      setup: '⚙️ Configuración',
      registration: '📝 Registro Abierto',
      active: '🎮 En Progreso', 
      completed: '🏆 Finalizado'
    }
    return texts[status] || status
  }

  return (
    <div className="space-y-6">
      {/* Header del torneo */}
      <div className="bg-surface border-2 border-primary rounded-lg p-6">
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <h1 className="text-3xl font-pixel text-primary mb-2">{tournament.name}</h1>
            <p className="text-gray-300">{tournament.description}</p>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`font-pixel ${getStatusColor(tournament.status)}`}>
              {getStatusText(tournament.status)}
            </span>
            <button
              onClick={() => setShowEditModal(true)}
              className="text-accent hover:text-primary text-lg"
              title="Editar torneo"
            >
              ✏️
            </button>
            <button
              onClick={() => deleteTournamentMutation.mutate(id)}
              className="text-red-400 hover:text-red-300 text-lg"
              title="Eliminar torneo"
            >
              🗑️
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="bg-background rounded p-3">
            <div className="text-accent font-pixel text-xl">{tournament.registered_teams_count}</div>
            <div className="text-gray-400 text-sm">Equipos</div>
          </div>
          <div className="bg-background rounded p-3">
            <div className="text-accent font-pixel text-xl">{tournament.max_teams}</div>
            <div className="text-gray-400 text-sm">Máximo</div>
          </div>
          <div className="bg-background rounded p-3">
            <div className="text-accent font-pixel text-xl">{tournament.completed_matches_count}</div>
            <div className="text-gray-400 text-sm">Partidas</div>
          </div>
          <div className="bg-background rounded p-3">
            <div className="text-accent font-pixel text-xl">{tournament.tournament_type === 'single' ? 'Simple' : 'Doble'}</div>
            <div className="text-gray-400 text-sm">Eliminación</div>
          </div>
        </div>
      </div>

      {/* Navegación de secciones */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link 
          to={`/tournaments/${id}/teams`}
          className="bg-surface border-2 border-accent hover:border-primary rounded-lg p-6 text-center transition-colors group"
        >
          <div className="text-4xl mb-3">👥</div>
          <h3 className="text-xl font-pixel text-white group-hover:text-primary">Equipos</h3>
          <p className="text-gray-400 mt-2">Registrar y gestionar equipos</p>
          <div className="text-accent font-pixel mt-2">{tournament.registered_teams_count} registrados</div>
        </Link>

        <Link 
          to={`/tournaments/${id}/brackets`}
          className="bg-surface border-2 border-secondary hover:border-primary rounded-lg p-6 text-center transition-colors group"
        >
          <div className="text-4xl mb-3">🏆</div>
          <h3 className="text-xl font-pixel text-white group-hover:text-primary">Brackets</h3>
          <p className="text-gray-400 mt-2">Visualizar y gestionar partidas</p>
          <div className="text-secondary font-pixel mt-2">{tournament.completed_matches_count} completadas</div>
        </Link>

        <div className="bg-surface border-2 border-gray-600 rounded-lg p-6 text-center opacity-50">
          <div className="text-4xl mb-3">💬</div>
          <h3 className="text-xl font-pixel text-gray-400">Chat</h3>
          <p className="text-gray-500 mt-2">Próximamente</p>
          <div className="text-gray-500 font-pixel mt-2">En desarrollo</div>
        </div>
      </div>

      {/* Acciones rápidas */}
      {tournament.status === 'registration' && tournament.can_start && (
        <div className="bg-green-900/20 border-2 border-green-500 rounded-lg p-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-green-400 font-pixel">¡Listo para iniciar!</h3>
              <p className="text-gray-300">El torneo tiene suficientes equipos para comenzar</p>
            </div>
            <button className="bg-green-500 hover:bg-green-600 text-white font-pixel py-2 px-4 rounded">
              🚀 Iniciar Torneo
            </button>
          </div>
        </div>
      )}

      {tournament.status === 'setup' && (
        <div className="bg-blue-900/20 border-2 border-blue-500 rounded-lg p-4">
          <div className="text-center">
            <h3 className="text-blue-400 font-pixel mb-2">Torneo en configuración</h3>
            <p className="text-gray-300">Registra equipos para poder iniciar el torneo</p>
          </div>
        </div>
      )}

      {showEditModal && (
        <TournamentEditModal
          tournament={tournament}
          onClose={() => setShowEditModal(false)}
          onSave={(data) => updateTournamentMutation.mutate({ id, data })}
          onDelete={() => deleteTournamentMutation.mutate(id)}
          isLoading={updateTournamentMutation.isPending || deleteTournamentMutation.isPending}
        />
      )}
    </div>
  )
}
