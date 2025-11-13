import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Tournament from './pages/Tournament'
import Teams from './pages/Teams'
import Brackets from './pages/Brackets'

function App() {
  return (
    <div className="min-h-screen bg-dark">
      <header className="bg-dark-light border-b border-primary/20 p-4">
        <h1 className="text-2xl font-pixel text-primary">🎮 Videogame Tourney Maker</h1>
      </header>
      
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/tournaments/:id" element={<Tournament />} />
          <Route path="/tournaments/:id/teams" element={<Teams />} />
          <Route path="/tournaments/:id/brackets" element={<Brackets />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
