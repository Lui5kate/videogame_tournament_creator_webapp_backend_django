import { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '../hooks/useAuth.jsx'
import { tournamentAPI } from '../services/api'
import TournamentEditModal from '../components/tournament/TournamentEditModal'
import ChatSidebar from '../components/chat/ChatSidebar'
import ChatToggle from '../components/chat/ChatToggle'

export default function Tournament() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { isAdmin, user, logout } = useAuth()
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [chatOpen, setChatOpen] = useState(false)
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

      <div className="container mx-auto px-4 py-8 space-y-6">
      {/* Botón de regreso */}
      <Link 
        to="/"
        className="inline-flex items-center space-x-2 text-accent hover:text-primary transition-colors font-pixel"
      >
        <span>←</span>
        <span>Volver al Dashboard</span>
      </Link>

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
            {/* Botones solo para administradores */}
            {isAdmin() && (
              <>
                {tournament.status !== 'completed' && (
                  <button
                    onClick={() => setShowEditModal(true)}
                    className="text-accent hover:text-primary text-lg"
                    title="Editar torneo"
                  >
                    ✏️
                  </button>
                )}
                <button
                  onClick={() => setShowDeleteModal(true)}
                  className="text-red-400 hover:text-red-300 text-lg"
                  title="Eliminar torneo"
                >
                  🗑️
                </button>
              </>
            )}
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

        <Link 
          to={`/tournaments/${id}/chat`}
          className="bg-surface border-2 border-accent hover:border-primary rounded-lg p-6 text-center transition-colors group"
        >
          <div className="text-4xl mb-3">💬</div>
          <h3 className="text-xl font-pixel text-white group-hover:text-primary">Chat</h3>
          <p className="text-gray-400 mt-2">Chat en vivo del torneo</p>
          <div className="text-accent font-pixel mt-2">Disponible</div>
        </Link>
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

      {showDeleteModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="card max-w-md w-full mx-4">
            <h3 className="text-xl font-pixel text-red-400 mb-4">🗑️ Confirmar Eliminación</h3>
            <p className="text-gray-300 mb-6">
              ¿Estás seguro de que quieres eliminar el torneo <strong>"{tournament.name}"</strong>?
            </p>
            <p className="text-red-300 text-sm mb-6">
              Esta acción no se puede deshacer y se perderán todos los datos del torneo.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded font-pixel"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  deleteTournamentMutation.mutate(id)
                  setShowDeleteModal(false)
                }}
                disabled={deleteTournamentMutation.isPending}
                className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded font-pixel disabled:opacity-50"
              >
                {deleteTournamentMutation.isPending ? 'Eliminando...' : 'Eliminar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Chat Components */}
      <ChatToggle 
        isOpen={chatOpen} 
        onToggle={() => setChatOpen(!chatOpen)} 
      />
      <ChatSidebar 
        tournamentId={id} 
        isOpen={chatOpen} 
        onToggle={() => setChatOpen(false)} 
      />
      </div>
    </div>
  )
}
