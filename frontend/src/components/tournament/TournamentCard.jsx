import { Link } from 'react-router-dom'

export default function TournamentCard({ tournament, isAdmin = false }) {
  const statusColors = {
    setup: 'bg-gray-500',
    registration: 'bg-blue-500', 
    active: 'bg-green-500',
    completed: 'bg-purple-500'
  }

  const statusLabels = {
    setup: 'Configuración',
    registration: 'Registro Abierto',
    active: 'En Curso',
    completed: 'Finalizado'
  }

  const typeLabels = {
    single: 'Eliminación Simple',
    double: 'Eliminación Doble'
  }

  return (
    <div className="card hover:border-primary/50 transition-colors">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-bold text-primary">{tournament.name}</h3>
        <span className={`px-2 py-1 rounded text-xs ${statusColors[tournament.status]}`}>
          {statusLabels[tournament.status]}
        </span>
      </div>
      
      <p className="text-gray-300 mb-4">{tournament.description}</p>
      
      <div className="flex justify-between text-sm text-gray-400 mb-4">
        <span>Tipo: {typeLabels[tournament.tournament_type]}</span>
        <span>Equipos: {tournament.registered_teams_count || 0}/{tournament.max_teams}</span>
      </div>
      
      <div className="space-y-2">
        <Link 
          to={`/tournaments/${tournament.id}`}
          className="btn-primary w-full text-center block"
        >
          {isAdmin ? 'Gestionar Torneo' : 'Ver Torneo'}
        </Link>
        
        {/* Botones solo para administradores */}
        {isAdmin && (
          <button 
            onClick={() => {/* TODO: Implementar eliminación */}}
            className="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors w-full text-sm mt-2"
          >
            🗑️ Eliminar
          </button>
        )}
      </div>
    </div>
  )
}
