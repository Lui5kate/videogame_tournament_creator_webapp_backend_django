import { useState } from 'react'

export default function TeamRegistrationForm({ onSubmit, isLoading, tournamentId }) {
  const [formData, setFormData] = useState({
    name: '',
    players: [
      { name: '', is_captain: true },
      { name: '', is_captain: false }
    ]
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({
      tournament: tournamentId,
      name: formData.name,
      players: formData.players
    })
    setFormData({
      name: '',
      players: [
        { name: '', is_captain: true },
        { name: '', is_captain: false }
      ]
    })
  }

  const updatePlayer = (index, field, value) => {
    const newPlayers = [...formData.players]
    newPlayers[index][field] = value
    setFormData({ ...formData, players: newPlayers })
  }

  return (
    <div className="bg-surface border-2 border-primary rounded-lg p-6">
      <h3 className="text-xl font-pixel text-accent mb-4">🎮 Registrar Nuevo Equipo</h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-white font-pixel mb-2">Nombre del Equipo</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full p-3 bg-background border-2 border-accent rounded text-gray-300 placeholder-gray-500"
            placeholder="Los Guerreros Gaming"
            required
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {formData.players.map((player, index) => (
            <div key={index} className="space-y-2">
              <label className="block text-white font-pixel">
                {player.is_captain ? '👑 Capitán' : '🎯 Jugador 2'}
              </label>
              <input
                type="text"
                value={player.name}
                onChange={(e) => updatePlayer(index, 'name', e.target.value)}
                className="w-full p-3 bg-background border-2 border-accent rounded text-gray-300 placeholder-gray-500"
                placeholder={player.is_captain ? "Mario" : "Luigi"}
                required
              />
            </div>
          ))}
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-primary hover:bg-secondary text-white font-pixel py-3 px-6 rounded-lg border-2 border-accent transition-colors disabled:opacity-50"
        >
          {isLoading ? '⏳ Registrando...' : '✅ Registrar Equipo'}
        </button>
      </form>
    </div>
  )
}
