import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { gameAPI } from '../../services/api'
import GameForm from './GameForm'
import GameCard from './GameCard'

export default function GameManagement() {
  const [showForm, setShowForm] = useState(false)
  const [editingGame, setEditingGame] = useState(null)
  const [filter, setFilter] = useState('all') // all, active, inactive
  const queryClient = useQueryClient()

  const { data: games = [], isLoading } = useQuery({
    queryKey: ['games'],
    queryFn: () => gameAPI.getAll().then(res => res.data)
  })

  const createMutation = useMutation({
    mutationFn: gameAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['games'])
      setShowForm(false)
    }
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => gameAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['games'])
      setEditingGame(null)
    }
  })

  const deleteMutation = useMutation({
    mutationFn: gameAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['games'])
    }
  })

  const toggleActiveMutation = useMutation({
    mutationFn: ({ id, is_active }) => gameAPI.update(id, { is_active }),
    onSuccess: () => {
      queryClient.invalidateQueries(['games'])
    }
  })

  const handleCreate = (gameData) => {
    createMutation.mutate(gameData)
  }

  const handleUpdate = (gameData) => {
    updateMutation.mutate({ id: editingGame.id, data: gameData })
  }

  const handleDelete = (gameId) => {
    if (window.confirm('¿Estás seguro de eliminar este juego?')) {
      deleteMutation.mutate(gameId)
    }
  }

  const handleToggleActive = (game) => {
    toggleActiveMutation.mutate({ id: game.id, is_active: !game.is_active })
  }

  const filteredGames = games.filter(game => {
    if (filter === 'active') return game.is_active
    if (filter === 'inactive') return !game.is_active
    return true
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-4 border-orange-500 border-t-transparent"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-accent pixel-font">🎮 Gestión de Juegos</h2>
          <p className="text-gray-400 text-sm">Administra los juegos disponibles para los torneos</p>
        </div>
        
        <button
          onClick={() => setShowForm(true)}
          className="bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white px-6 py-3 rounded-lg pixel-font text-sm hover:shadow-lg hover:shadow-green-500/50 transition-all duration-200 hover:scale-105"
        >
          ➕ Nuevo Juego
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {[
          { key: 'all', label: '🎯 Todos', count: games.length },
          { key: 'active', label: '✅ Activos', count: games.filter(g => g.is_active).length },
          { key: 'inactive', label: '❌ Inactivos', count: games.filter(g => !g.is_active).length }
        ].map(({ key, label, count }) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={`px-4 py-2 rounded-lg pixel-font text-sm transition-all duration-200 ${
              filter === key
                ? 'bg-orange-500 text-white shadow-lg'
                : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
            }`}
          >
            {label} ({count})
          </button>
        ))}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <div className="text-2xl font-bold text-accent pixel-font">{games.length}</div>
          <div className="text-gray-400 text-sm">Total de Juegos</div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-400 pixel-font">
            {games.filter(g => g.is_active).length}
          </div>
          <div className="text-gray-400 text-sm">Juegos Activos</div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <div className="text-2xl font-bold text-blue-400 pixel-font">
            {games.filter(g => g.is_predefined).length}
          </div>
          <div className="text-gray-400 text-sm">Juegos Predefinidos</div>
        </div>
      </div>

      {/* Games Grid */}
      {filteredGames.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <div className="text-6xl mb-4">🎮</div>
          <p className="text-lg">No hay juegos {filter === 'all' ? '' : filter === 'active' ? 'activos' : 'inactivos'}</p>
          {filter === 'all' && (
            <button
              onClick={() => setShowForm(true)}
              className="mt-4 text-orange-400 hover:text-orange-300 pixel-font"
            >
              ➕ Crear el primer juego
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredGames.map(game => (
            <GameCard
              key={game.id}
              game={game}
              onEdit={() => setEditingGame(game)}
              onDelete={() => handleDelete(game.id)}
              onToggleActive={() => handleToggleActive(game)}
              isDeleting={deleteMutation.isPending}
              isToggling={toggleActiveMutation.isPending}
            />
          ))}
        </div>
      )}

      {/* Create Form Modal */}
      {showForm && (
        <GameForm
          onSubmit={handleCreate}
          onCancel={() => setShowForm(false)}
          isLoading={createMutation.isPending}
          title="Crear Nuevo Juego"
        />
      )}

      {/* Edit Form Modal */}
      {editingGame && (
        <GameForm
          game={editingGame}
          onSubmit={handleUpdate}
          onCancel={() => setEditingGame(null)}
          isLoading={updateMutation.isPending}
          title="Editar Juego"
        />
      )}
    </div>
  )
}
