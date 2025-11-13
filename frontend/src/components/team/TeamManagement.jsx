import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { teamAPI } from '../../services/api'

export default function TeamManagement({ tournamentId }) {
  const [selectedPlayer, setSelectedPlayer] = useState('')
  const [selectedTeam, setSelectedTeam] = useState('')
  const [isCaptain, setIsCaptain] = useState(false)
  const queryClient = useQueryClient()

  const { data: teams = [], isLoading: teamsLoading } = useQuery({
    queryKey: ['teams', tournamentId],
    queryFn: () => teamAPI.getByTournament(tournamentId).then(res => res.data || [])
  })

  const { data: availablePlayers = [], isLoading: playersLoading } = useQuery({
    queryKey: ['available-players', tournamentId],
    queryFn: () => teamAPI.getAvailablePlayers(tournamentId).then(res => res.data || [])
  })

  const assignPlayerMutation = useMutation({
    mutationFn: teamAPI.assignPlayer,
    onSuccess: () => {
      queryClient.invalidateQueries(['teams', tournamentId])
      queryClient.invalidateQueries(['available-players', tournamentId])
      setSelectedPlayer('')
      setSelectedTeam('')
      setIsCaptain(false)
    }
  })

  const removePlayerMutation = useMutation({
    mutationFn: ({ teamId, userId }) => teamAPI.removePlayer(teamId, userId),
    onSuccess: () => {
      queryClient.invalidateQueries(['teams', tournamentId])
      queryClient.invalidateQueries(['available-players', tournamentId])
    }
  })

  const handleAssignPlayer = (e) => {
    e.preventDefault()
    if (!selectedPlayer || !selectedTeam) return

    assignPlayerMutation.mutate({
      user_id: parseInt(selectedPlayer),
      team_id: parseInt(selectedTeam),
      is_captain: isCaptain
    })
  }

  const handleRemovePlayer = (teamId, userId) => {
    if (confirm('¿Estás seguro de remover este jugador del equipo?')) {
      removePlayerMutation.mutate({ teamId, userId })
    }
  }

  if (teamsLoading || playersLoading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin text-4xl mb-4">⚙️</div>
        <p className="text-gray-400">Cargando equipos y jugadores...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Formulario de Asignación */}
      <div className="bg-slate-800/50 backdrop-blur-sm border-2 border-orange-500/30 rounded-lg p-6">
        <h3 className="text-xl font-bold text-orange-400 mb-4 pixel-font">
          👥 ASIGNAR JUGADORES
        </h3>
        
        <form onSubmit={handleAssignPlayer} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Selector de Jugador */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Jugador
              </label>
              <select
                value={selectedPlayer}
                onChange={(e) => setSelectedPlayer(e.target.value)}
                className="w-full bg-slate-700 border-2 border-slate-600 rounded-lg px-3 py-2 text-blue-500 focus:border-orange-500 focus:outline-none"
                required
              >
                <option value="">Seleccionar jugador...</option>
                {Array.isArray(availablePlayers) && availablePlayers
                  .filter(player => !player.current_team)
                  .map(player => (
                    <option key={player.id} value={player.id}>
                      {player.full_name} ({player.attuid})
                    </option>
                  ))}
              </select>
            </div>

            {/* Selector de Equipo */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Equipo
              </label>
              <select
                value={selectedTeam}
                onChange={(e) => setSelectedTeam(e.target.value)}
                className="w-full bg-slate-700 border-2 border-slate-600 rounded-lg px-3 py-2 text-blue-500 focus:border-orange-500 focus:outline-none"
                required
              >
                <option value="">Seleccionar equipo...</option>
                {Array.isArray(teams) && teams.map(team => (
                  <option key={team.id} value={team.id}>
                    {team.name} ({team.players?.length || 0}/2)
                  </option>
                ))}
              </select>
            </div>

            {/* Checkbox Capitán */}
            <div className="flex items-end">
              <label className="flex items-center space-x-2 text-gray-300">
                <input
                  type="checkbox"
                  checked={isCaptain}
                  onChange={(e) => setIsCaptain(e.target.checked)}
                  className="w-4 h-4 text-orange-500 bg-slate-700 border-slate-600 rounded focus:ring-orange-500"
                />
                <span>👑 Capitán</span>
              </label>
            </div>
          </div>

          <button
            type="submit"
            disabled={!selectedPlayer || !selectedTeam || assignPlayerMutation.isLoading}
            className="bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold py-2 px-6 rounded-lg transition-all duration-200 pixel-font"
          >
            {assignPlayerMutation.isLoading ? '⏳ Asignando...' : '✅ Asignar Jugador'}
          </button>
        </form>
      </div>

      {/* Lista de Equipos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.isArray(teams) && teams.map(team => (
          <div key={team.id} className="bg-slate-800/50 backdrop-blur-sm border-2 border-slate-600 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-lg font-bold text-orange-400 pixel-font">
                {team.name}
              </h4>
              <span className="text-sm text-gray-400">
                {team.players?.length || 0}/2 jugadores
              </span>
            </div>

            <div className="space-y-2">
              {team.players?.length > 0 ? (
                team.players.map(player => (
                  <div key={player.id} className="flex items-center justify-between bg-slate-700/50 rounded-lg p-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">
                        {player.is_captain ? '👑' : '🎮'}
                      </span>
                      <div>
                        <p className="text-white font-medium">
                          {player.user_info?.full_name || player.name}
                        </p>
                        <p className="text-xs text-gray-400">
                          {player.user_info?.attuid}
                          {player.is_captain && ' • Capitán'}
                        </p>
                      </div>
                    </div>
                    
                    {player.user_info && (
                      <button
                        onClick={() => handleRemovePlayer(team.id, player.user_info.id)}
                        className="text-red-400 hover:text-red-300 transition-colors"
                        title="Remover jugador"
                      >
                        ❌
                      </button>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-gray-400">
                  <p>🚫 Sin jugadores asignados</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Jugadores Sin Asignar */}
      {Array.isArray(availablePlayers) && availablePlayers.filter(p => !p.current_team).length > 0 && (
        <div className="bg-slate-800/50 backdrop-blur-sm border-2 border-yellow-500/30 rounded-lg p-6">
          <h3 className="text-xl font-bold text-yellow-400 mb-4 pixel-font">
            🎯 JUGADORES SIN ASIGNAR
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {Array.isArray(availablePlayers) && availablePlayers
              .filter(player => !player.current_team)
              .map(player => (
                <div key={player.id} className="bg-slate-700/50 rounded-lg p-3">
                  <p className="text-white font-medium">{player.full_name}</p>
                  <p className="text-xs text-gray-400">{player.attuid}</p>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}
