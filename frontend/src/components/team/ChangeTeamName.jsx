import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { teamAPI } from '../../services/api'

export default function ChangeTeamName({ team, isCaptain, onClose }) {
  const [newName, setNewName] = useState('')
  const [error, setError] = useState('')
  const queryClient = useQueryClient()

  const changeNameMutation = useMutation({
    mutationFn: teamAPI.changeTeamName,
    onSuccess: () => {
      queryClient.invalidateQueries(['teams'])
      queryClient.invalidateQueries(['my-team'])
      onClose()
    },
    onError: (error) => {
      setError(error.response?.data?.error || 'Error al cambiar nombre')
    }
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!newName.trim() || newName.trim().length < 2) {
      setError('El nombre debe tener al menos 2 caracteres')
      return
    }
    
    setError('')
    changeNameMutation.mutate({
      team_id: team.id,
      new_name: newName.trim()
    })
  }

  if (!isCaptain) {
    return (
      <div className="bg-surface/90 backdrop-blur-sm p-6 rounded-lg border-2 border-primary/30">
        <div className="text-center text-gray-400">
          <div className="text-4xl mb-2">🚫</div>
          <p>Solo el capitán del equipo puede cambiar el nombre</p>
        </div>
      </div>
    )
  }

  if (team.name_changed) {
    return (
      <div className="bg-surface/90 backdrop-blur-sm p-6 rounded-lg border-2 border-primary/30">
        <div className="text-center text-gray-400">
          <div className="text-4xl mb-2">✅</div>
          <p>El nombre del equipo ya fue cambiado anteriormente</p>
          <p className="text-sm mt-2">Solo se permite un cambio por equipo</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-surface/90 backdrop-blur-sm p-6 rounded-lg border-2 border-primary/30">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl pixel-font text-primary">✏️ Cambiar Nombre del Equipo</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white text-xl"
        >
          ✕
        </button>
      </div>

      <div className="mb-4">
        <p className="text-gray-300 text-sm mb-2">
          👑 Como capitán, puedes cambiar el nombre del equipo <strong>una sola vez</strong>
        </p>
        <p className="text-accent text-sm">
          Nombre actual: <strong>{team.name}</strong>
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Nuevo nombre del equipo..."
            className="w-full p-3 bg-background border-2 border-primary/30 rounded-lg text-blue-500 placeholder-gray-400 focus:border-primary focus:outline-none"
            minLength={2}
            maxLength={50}
            required
          />
        </div>

        {error && (
          <div className="bg-red-500/20 border border-red-500 rounded-lg p-3">
            <p className="text-red-300 text-sm">❌ {error}</p>
          </div>
        )}

        <div className="flex gap-3">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded-lg transition-colors pixel-font"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={changeNameMutation.isPending || !newName.trim()}
            className="flex-1 bg-primary hover:bg-primary/80 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-2 px-4 rounded-lg transition-colors pixel-font"
          >
            {changeNameMutation.isPending ? '⏳ Cambiando...' : '✅ Cambiar Nombre'}
          </button>
        </div>
      </form>
    </div>
  )
}
