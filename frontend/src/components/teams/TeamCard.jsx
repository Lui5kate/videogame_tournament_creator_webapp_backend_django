import { useState, useRef } from 'react'

export default function TeamCard({ team, onUploadPhoto, onEdit, isUploading }) {
  const [showUpload, setShowUpload] = useState(false)
  const fileInputRef = useRef(null)

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      const formData = new FormData()
      formData.append('team_photo', file)
      onUploadPhoto(formData)
      setShowUpload(false)
    }
  }

  const getBracketStatusColor = (status) => {
    const colors = {
      winners: 'text-green-400',
      losers: 'text-yellow-400',
      eliminated: 'text-red-400',
      champion: 'text-accent'
    }
    return colors[status] || 'text-gray-400'
  }

  const getBracketStatusText = (status) => {
    const texts = {
      winners: '🏆 Winners',
      losers: '⚡ Losers',
      eliminated: '❌ Eliminado',
      champion: '👑 Campeón'
    }
    return texts[status] || '⏳ Esperando'
  }

  return (
    <div className="bg-surface border-2 border-accent rounded-lg p-4 hover:border-primary transition-colors">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-pixel text-white h-12 leading-6 overflow-hidden">{team.name}</h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={onEdit}
            className="text-accent hover:text-primary text-sm"
            title="Editar equipo"
          >
            ✏️
          </button>
          <span className={`text-sm font-pixel ${getBracketStatusColor(team.bracket_status)}`}>
            {getBracketStatusText(team.bracket_status)}
          </span>
        </div>
      </div>

      {/* Foto del equipo */}
      <div className="mb-4">
        {team.team_photo ? (
          <img 
            src={team.team_photo}
            alt={team.name}
            className="w-full h-32 object-cover rounded border-2 border-accent"
          />
        ) : (
          <div className="w-full h-32 bg-background border-2 border-dashed border-gray-500 rounded flex items-center justify-center">
            <span className="text-gray-400 text-sm">📸 Sin foto</span>
          </div>
        )}
        
        {!showUpload ? (
          <button
            onClick={() => setShowUpload(true)}
            className="w-full mt-2 bg-accent hover:bg-secondary text-background font-pixel py-1 px-3 rounded text-sm transition-colors"
          >
            📷 {team.team_photo ? 'Cambiar Foto' : 'Subir Foto'}
          </button>
        ) : (
          <div className="mt-2 space-y-2">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="w-full text-xs text-white file:mr-2 file:py-1 file:px-2 file:rounded file:border-0 file:bg-primary file:text-white"
            />
            <button
              onClick={() => setShowUpload(false)}
              className="w-full bg-gray-600 hover:bg-gray-500 text-white py-1 px-3 rounded text-sm"
            >
              Cancelar
            </button>
          </div>
        )}
      </div>

      {/* Jugadores */}
      <div className="space-y-2 mb-4">
        {team.players?.map((player, index) => (
          <div key={player.id} className="flex items-center space-x-2">
            <span className="text-accent">{player.is_captain ? '👑' : '🎯'}</span>
            <span className="text-white text-sm">{player.name}</span>
          </div>
        ))}
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-3 gap-2 text-center text-sm">
        <div className="bg-background rounded p-2">
          <div className="text-green-400 font-pixel">{team.wins}</div>
          <div className="text-gray-400">Victorias</div>
        </div>
        <div className="bg-background rounded p-2">
          <div className="text-red-400 font-pixel">{team.losses}</div>
          <div className="text-gray-400">Derrotas</div>
        </div>
        <div className="bg-background rounded p-2">
          <div className="text-accent font-pixel">{team.points}</div>
          <div className="text-gray-400">Puntos</div>
        </div>
      </div>

      {isUploading && (
        <div className="mt-2 text-center text-accent text-sm">
          ⏳ Subiendo foto...
        </div>
      )}
    </div>
  )
}
