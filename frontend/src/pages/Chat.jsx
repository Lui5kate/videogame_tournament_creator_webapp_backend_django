import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '../hooks/useAuth.jsx'
import { chatAPI, tournamentAPI } from '../services/api'

export default function Chat() {
  const { id: tournamentId } = useParams()
  const [message, setMessage] = useState('')
  const messagesEndRef = useRef(null)
  const queryClient = useQueryClient()
  const { user } = useAuth()

  const { data: tournament } = useQuery({
    queryKey: ['tournament', tournamentId],
    queryFn: () => tournamentAPI.getById(tournamentId).then(res => res.data)
  })

  const { data: messages = [], isLoading, refetch } = useQuery({
    queryKey: ['chat-messages', tournamentId],
    queryFn: () => chatAPI.getMessages(parseInt(tournamentId)).then(res => {
      return res.data
    }),
    refetchInterval: 3000,
    enabled: !!tournamentId
  })

  const sendMessageMutation = useMutation({
    mutationFn: chatAPI.sendMessage,
    onSuccess: () => {
      setMessage('')
      refetch()
    },
    onError: (error) => {
      console.error('Error sending message:', error)
      alert('Error al enviar mensaje')
    }
  })

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!message.trim()) return

    sendMessageMutation.mutate({
      tournament: parseInt(tournamentId),
      message: message.trim()
    })
  }

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

  const displayName = user?.profile ? 
    `${user.profile.first_name} ${user.profile.last_name}` : 
    user?.username || 'Usuario'

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
            👤 {displayName}
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg) => (
          <div key={msg.id} className={`p-3 rounded-lg ${getMessageStyle(msg.message_type)}`}>
            <div className="flex items-start gap-3">
              <span className="text-lg flex-shrink-0">{getMessageIcon(msg.message_type)}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-primary pixel-font text-sm">
                    {msg.display_name}
                  </span>
                  <span className="text-xs text-gray-400">
                    {msg.formatted_time}
                  </span>
                  {msg.user_type === 'admin' && (
                    <span className="text-xs bg-accent/20 text-accent px-2 py-1 rounded pixel-font">
                      👑 ADMIN
                    </span>
                  )}
                </div>
                <p className="text-gray-200 break-words">{msg.message}</p>
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <div className="bg-surface/90 backdrop-blur-sm border-t-2 border-primary/30 p-4 flex-shrink-0">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Escribe tu mensaje..."
            className="flex-1 bg-background border-2 border-primary/30 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:border-primary focus:outline-none"
            disabled={sendMessageMutation.isLoading}
          />
          <button
            type="submit"
            disabled={!message.trim() || sendMessageMutation.isLoading}
            className="bg-primary hover:bg-primary/80 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-2 px-6 rounded-lg transition-colors pixel-font"
          >
            {sendMessageMutation.isLoading ? '⏳' : '📤'}
          </button>
        </form>
      </div>
    </div>
  )
}
