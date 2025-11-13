import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { teamAPI, tournamentAPI } from '../services/api'
import TeamRegistrationForm from '../components/teams/TeamRegistrationForm'
import TeamCard from '../components/teams/TeamCard'
import TeamEditModal from '../components/teams/TeamEditModal'
import ChatSidebar from '../components/chat/ChatSidebar'
import ChatToggle from '../components/chat/ChatToggle'

export default function Teams() {
  const { id: tournamentId } = useParams()
  const [editingTeam, setEditingTeam] = useState(null)
  const [chatOpen, setChatOpen] = useState(false)
  const queryClient = useQueryClient()

  const { data: tournament } = useQuery({
    queryKey: ['tournament', tournamentId],
    queryFn: () => tournamentAPI.getById(tournamentId).then(res => res.data),
    enabled: !!tournamentId
  })

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

  const canAddMoreTeams = tournament && teams.length < tournament.max_teams

  return (
    <div className="space-y-6">
      {/* Botón de regreso */}
      <Link 
        to={`/tournaments/${tournamentId}`}
        className="inline-flex items-center space-x-2 text-accent hover:text-primary transition-colors font-pixel"
      >
        <span>←</span>
        <span>Volver al Torneo</span>
      </Link>

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
            {teams.length}/{tournament?.max_teams || '?'} equipos
          </div>
        </div>
      </div>

      {canAddMoreTeams ? (
        <TeamRegistrationForm 
          onSubmit={createTeamMutation.mutate}
          isLoading={createTeamMutation.isPending}
          tournamentId={parseInt(tournamentId)}
        />
      ) : (
        <div className="bg-orange-900/20 border-2 border-orange-500 rounded-lg p-4">
          <div className="text-center">
            <h3 className="text-orange-400 font-pixel mb-2">✅ Registro Completo</h3>
            <p className="text-gray-300">Se ha alcanzado el límite máximo de {tournament?.max_teams} equipos</p>
            <p className="text-gray-400 text-sm mt-1">Elimina un equipo para poder registrar uno nuevo</p>
          </div>
        </div>
      )}

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

      {/* Chat Components */}
      <ChatToggle 
        isOpen={chatOpen} 
        onToggle={() => setChatOpen(!chatOpen)} 
      />
      <ChatSidebar 
        tournamentId={tournamentId} 
        isOpen={chatOpen} 
        onToggle={() => setChatOpen(false)} 
      />
    </div>
  )
}
