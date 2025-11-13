export default function GameCard({ game, onEdit, onDelete, onToggleActive, isDeleting, isToggling }) {
  return (
    <div className={`bg-slate-800/50 border-2 rounded-lg p-4 transition-all duration-200 hover:scale-105 ${
      game.is_active ? 'border-green-500/30 hover:border-green-500/50' : 'border-gray-600/30 hover:border-gray-500/50'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-3xl">{game.emoji || '🎮'}</span>
          <div>
            <h3 className="font-bold text-white pixel-font">{game.name}</h3>
            <div className="flex items-center gap-2 text-xs">
              <span className={`px-2 py-1 rounded pixel-font ${
                game.is_active 
                  ? 'bg-green-500/20 text-green-400' 
                  : 'bg-gray-500/20 text-gray-400'
              }`}>
                {game.is_active ? '✅ Activo' : '❌ Inactivo'}
              </span>
              {game.is_predefined && (
                <span className="px-2 py-1 rounded bg-blue-500/20 text-blue-400 pixel-font">
                  🏷️ Predefinido
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Description */}
      {game.description && (
        <p className="text-gray-300 text-sm mb-3 line-clamp-2">
          {game.description}
        </p>
      )}

      {/* Image */}
      {game.image && (
        <div className="mb-3">
          <img 
            src={game.image} 
            alt={game.name}
            className="w-full h-24 object-cover rounded border border-slate-600"
          />
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 gap-2 mb-4 text-xs">
        <div className="bg-slate-700/50 rounded p-2 text-center">
          <div className="text-orange-400 font-bold pixel-font">
            {game.matches_count || 0}
          </div>
          <div className="text-gray-400">Partidas</div>
        </div>
        <div className="bg-slate-700/50 rounded p-2 text-center">
          <div className="text-blue-400 font-bold pixel-font">
            {game.tournaments_count || 0}
          </div>
          <div className="text-gray-400">Torneos</div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={onEdit}
          className="flex-1 bg-blue-600 hover:bg-blue-500 text-white px-3 py-2 rounded pixel-font text-xs transition-all duration-200 hover:scale-105"
        >
          ✏️ Editar
        </button>
        
        <button
          onClick={onToggleActive}
          disabled={isToggling}
          className={`flex-1 px-3 py-2 rounded pixel-font text-xs transition-all duration-200 hover:scale-105 disabled:opacity-50 ${
            game.is_active
              ? 'bg-yellow-600 hover:bg-yellow-500 text-white'
              : 'bg-green-600 hover:bg-green-500 text-white'
          }`}
        >
          {isToggling ? '⏳' : game.is_active ? '⏸️ Pausar' : '▶️ Activar'}
        </button>
        
        {!game.is_predefined && (
          <button
            onClick={onDelete}
            disabled={isDeleting}
            className="bg-red-600 hover:bg-red-500 text-white px-3 py-2 rounded pixel-font text-xs transition-all duration-200 hover:scale-105 disabled:opacity-50"
          >
            {isDeleting ? '⏳' : '🗑️'}
          </button>
        )}
      </div>
    </div>
  )
}
