import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { chatAPI, tournamentAPI } from '../services/api'

export default function Chat() {
  const { id: tournamentId } = useParams()
  const [message, setMessage] = useState('')
  const [username, setUsername] = useState('')
  const [isUsernameSet, setIsUsernameSet] = useState(false)
  const messagesEndRef = useRef(null)
  const queryClient = useQueryClient()

  // Load username from localStorage on mount
  useEffect(() => {
    const savedUsername = localStorage.getItem('chat_username')
    if (savedUsername) {
      setUsername(savedUsername)
      setIsUsernameSet(true)
    }
  }, [])

  const { data: tournament } = useQuery({
    queryKey: ['tournament', tournamentId],
    queryFn: () => tournamentAPI.getById(tournamentId).then(res => res.data)
  })

  const { data: messages = [], isLoading, refetch } = useQuery({
    queryKey: ['chat-messages', tournamentId],
    queryFn: () => chatAPI.getMessages(parseInt(tournamentId)).then(res => {
      console.log('Messages fetched:', res.data.length)
      return res.data.reverse()
    }),
    refetchInterval: 2000
  })

  const sendMessageMutation = useMutation({
    mutationFn: chatAPI.sendMessage,
    onSuccess: async (data) => {
      console.log('Message sent successfully:', data)
      setMessage('')
      setTimeout(() => refetch(), 500)
    },
    onError: (error) => {
      console.error('Error sending message:', error)
      console.error('Error response:', error.response?.data)
      alert('Error al enviar mensaje: ' + (error.response?.data?.message || error.message))
    }
  })

  const handleSendMessage = (e) => {
    e.preventDefault()
    if (!message.trim()) return
    
    if (!isUsernameSet) {
      if (!username.trim() || username.trim().length < 2) {
        alert('El nombre debe tener al menos 2 caracteres')
        return
      }
      localStorage.setItem('chat_username', username.trim())
      setIsUsernameSet(true)
    }

    console.log('Sending message:', {
      tournament: parseInt(tournamentId),
      username: username.trim(),
      message: message.trim()
    })

    sendMessageMutation.mutate({
      tournament: parseInt(tournamentId),
      username: username.trim(),
      message: message.trim()
    })
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const getMessageStyle = (messageType) => {
    const styles = {
      user: 'bg-surface border-l-4 border-primary',
      system: 'bg-secondary/20 border-l-4 border-secondary',
      celebration: 'bg-accent/20 border-l-4 border-accent'
    }
    return styles[messageType] || styles.user
  }

  const getMessageIcon = (messageType) => {
    const icons = {
      user: '💬',
      system: '🤖',
      celebration: '🎉'
    }
    return icons[messageType] || icons.user
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-white pixel-font">
          <div className="animate-spin text-6xl mb-4">💬</div>
          <div className="text-xl">Cargando chat...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen bg-gradient-to-br from-background via-dark to-background flex flex-col overflow-hidden">
      {/* Header */}
      <div className="bg-surface/90 backdrop-blur-sm border-b-2 border-primary/30 p-2 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link 
              to={`/tournaments/${tournamentId}`}
              className="text-accent hover:text-primary transition-colors pixel-font flex items-center gap-2"
            >
              <span>←</span>
              <span>Volver al Torneo</span>
            </Link>
            <div className="text-xl pixel-font text-primary">
              💬 Chat - {tournament?.name}
            </div>
          </div>
          <div className="text-accent pixel-font text-sm">
            {messages.length} mensajes
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-hidden flex flex-col min-h-0">
        <div className="flex-1 overflow-y-auto p-2 space-y-1 chat-messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`p-3 rounded-lg chat-message ${getMessageStyle(msg.message_type)}`}>
              <div className="flex items-start gap-3">
                <div className="text-xl">{getMessageIcon(msg.message_type)}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold text-accent pixel-font text-sm">{msg.username}</span>
                    <span className="text-xs text-gray-400">
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="text-white text-sm">{msg.message}</div>
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="bg-surface/90 backdrop-blur-sm border-t-2 border-primary/30 p-2 flex-shrink-0">
          <form onSubmit={handleSendMessage} className="space-y-2">
            {!isUsernameSet && (
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Tu nombre..."
                className="w-full p-2 bg-background border-2 border-accent rounded text-blue-600 placeholder-gray-500 pixel-font text-sm"
                autoComplete="off"
                minLength={2}
                required
              />
            )}
            <div className="flex gap-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Escribe tu mensaje..."
                className="flex-1 p-2 bg-background border-2 border-primary rounded text-blue-600 placeholder-gray-500 text-sm"
                autoComplete="off"
                disabled={sendMessageMutation.isPending}
                required
              />
              <button
                type="submit"
                disabled={sendMessageMutation.isPending || !message.trim()}
                className="bg-gradient-to-r from-primary to-secondary text-white px-4 py-2 rounded pixel-font disabled:opacity-50 text-sm"
              >
                🚀
              </button>
            </div>
            {isUsernameSet && (
              <div className="text-xs text-gray-400 pixel-font">
                Como: <span className="text-accent">{username}</span>
                <button
                  type="button"
                  onClick={() => {
                    setIsUsernameSet(false)
                    setUsername('')
                    localStorage.removeItem('chat_username')
                  }}
                  className="ml-2 text-secondary hover:text-accent"
                >
                  (cambiar)
                </button>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  )
}
