import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { tournamentAPI } from '../../services/api'

export default function CreateTournamentModal({ onClose }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    tournament_type: 'single',
    max_teams: '8'
  })

  const queryClient = useQueryClient()
  
  const createMutation = useMutation({
    mutationFn: (data) => {
      console.log('Sending data:', data) // Debug log
      return tournamentAPI.create(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['tournaments'])
      onClose()
    },
    onError: (error) => {
      console.error('Error creating tournament:', error)
      console.error('Error response:', error.response?.data)
    }
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    const submitData = {
      ...formData,
      max_teams: parseInt(formData.max_teams)
    }
    console.log('Form data:', submitData) // Debug log
    createMutation.mutate(submitData)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="card max-w-md w-full mx-4">
        <h3 className="text-xl font-bold text-primary mb-4">Crear Torneo</h3>
        
        {createMutation.error && (
          <div className="bg-red-500/20 border border-red-500 text-red-300 p-3 rounded mb-4">
            Error: {createMutation.error.response?.data?.detail || createMutation.error.message}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Nombre del torneo"
            className="input-field w-full"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            required
          />
          
          <textarea
            placeholder="Descripción"
            className="input-field w-full h-20"
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
          />
          
          <select
            className="input-field w-full"
            value={formData.tournament_type}
            onChange={(e) => setFormData({...formData, tournament_type: e.target.value})}
          >
            <option value="single">Eliminación Simple</option>
            <option value="double">Eliminación Doble</option>
          </select>
          
          <input
            type="number"
            placeholder="Máximo de equipos"
            className="input-field w-full"
            value={formData.max_teams}
            onChange={(e) => setFormData({...formData, max_teams: e.target.value})}
            min="4"
            max="32"
          />
          
          <div className="flex gap-2">
            <button 
              type="submit" 
              className="btn-primary flex-1"
              disabled={createMutation.isPending}
            >
              {createMutation.isPending ? 'Creando...' : 'Crear'}
            </button>
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
