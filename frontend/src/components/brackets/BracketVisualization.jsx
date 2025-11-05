import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { matchAPI } from '../../services/api'
import MatchCard from './MatchCard'

export default function BracketVisualization({ tournamentId }) {
  const queryClient = useQueryClient()

  const { data: matches, isLoading } = useQuery({
    queryKey: ['matches', tournamentId],
    queryFn: () => matchAPI.getByTournament(tournamentId).then(res => res.data)
  })

  const generateBracketsMutation = useMutation({
    mutationFn: matchAPI.generateBrackets,
    onSuccess: () => {
      queryClient.invalidateQueries(['matches', tournamentId])
      queryClient.invalidateQueries(['tournament', tournamentId])
    }
  })

  const handleGenerateBrackets = () => {
    generateBracketsMutation.mutate({ tournament_id: tournamentId })
  }

  if (isLoading) {
    return (
      <div className="text-center text-white pixel-font">
        <div className="animate-pulse">🎮 Cargando brackets...</div>
      </div>
    )
  }

  if (!matches || matches.length === 0) {
    return (
      <div className="text-center space-y-6">
        <div className="text-gray-400 pixel-font">
          <div className="text-4xl mb-4">🏆</div>
          <div>No hay brackets generados</div>
        </div>
        <button
          onClick={handleGenerateBrackets}
          disabled={generateBracketsMutation.isPending}
          className="bg-gradient-to-r from-primary to-secondary text-white px-6 py-3 rounded-lg pixel-font text-sm hover:shadow-lg hover:shadow-primary/50 transition-all duration-200 hover:scale-105 disabled:opacity-50"
        >
          {generateBracketsMutation.isPending ? '⚡ Generando...' : '🎯 Generar Brackets'}
        </button>
      </div>
    )
  }

  // Group matches by bracket type and round
  const groupedMatches = matches.reduce((acc, match) => {
    const key = `${match.bracket_type}_${match.round_number}`
    if (!acc[key]) acc[key] = []
    acc[key].push(match)
    return acc
  }, {})

  // Separate brackets
  const winnersBracket = Object.keys(groupedMatches)
    .filter(key => key.startsWith('winners'))
    .sort()
    .map(key => ({ key, matches: groupedMatches[key] }))

  const losersBracket = Object.keys(groupedMatches)
    .filter(key => key.startsWith('losers'))
    .sort()
    .map(key => ({ key, matches: groupedMatches[key] }))

  const finalMatches = Object.keys(groupedMatches)
    .filter(key => key.includes('grand_final') || key.includes('final_reset'))
    .sort()
    .map(key => ({ key, matches: groupedMatches[key] }))

  return (
    <div className="space-y-8">
      {/* Winners Bracket */}
      {winnersBracket.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-accent pixel-font flex items-center gap-2">
            🏆 Winners Bracket
          </h3>
          <div className="space-y-6">
            {winnersBracket.map(({ key, matches }) => (
              <div key={key} className="space-y-2">
                <h4 className="text-sm text-gray-300 pixel-font">
                  Ronda {matches[0]?.round_number}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {matches.map(match => (
                    <MatchCard 
                      key={match.id} 
                      match={match} 
                      tournamentId={tournamentId} 
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Losers Bracket */}
      {losersBracket.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-secondary pixel-font flex items-center gap-2">
            🔄 Losers Bracket
          </h3>
          <div className="space-y-6">
            {losersBracket.map(({ key, matches }) => (
              <div key={key} className="space-y-2">
                <h4 className="text-sm text-gray-300 pixel-font">
                  Ronda {matches[0]?.round_number}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {matches.map(match => (
                    <MatchCard 
                      key={match.id} 
                      match={match} 
                      tournamentId={tournamentId} 
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Grand Final */}
      {finalMatches.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-2xl font-bold text-accent pixel-font flex items-center gap-2 justify-center">
            👑 Gran Final
          </h3>
          <div className="flex justify-center">
            <div className="grid grid-cols-1 gap-4 max-w-md">
              {finalMatches.map(({ matches }) =>
                matches.map(match => (
                  <MatchCard 
                    key={match.id} 
                    match={match} 
                    tournamentId={tournamentId} 
                  />
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tournament Progress */}
      <div className="bg-surface/50 rounded-lg p-4 border border-primary/30">
        <h4 className="text-lg font-bold text-accent pixel-font mb-3">📊 Progreso del Torneo</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="space-y-1">
            <div className="text-2xl">⏳</div>
            <div className="text-sm text-gray-300 pixel-font">Pendientes</div>
            <div className="text-accent font-bold">
              {matches.filter(m => m.status === 'pending').length}
            </div>
          </div>
          <div className="space-y-1">
            <div className="text-2xl">🎮</div>
            <div className="text-sm text-gray-300 pixel-font">En Progreso</div>
            <div className="text-blue-400 font-bold">
              {matches.filter(m => m.status === 'in_progress').length}
            </div>
          </div>
          <div className="space-y-1">
            <div className="text-2xl">✅</div>
            <div className="text-sm text-gray-300 pixel-font">Completadas</div>
            <div className="text-green-400 font-bold">
              {matches.filter(m => m.status === 'completed').length}
            </div>
          </div>
          <div className="space-y-1">
            <div className="text-2xl">🏆</div>
            <div className="text-sm text-gray-300 pixel-font">Total</div>
            <div className="text-white font-bold">
              {matches.length}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
