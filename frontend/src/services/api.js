import axios from 'axios'

const api = axios.create({
  baseURL: 'http://10.150.153.31:8097/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para añadir token automáticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar tokens expirados
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

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
  getAll: (tournamentId) => api.get('/teams/teams/', { 
    params: tournamentId ? { tournament: tournamentId } : {} 
  }),
  getById: (id) => api.get(`/teams/teams/${id}/`),
  getByTournament: (tournamentId) => api.get(`/teams/teams/?tournament=${tournamentId}`),
  create: (data) => api.post('/teams/teams/', data),
  update: (id, data) => api.put(`/teams/teams/${id}/`, data),
  delete: (id) => api.delete(`/teams/teams/${id}/`),
  uploadPhoto: (id, formData) => api.post(`/teams/teams/${id}/upload_photo/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getAvailablePlayers: (tournamentId) => api.get(`/teams/available-players/?tournament=${tournamentId}`),
  assignPlayer: (data) => api.post('/teams/assign-player/', data),
  removePlayer: (teamId, userId) => api.delete(`/teams/remove-player/${teamId}/${userId}/`),
  changeTeamName: (data) => api.post('/teams/change-team-name/', data),
  getMyTeam: (tournamentId) => api.get(`/teams/my-team/?tournament=${tournamentId}`)
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
  startMatch: (id) => api.post(`/matches/${id}/start-match/`),
  getActiveRound: (tournamentId) => api.get(`/matches/get_active_round/?tournament_id=${tournamentId}`),
  manualAdvance: (matchId) => api.post(`/matches/${matchId}/manual_advance/`),
  cleanupTournament: (tournamentId) => api.post('/matches/cleanup_tournament/', { tournament_id: tournamentId }),
  getAdvanceableMatches: (tournamentId) => api.get(`/matches/advanceable_matches/?tournament_id=${tournamentId}`)
}

export const chatAPI = {
  getMessages: (tournamentId) => api.get(`/messages/?tournament=${tournamentId}`),
  sendMessage: (data) => api.post('/messages/', data),
  getRoom: (tournamentId) => api.get(`/rooms/by-tournament/?tournament=${tournamentId}`),
  createRoom: (data) => api.post('/rooms/', data)
}

export const gameAPI = {
  getAll: () => api.get('/games/'),
  getById: (id) => api.get(`/games/${id}/`),
  create: (data) => api.post('/games/', data),
  update: (id, data) => api.patch(`/games/${id}/`, data),
  delete: (id) => api.delete(`/games/${id}/`),
  getPredefined: () => api.get('/games/predefined/'),
  createFromTemplate: (data) => api.post('/games/create-from-template/', data),
  uploadImage: (id, imageFile) => {
    const formData = new FormData()
    formData.append('image', imageFile)
    return api.post(`/games/${id}/upload-image/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

export default api
