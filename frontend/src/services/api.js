import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const tournamentAPI = {
  getAll: () => api.get('/tournaments/'),
  create: (data) => api.post('/tournaments/', data),
  getById: (id) => api.get(`/tournaments/${id}/`),
  update: (id, data) => api.put(`/tournaments/${id}/`, data),
  delete: (id) => api.delete(`/tournaments/${id}/`),
  start: (id) => api.post(`/tournaments/${id}/start/`),
  getStats: (id) => api.get(`/tournaments/${id}/stats/`),
}

export const teamAPI = {
  getAll: (tournamentId) => api.get('/teams/', { 
    params: tournamentId ? { tournament: tournamentId } : {} 
  }),
  create: (data) => api.post('/teams/', data),
  update: (id, data) => api.put(`/teams/${id}/`, data),
  delete: (id) => api.delete(`/teams/${id}/`),
  uploadPhoto: (id, formData) => api.post(`/teams/${id}/upload_photo/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
}

export const gameAPI = {
  getAll: () => api.get('/games/'),
  getPredefined: () => api.get('/games/predefined/'),
}

export const matchAPI = {
  getAll: () => api.get('/matches/'),
  getById: (id) => api.get(`/matches/${id}/`),
  getByTournament: (tournamentId) => api.get(`/matches/?tournament=${tournamentId}`),
  create: (data) => api.post('/matches/', data),
  update: (id, data) => api.put(`/matches/${id}/`, data),
  delete: (id) => api.delete(`/matches/${id}/`),
  declareWinner: (data) => api.post('/matches/declare_winner/', data),
  generateBrackets: (data) => api.post('/matches/generate-brackets/', data),
  getVisualization: (tournamentId) => api.get(`/matches/visualization/?tournament=${tournamentId}`),
  getNextMatches: (tournamentId) => api.get(`/matches/next-matches/?tournament=${tournamentId}`),
  startMatch: (id) => api.post(`/matches/${id}/start-match/`)
}

export default api
