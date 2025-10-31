import { useState } from 'react'

export default function TournamentEditModal({ tournament, onClose, onSave, onDelete, isLoading }) {
  const [formData, setFormData] = useState({
    name: tournament.name,
    description: tournament.description || '',
    tournament_type: tournament.tournament_type,
    max_teams: tournament.max_teams,
    points_per_win: tournament.points_per_win,
    points_per_participation: tournament.points_per_participation
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-surface border-4 border-primary rounded-lg p-6 w-full max-w-lg mx-4 shadow-2xl shadow-primary/20">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-pixel text-primary">✏️ Editar Torneo</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-white font-pixel mb-2">Nombre del Torneo</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full p-3 bg-background border-2 border-accent rounded text-gray-300 placeholder-gray-500"
              required
            />
          </div>

          <div>
            <label className="block text-white font-pixel mb-2">Descripción</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full p-3 bg-background border-2 border-accent rounded text-gray-300 placeholder-gray-500 h-20 resize-none"
              placeholder="Descripción del torneo..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-white font-pixel mb-2">Tipo</label>
              <select
                value={formData.tournament_type}
                onChange={(e) => setFormData({ ...formData, tournament_type: e.target.value })}
                className="w-full p-3 bg-background border-2 border-accent rounded text-gray-300"
              >
                <option value="single">Eliminación Simple</option>
                <option value="double">Eliminación Doble</option>
              </select>
            </div>

            <div>
              <label className="block text-white font-pixel mb-2">Máx. Equipos</label>
              <input
                type="number"
                value={formData.max_teams}
                onChange={(e) => setFormData({ ...formData, max_teams: parseInt(e.target.value) })}
                className="w-full p-3 bg-background border-2 border-accent rounded text-gray-300"
                min="2"
                max="32"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-white font-pixel mb-2">Puntos Victoria</label>
              <input
                type="number"
                value={formData.points_per_win}
                onChange={(e) => setFormData({ ...formData, points_per_win: parseInt(e.target.value) })}
                className="w-full p-3 bg-background border-2 border-accent rounded text-gray-300"
                min="1"
                required
              />
            </div>

            <div>
              <label className="block text-white font-pixel mb-2">Puntos Participación</label>
              <input
                type="number"
                value={formData.points_per_participation}
                onChange={(e) => setFormData({ ...formData, points_per_participation: parseInt(e.target.value) })}
                className="w-full p-3 bg-background border-2 border-accent rounded text-gray-300"
                min="0"
                required
              />
            </div>
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
              onClick={onDelete}
              className="w-full bg-red-600 hover:bg-red-500 text-white font-pixel py-2 px-3 rounded text-sm transition-colors"
            >
              🗑️ Eliminar Torneo
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
