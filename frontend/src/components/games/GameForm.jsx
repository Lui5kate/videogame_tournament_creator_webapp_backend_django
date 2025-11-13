import { useState, useEffect } from 'react'

const PREDEFINED_GAMES = [
  { name: 'Street Fighter', emoji: '🥊', description: 'Juego de lucha clásico' },
  { name: 'FIFA', emoji: '⚽', description: 'Simulador de fútbol' },
  { name: 'Mario Kart', emoji: '🏎️', description: 'Carreras arcade divertidas' },
  { name: 'Tekken', emoji: '👊', description: 'Combate 3D intenso' },
  { name: 'Call of Duty', emoji: '🔫', description: 'Shooter en primera persona' },
  { name: 'Super Smash Bros', emoji: '⚔️', description: 'Peleas entre personajes Nintendo' },
  { name: 'Rocket League', emoji: '🚗', description: 'Fútbol con coches' },
  { name: 'Mortal Kombat', emoji: '💀', description: 'Combate brutal y sangriento' },
  { name: 'Fortnite', emoji: '🏗️', description: 'Battle Royale con construcción' },
  { name: 'League of Legends', emoji: '🏰', description: 'MOBA estratégico' }
]

export default function GameForm({ game, onSubmit, onCancel, isLoading, title }) {
  const [formData, setFormData] = useState({
    name: '',
    emoji: '🎮',
    description: '',
    is_active: true,
    is_predefined: false
  })
  const [showPredefined, setShowPredefined] = useState(false)
  const [imageFile, setImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)

  useEffect(() => {
    if (game) {
      setFormData({
        name: game.name || '',
        emoji: game.emoji || '🎮',
        description: game.description || '',
        is_active: game.is_active ?? true,
        is_predefined: game.is_predefined ?? false
      })
      if (game.image) {
        setImagePreview(game.image)
      }
    }
  }, [game])

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setImageFile(file)
      const reader = new FileReader()
      reader.onload = (e) => setImagePreview(e.target.result)
      reader.readAsDataURL(file)
    }
  }

  const handlePredefinedSelect = (predefined) => {
    setFormData(prev => ({
      ...prev,
      name: predefined.name,
      emoji: predefined.emoji,
      description: predefined.description,
      is_predefined: true
    }))
    setShowPredefined(false)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    let submitData = { ...formData }
    
    // Si hay imagen, subirla primero
    if (imageFile) {
      const formDataImage = new FormData()
      formDataImage.append('image', imageFile)
      // Aquí podrías implementar la subida de imagen
      // submitData.image = uploadedImageUrl
    }
    
    onSubmit(submitData)
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 border-2 border-orange-500/30 rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-accent pixel-font">{title}</h2>
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-white text-2xl"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Quick Select Predefined */}
          {!game && (
            <div className="space-y-3">
              <button
                type="button"
                onClick={() => setShowPredefined(!showPredefined)}
                className="w-full bg-blue-600 hover:bg-blue-500 text-white px-4 py-3 rounded-lg pixel-font text-sm transition-all duration-200"
              >
                🎯 {showPredefined ? 'Ocultar' : 'Seleccionar'} Juego Predefinido
              </button>
              
              {showPredefined && (
                <div className="grid grid-cols-2 gap-2 p-4 bg-slate-700/50 rounded-lg">
                  {PREDEFINED_GAMES.map((predefined, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => handlePredefinedSelect(predefined)}
                      className="flex items-center gap-2 p-2 bg-slate-600 hover:bg-slate-500 rounded text-left transition-all duration-200"
                    >
                      <span className="text-xl">{predefined.emoji}</span>
                      <span className="text-sm">{predefined.name}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Basic Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-orange-400 text-sm font-semibold mb-2 pixel-font">
                Nombre del Juego *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white focus:border-orange-500 focus:outline-none transition-colors"
                placeholder="Ej: Street Fighter 6"
              />
            </div>

            <div>
              <label className="block text-orange-400 text-sm font-semibold mb-2 pixel-font">
                Emoji *
              </label>
              <input
                type="text"
                name="emoji"
                value={formData.emoji}
                onChange={handleChange}
                required
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white focus:border-orange-500 focus:outline-none transition-colors text-center text-2xl"
                placeholder="🎮"
                maxLength="2"
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-orange-400 text-sm font-semibold mb-2 pixel-font">
              Descripción
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="3"
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white focus:border-orange-500 focus:outline-none transition-colors resize-none"
              placeholder="Descripción del juego..."
            />
          </div>

          {/* Image Upload */}
          <div>
            <label className="block text-orange-400 text-sm font-semibold mb-2 pixel-font">
              Imagen del Juego
            </label>
            <div className="space-y-3">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white focus:border-orange-500 focus:outline-none transition-colors file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-orange-500 file:text-white file:cursor-pointer"
              />
              {imagePreview && (
                <div className="relative">
                  <img 
                    src={imagePreview} 
                    alt="Preview" 
                    className="w-full h-32 object-cover rounded border border-slate-600"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      setImageFile(null)
                      setImagePreview(null)
                    }}
                    className="absolute top-2 right-2 bg-red-500 hover:bg-red-400 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs"
                  >
                    ✕
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Options */}
          <div className="space-y-3">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleChange}
                className="w-5 h-5 text-orange-500 bg-slate-700 border-slate-600 rounded focus:ring-orange-500"
              />
              <span className="text-white pixel-font">✅ Juego activo (disponible para torneos)</span>
            </label>

            {!game && (
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  name="is_predefined"
                  checked={formData.is_predefined}
                  onChange={handleChange}
                  className="w-5 h-5 text-blue-500 bg-slate-700 border-slate-600 rounded focus:ring-blue-500"
                />
                <span className="text-white pixel-font">🏷️ Marcar como predefinido</span>
              </label>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-4 pt-4">
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 bg-slate-600 hover:bg-slate-500 text-white px-6 py-3 rounded-lg pixel-font transition-all duration-200"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isLoading || !formData.name.trim()}
              className="flex-1 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 text-white px-6 py-3 rounded-lg pixel-font transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? '⏳ Guardando...' : game ? 'Actualizar' : 'Crear Juego'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
