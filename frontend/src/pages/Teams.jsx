import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { teamAPI } from '../services/api'
import TeamRegistrationForm from '../components/teams/TeamRegistrationForm'
import TeamCard from '../components/teams/TeamCard'
import TeamEditModal from '../components/teams/TeamEditModal'

export default function Teams() {
  const { id: tournamentId } = useParams()
  const [editingTeam, setEditingTeam] = useState(null)
  const queryClient = useQueryClient()

  const { data: teams = [], isLoading } = useQuery({
    queryKey: ['teams', tournamentId],
    queryFn: () => teamAPI.getAll(tournamentId).then(res => res.data),
    enabled: !!tournamentId
  })

  const createTeamMutation = useMutation({
    mutationFn: teamAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['teams', tournamentId])
    },
    onError: (error) => {
      console.error('Error creating team:', error)
      console.error('Error response:', error.response?.data)
      
      if (error.response?.data) {
        const errorData = error.response.data
        if (errorData.non_field_errors) {
          alert(`Error: ${errorData.non_field_errors[0]}`)
        } else if (errorData.name) {
          alert(`Error en nombre: ${errorData.name[0]}`)
        } else if (errorData.players) {
          alert(`Error en jugadores: ${JSON.stringify(errorData.players)}`)
        } else {
          alert(`Error: ${JSON.stringify(errorData)}`)
        }
      } else {
        alert('Error al crear el equipo. Revisa los datos.')
      }
    }
  })

  const uploadPhotoMutation = useMutation({
    mutationFn: ({ teamId, formData }) => teamAPI.uploadPhoto(teamId, formData),
    onSuccess: () => {
      queryClient.invalidateQueries(['teams', tournamentId])
    }
  })

  const updateTeamMutation = useMutation({
    mutationFn: ({ teamId, data }) => teamAPI.update(teamId, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['teams', tournamentId])
      setEditingTeam(null)
    }
  })

  const deleteTeamMutation = useMutation({
    mutationFn: teamAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['teams', tournamentId])
      setEditingTeam(null)
    }
  })

  if (isLoading) {
    return <div className="text-center text-white">Cargando equipos...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-pixel text-primary">👥 Registro de Equipos</h2>
        <div className="flex items-center gap-4">
          <Link
            to={`/tournaments/${tournamentId}/brackets`}
            className="bg-gradient-to-r from-secondary to-accent text-white px-4 py-2 rounded-lg pixel-font text-sm hover:shadow-lg hover:shadow-secondary/50 transition-all duration-200 hover:scale-105"
          >
            🏆 Ver Brackets
          </Link>
          <div className="text-accent font-pixel">
            {teams.length} equipos registrados
          </div>
        </div>
      </div>

      <TeamRegistrationForm 
        onSubmit={createTeamMutation.mutate}
        isLoading={createTeamMutation.isPending}
        tournamentId={parseInt(tournamentId)}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {teams.map(team => (
          <TeamCard 
            key={team.id} 
            team={team}
            onUploadPhoto={(formData) => uploadPhotoMutation.mutate({ teamId: team.id, formData })}
            onEdit={() => setEditingTeam(team)}
            isUploading={uploadPhotoMutation.isPending}
          />
        ))}
      </div>

      {teams.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <div className="text-6xl mb-4">🎮</div>
          <p className="text-xl">No hay equipos registrados aún</p>
          <p>¡Registra el primer equipo para comenzar!</p>
        </div>
      )}

      {editingTeam && (
        <TeamEditModal
          team={editingTeam}
          onClose={() => setEditingTeam(null)}
          onSave={(data) => updateTeamMutation.mutate({ teamId: editingTeam.id, data })}
          onDelete={(teamId) => deleteTeamMutation.mutate(teamId)}
          isLoading={updateTeamMutation.isPending || deleteTeamMutation.isPending}
        />
      )}
    </div>
  )
}
