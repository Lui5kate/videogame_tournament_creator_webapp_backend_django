import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, useRef, useEffect } from 'react'
import { matchAPI } from '../../services/api'
import MatchCard from './MatchCard'

export default function BracketVisualization({ tournamentId }) {
  const queryClient = useQueryClient()
  const containerRef = useRef(null)
  const [zoomLevel, setZoomLevel] = useState(1)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [panPosition, setPanPosition] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })

  const { data: matches, isLoading } = useQuery({
    queryKey: ['matches', tournamentId],
    queryFn: () => matchAPI.getByTournament(tournamentId).then(res => res.data)
  })

  const { data: activeRoundData } = useQuery({
    queryKey: ['activeRound', tournamentId],
    queryFn: () => matchAPI.getActiveRound(tournamentId).then(res => res.data),
    refetchInterval: 3000,
    enabled: !!matches && matches.length > 0
  })

  const generateBracketsMutation = useMutation({
    mutationFn: matchAPI.generateBrackets,
    onSuccess: () => {
      queryClient.invalidateQueries(['matches', tournamentId])
      queryClient.invalidateQueries(['tournament', tournamentId])
      queryClient.invalidateQueries(['activeRound', tournamentId])
    }
  })

  const cleanupMutation = useMutation({
    mutationFn: matchAPI.cleanupTournament,
    onSuccess: () => {
      queryClient.invalidateQueries(['matches', tournamentId])
      queryClient.invalidateQueries(['tournament', tournamentId])
      queryClient.invalidateQueries(['activeRound', tournamentId])
    }
  })

  // Zoom controls
  const handleZoomIn = () => setZoomLevel(prev => Math.min(prev + 0.2, 3))
  const handleZoomOut = () => setZoomLevel(prev => Math.max(prev - 0.2, 0.5))
  const handleResetZoom = () => {
    setZoomLevel(1)
    setPanPosition({ x: 0, y: 0 })
  }

  // Fullscreen toggle
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
    if (!isFullscreen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'auto'
    }
  }

  // Pan functionality
  const handleMouseDown = (e) => {
    if (e.target.closest('.match-card')) return // Don't pan when clicking match cards
    setIsDragging(true)
    setDragStart({ x: e.clientX - panPosition.x, y: e.clientY - panPosition.y })
  }

  const handleMouseMove = (e) => {
    if (!isDragging) return
    setPanPosition({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    })
  }

  const handleMouseUp = () => setIsDragging(false)

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.key === 'Escape' && isFullscreen) {
        toggleFullscreen()
      }
      if (e.key === '+' || e.key === '=') {
        e.preventDefault()
        handleZoomIn()
      }
      if (e.key === '-') {
        e.preventDefault()
        handleZoomOut()
      }
      if (e.key === '0') {
        e.preventDefault()
        handleResetZoom()
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [isFullscreen])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      document.body.style.overflow = 'auto'
    }
  }, [])

  const handleGenerateBrackets = () => {
    generateBracketsMutation.mutate({ tournament_id: tournamentId })
  }

  const handleCleanupTournament = () => {
    cleanupMutation.mutate(tournamentId)
  }

  const isRoundActive = (bracketType, roundNumber) => {
    if (!activeRoundData?.active_round) return false
    return activeRoundData.active_round.bracket_type === bracketType && 
           activeRoundData.active_round.round_number === roundNumber
  }

  const isRoundDisabled = (bracketType, roundNumber) => {
    if (!activeRoundData?.active_round) return false
    
    if (isRoundActive(bracketType, roundNumber)) return false
    
    const roundMatches = matches.filter(m => 
      m.bracket_type === bracketType && 
      m.round_number === roundNumber &&
      m.team1 && m.team2
    )
    
    const completedMatches = roundMatches.filter(m => m.status === 'completed')
    
    if (roundMatches.length > 0 && completedMatches.length === roundMatches.length) {
      return false
    }
    
    return true
  }

  const getRoundClasses = (bracketType, roundNumber) => {
    const baseClasses = "mb-6 p-6 rounded-xl border-2 transition-all duration-300 backdrop-blur-sm"
    
    if (isRoundActive(bracketType, roundNumber)) {
      return `${baseClasses} border-accent bg-gradient-to-br from-accent/30 to-primary/30 shadow-2xl shadow-accent/50 ring-2 ring-accent/50`
    } else if (isRoundDisabled(bracketType, roundNumber)) {
      return `${baseClasses} border-gray-600 bg-gray-800/20 opacity-40`
    } else {
      return `${baseClasses} border-gray-500 bg-surface/30 shadow-lg`
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-white pixel-font">
          <div className="animate-spin text-6xl mb-4">🎮</div>
          <div className="text-xl">Cargando brackets...</div>
        </div>
      </div>
    )
  }

  if (!matches || matches.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center space-y-8 max-w-md">
          <div className="text-gray-400 pixel-font">
            <div className="text-8xl mb-6">🏆</div>
            <div className="text-2xl mb-4">No hay brackets generados</div>
            <div className="text-sm text-gray-500">Genera los brackets para comenzar el torneo</div>
          </div>
          <button
            onClick={handleGenerateBrackets}
            disabled={generateBracketsMutation.isPending}
            className="bg-gradient-to-r from-primary to-secondary text-white px-8 py-4 rounded-xl pixel-font text-lg hover:shadow-2xl hover:shadow-primary/50 transition-all duration-300 hover:scale-105 disabled:opacity-50 transform"
          >
            {generateBracketsMutation.isPending ? '⚡ Generando...' : '🎯 Generar Brackets'}
          </button>
        </div>
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

  const finals = Object.keys(groupedMatches)
    .filter(key => key.startsWith('grand_final') || key.startsWith('final_reset'))
    .sort()
    .map(key => ({ key, matches: groupedMatches[key] }))

  const containerClasses = isFullscreen 
    ? "fixed inset-0 z-50 bg-background/95 backdrop-blur-lg"
    : "relative min-h-screen bg-gradient-to-br from-background via-dark to-background"

  return (
    <div className={containerClasses}>
      {/* Control Panel */}
      <div className="absolute top-4 right-4 z-10 flex gap-2">
        {/* Cleanup Button */}
        <button
          onClick={handleCleanupTournament}
          disabled={cleanupMutation.isPending}
          className="w-12 h-12 bg-secondary/20 hover:bg-secondary/40 rounded-lg flex items-center justify-center text-white transition-all duration-200 hover:scale-110 border border-secondary/20 disabled:opacity-50"
          title="Auto-avanzar equipos huérfanos"
        >
          {cleanupMutation.isPending ? '⚡' : '🧹'}
        </button>

        {/* Zoom Controls */}
        <div className="bg-surface/90 backdrop-blur-sm rounded-lg p-2 flex gap-1 border border-primary/20">
          <button
            onClick={handleZoomOut}
            className="w-10 h-10 bg-primary/20 hover:bg-primary/40 rounded-lg flex items-center justify-center text-white transition-all duration-200 hover:scale-110"
            title="Zoom Out (-)"
          >
            −
          </button>
          <div className="w-16 h-10 bg-background/50 rounded-lg flex items-center justify-center text-white pixel-font text-xs">
            {Math.round(zoomLevel * 100)}%
          </div>
          <button
            onClick={handleZoomIn}
            className="w-10 h-10 bg-primary/20 hover:bg-primary/40 rounded-lg flex items-center justify-center text-white transition-all duration-200 hover:scale-110"
            title="Zoom In (+)"
          >
            +
          </button>
          <button
            onClick={handleResetZoom}
            className="w-10 h-10 bg-secondary/20 hover:bg-secondary/40 rounded-lg flex items-center justify-center text-white transition-all duration-200 hover:scale-110"
            title="Reset (0)"
          >
            ⌂
          </button>
        </div>

        {/* Fullscreen Toggle */}
        <button
          onClick={toggleFullscreen}
          className="w-12 h-12 bg-accent/20 hover:bg-accent/40 rounded-lg flex items-center justify-center text-white transition-all duration-200 hover:scale-110 border border-accent/20"
          title={isFullscreen ? "Exit Fullscreen (Esc)" : "Fullscreen"}
        >
          {isFullscreen ? '⤓' : '⤢'}
        </button>
      </div>

      {/* Active Round Indicator */}
      {activeRoundData?.active_round && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10">
          <div className="bg-gradient-to-r from-accent to-primary text-white px-8 py-4 rounded-xl shadow-2xl shadow-accent/50 border border-accent/30 backdrop-blur-sm">
            <span className="pixel-font text-lg">
              🎯 Siguiente: {activeRoundData.active_round.bracket_type === 'winners' ? '🏆 Winners' : 
                            activeRoundData.active_round.bracket_type === 'losers' ? '🔄 Losers' : 
                            activeRoundData.active_round.bracket_type === 'grand_final' ? '👑 Gran Final' : '⚡ Reset Final'} 
              Round {activeRoundData.active_round.round_number}
            </span>
          </div>
        </div>
      )}

      {/* Bracket Container */}
      <div 
        ref={containerRef}
        className="bracket-viewport w-full h-full overflow-hidden cursor-grab active:cursor-grabbing"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ 
          cursor: isDragging ? 'grabbing' : 'grab'
        }}
      >
        <div 
          className="bracket-content transition-transform duration-200 ease-out"
          style={{
            transform: `scale(${zoomLevel}) translate(${panPosition.x}px, ${panPosition.y}px)`,
            transformOrigin: 'center center',
            minWidth: '100%',
            minHeight: '100%',
            padding: '80px 40px 40px 40px'
          }}
        >
          {/* Main Horizontal Bracket Container */}
          <div className="main-bracket">
            {/* Winners Bracket - Top */}
            <div className="winner-bracket mb-16">
              <h2 className="text-4xl font-bold text-accent mb-8 text-center pixel-font drop-shadow-lg">
                🏆 Winners Bracket
              </h2>
              <div className="flex gap-12 min-w-max pb-8">
                {winnersBracket.map(({ key, matches: roundMatches }, roundIndex) => {
                  const roundNumber = parseInt(key.split('_')[1])
                  return (
                    <div key={key} className="round-column flex-shrink-0 w-80">
                      <div className={`${getRoundClasses('winners', roundNumber)} h-full min-h-96`}>
                        <h3 className="text-2xl font-bold text-white mb-6 text-center pixel-font">
                          Round {roundNumber}
                          {isRoundActive('winners', roundNumber) && (
                            <div className="text-accent animate-pulse text-lg mt-2">🔥 ACTIVO</div>
                          )}
                          {isRoundDisabled('winners', roundNumber) && (
                            <div className="text-gray-500 text-lg mt-2">🔒 BLOQUEADO</div>
                          )}
                        </h3>
                        <div className="space-y-6">
                          {roundMatches.map(match => (
                            <div key={match.id} className="match-card">
                              <MatchCard
                                match={match}
                                tournamentId={tournamentId}
                                disabled={isRoundDisabled('winners', roundNumber)}
                              />
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )
                })}
                {/* Finals Column */}
                {finals.length > 0 && (
                  <div className="round-column flex-shrink-0 w-80">
                    <div className="p-6 rounded-xl border-2 border-accent bg-gradient-to-br from-accent/30 to-primary/30 shadow-2xl shadow-accent/50 h-full min-h-96">
                      <h3 className="text-2xl font-bold text-white mb-6 text-center pixel-font">
                        🥇 FINALES
                      </h3>
                      <div className="space-y-6">
                        {finals.map(({ matches: roundMatches }) => 
                          roundMatches.map(match => (
                            <div key={match.id} className="match-card">
                              <div className="text-center text-lg pixel-font text-accent mb-4">
                                {match.bracket_type === 'grand_final' ? '👑 Gran Final' : '⚡ Reset'}
                              </div>
                              <MatchCard
                                match={match}
                                tournamentId={tournamentId}
                                disabled={isRoundDisabled(match.bracket_type, 1)}
                              />
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Losers Bracket - Bottom */}
            <div className="loser-bracket">
              <h2 className="text-4xl font-bold text-secondary mb-8 text-center pixel-font drop-shadow-lg">
                🔄 Losers Bracket
              </h2>
              <div className="flex gap-12 min-w-max pb-8">
                {losersBracket.map(({ key, matches: roundMatches }, roundIndex) => {
                  const roundNumber = parseInt(key.split('_')[1])
                  return (
                    <div key={key} className="round-column flex-shrink-0 w-80">
                      <div className={`${getRoundClasses('losers', roundNumber)} min-h-96`}>
                        <h3 className="text-2xl font-bold text-white mb-6 text-center pixel-font">
                          Round {roundNumber}
                          {isRoundActive('losers', roundNumber) && (
                            <div className="text-accent animate-pulse text-lg mt-2">🔥 ACTIVO</div>
                          )}
                          {isRoundDisabled('losers', roundNumber) && (
                            <div className="text-gray-500 text-lg mt-2">🔒 BLOQUEADO</div>
                          )}
                        </h3>
                        <div className="space-y-6">
                          {roundMatches.map(match => (
                            <div key={match.id} className="match-card">
                              <MatchCard
                                match={match}
                                tournamentId={tournamentId}
                                disabled={isRoundDisabled('losers', roundNumber)}
                              />
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Help Text */}
      {isFullscreen && (
        <div className="absolute bottom-4 left-4 text-gray-400 pixel-font text-sm">
          <div>🖱️ Arrastra para mover • ⌨️ +/- para zoom • ESC para salir</div>
        </div>
      )}
    </div>
  )
}
