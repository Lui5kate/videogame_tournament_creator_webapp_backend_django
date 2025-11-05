import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { matchAPI } from '../../services/api'

export default function MatchCard({ match, tournamentId }) {
  const [isLoading, setIsLoading] = useState(false)
  const queryClient = useQueryClient()

  const declareWinnerMutation = useMutation({
    mutationFn: matchAPI.declareWinner,
    onSuccess: () => {
      queryClient.invalidateQueries(['matches', tournamentId])
      queryClient.invalidateQueries(['tournament', tournamentId])
      setIsLoading(false)
    },
    onError: () => setIsLoading(false)
  })

  const handleDeclareWinner = (winnerId) => {
    setIsLoading(true)
    declareWinnerMutation.mutate({
      match_id: match.id,
      winner_id: winnerId
    })
  }

  const getBracketTypeStyle = (type) => {
    const styles = {
      winners: 'border-accent bg-gradient-to-r from-primary/20 to-secondary/20',
      losers: 'border-secondary bg-gradient-to-r from-secondary/20 to-accent/20',
      grand_final: 'border-accent bg-gradient-to-r from-accent/30 to-primary/30 shadow-lg shadow-accent/50',
      final_reset: 'border-primary bg-gradient-to-r from-primary/30 to-secondary/30 shadow-lg shadow-primary/50'
    }
    return styles[type] || 'border-gray-600 bg-gray-800/50'
  }

  const getBracketTypeLabel = (type) => {
    const labels = {
      winners: '🏆 Winners',
      losers: '🔄 Losers', 
      grand_final: '👑 Gran Final',
      final_reset: '⚡ Reset Final'
    }
    return labels[type] || type
  }

  const getTeamButtonStyle = (team, isWinner, isCompleted) => {
    if (isWinner) return 'bg-green-600 text-white shadow-lg shadow-green-500/50 transform scale-105'
    if (isCompleted) return 'bg-gray-700 text-gray-400'
    return 'bg-surface hover:bg-primary/80 text-white hover:shadow-lg hover:shadow-primary/50 transition-all duration-200 hover:scale-105'
  }

  return (
    <div className={`border-2 rounded-lg p-4 transition-all duration-300 ${getBracketTypeStyle(match.bracket_type)}`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-3">
        <span className="text-sm font-bold text-accent pixel-font">
          {getBracketTypeLabel(match.bracket_type)} - R{match.round_number}
        </span>
        <span className="text-xs text-gray-400">
          Match #{match.match_number}
        </span>
      </div>

      {/* Game Info */}
      {match.game && (
        <div className="text-center mb-3 p-2 bg-background/50 rounded">
          <span className="text-2xl">{match.game.emoji}</span>
          <span className="text-sm text-gray-300 ml-2 pixel-font">{match.game.name}</span>
        </div>
      )}

      {/* Teams */}
      <div className="space-y-2">
        {match.team1 ? (
          <button
            onClick={() => handleDeclareWinner(match.team1.id)}
            disabled={match.status === 'completed' || isLoading}
            className={`w-full p-3 rounded text-left pixel-font text-sm ${getTeamButtonStyle(
              match.team1, 
              match.winner?.id === match.team1.id, 
              match.status === 'completed'
            )}`}
          >
            <div className="flex justify-between items-center">
              <span>{match.team1.name}</span>
              {match.winner?.id === match.team1.id && <span className="text-accent">🏆</span>}
            </div>
          </button>
        ) : (
          <div className="w-full p-3 bg-gray-800/50 rounded text-gray-500 text-center pixel-font text-sm">
            TBD
          </div>
        )}

        <div className="text-center text-accent font-bold pixel-font">VS</div>

        {match.team2 ? (
          <button
            onClick={() => handleDeclareWinner(match.team2.id)}
            disabled={match.status === 'completed' || isLoading}
            className={`w-full p-3 rounded text-left pixel-font text-sm ${getTeamButtonStyle(
              match.team2, 
              match.winner?.id === match.team2.id, 
              match.status === 'completed'
            )}`}
          >
            <div className="flex justify-between items-center">
              <span>{match.team2.name}</span>
              {match.winner?.id === match.team2.id && <span className="text-accent">🏆</span>}
            </div>
          </button>
        ) : (
          <div className="w-full p-3 bg-gray-800/50 rounded text-gray-500 text-center pixel-font text-sm">
            TBD
          </div>
        )}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="text-center mt-3 text-accent pixel-font text-sm animate-pulse">
          ⚡ Actualizando bracket...
        </div>
      )}

      {/* Status Indicator */}
      <div className="mt-2 text-center">
        {match.status === 'completed' && (
          <span className="text-green-400 text-xs pixel-font">✅ Completado</span>
        )}
        {match.status === 'in_progress' && (
          <span className="text-blue-400 text-xs pixel-font animate-pulse">🎮 En Progreso</span>
        )}
        {match.status === 'pending' && (
          <span className="text-gray-400 text-xs pixel-font">⏳ Pendiente</span>
        )}
      </div>
    </div>
  )
}
