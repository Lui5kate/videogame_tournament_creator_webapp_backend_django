import { useState } from 'react'

export default function TeamEditModal({ team, onClose, onSave, onDelete, isLoading }) {
  const [formData, setFormData] = useState({
    name: team.name,
    players: team.players || [
      { id: null, name: '', is_captain: true },
      { id: null, name: '', is_captain: false }
    ]
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSave({
      name: formData.name,
      players: formData.players
    })
  }

  const updatePlayer = (index, field, value) => {
    const newPlayers = [...formData.players]
    newPlayers[index][field] = value
    setFormData({ ...formData, players: newPlayers })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-surface border-4 border-primary rounded-lg p-6 w-full max-w-md mx-4 shadow-2xl shadow-primary/20">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-pixel text-primary">✏️ Editar Equipo</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-white font-pixel mb-2">Nombre del Equipo</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full p-3 bg-background border-2 border-accent rounded text-blue-300 placeholder-gray-500"
              required
            />
          </div>

          <div className="space-y-3">
            <label className="block text-white font-pixel">Jugadores</label>
            {formData.players.map((player, index) => (
              <div key={index} className="space-y-2">
                <label className="block text-accent text-sm">
                  {player.is_captain ? '👑 Capitán' : '🎯 Jugador 2'}
                </label>
                <input
                  type="text"
                  value={player.name}
                  onChange={(e) => updatePlayer(index, 'name', e.target.value)}
                  className="w-full p-2 bg-background border-2 border-accent rounded text-gray-300 placeholder-gray-500"
                  placeholder={player.is_captain ? "Mario" : "Luigi"}
                  required
                />
              </div>
            ))}
          </div>

          <div className="flex flex-col space-y-2 pt-4">
            <div className="flex space-x-2">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 bg-gray-600 hover:bg-gray-500 text-white font-pixel py-2 px-3 rounded text-sm transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 bg-primary hover:bg-secondary text-white font-pixel py-2 px-3 rounded text-sm transition-colors disabled:opacity-50"
              >
                {isLoading ? '⏳ Guardando...' : '💾 Guardar'}
              </button>
            </div>
            <button
              type="button"
              onClick={() => onDelete(team.id)}
              className="w-full bg-red-600 hover:bg-red-500 text-white font-pixel py-2 px-3 rounded text-sm transition-colors"
            >
              🗑️ Eliminar Equipo
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
