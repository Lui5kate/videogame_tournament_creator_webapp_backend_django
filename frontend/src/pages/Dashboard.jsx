import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { tournamentAPI } from '../services/api'
import TournamentCard from '../components/tournament/TournamentCard'
import CreateTournamentModal from '../components/tournament/CreateTournamentModal'

export default function Dashboard() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  
  const { data: tournaments, isLoading } = useQuery({
    queryKey: ['tournaments'],
    queryFn: () => tournamentAPI.getAll().then(res => res.data)
  })

  if (isLoading) return <div className="text-center">Cargando...</div>

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-3xl font-pixel text-primary">Torneos</h2>
        <button 
          onClick={() => setShowCreateModal(true)}
          className="btn-primary"
        >
          + Crear Torneo
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tournaments?.map(tournament => (
          <TournamentCard key={tournament.id} tournament={tournament} />
        ))}
      </div>

      {showCreateModal && (
        <CreateTournamentModal onClose={() => setShowCreateModal(false)} />
      )}
    </div>
  )
}
