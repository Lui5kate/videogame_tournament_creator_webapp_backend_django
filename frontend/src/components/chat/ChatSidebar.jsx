import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '../../hooks/useAuth.jsx'
import { chatAPI } from '../../services/api'

export default function ChatSidebar({ tournamentId, isOpen, onToggle }) {
  const [message, setMessage] = useState('')
  const messagesEndRef = useRef(null)
  const queryClient = useQueryClient()
  const { user } = useAuth()

  const { data: messages = [], refetch } = useQuery({
    queryKey: ['chat-messages', tournamentId],
    queryFn: () => chatAPI.getMessages(parseInt(tournamentId)).then(res => {
      return res.data
    }),
    refetchInterval: 2000,
    enabled: isOpen
  })

  const sendMessageMutation = useMutation({
    mutationFn: chatAPI.sendMessage,
    onSuccess: async () => {
      setMessage('')
      setTimeout(() => refetch(), 500)
    },
    onError: (error) => {
      console.error('Error sending message:', error)
    }
  })

  const handleSendMessage = (e) => {
    e.preventDefault()
    if (!message.trim() || !user) return

    sendMessageMutation.mutate({
      tournament: parseInt(tournamentId),
      message: message.trim()
    })
  }

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isOpen])

  const getMessageIcon = (messageType) => {
    const icons = {
      user: '💬',
      system: '🤖',
      celebration: '🎉'
    }
    return icons[messageType] || icons.user
  }

  const recentMessages = messages.slice(-20)

  if (!isOpen) return null

  return (
    <div className="fixed right-0 top-16 bottom-0 w-[30%] min-w-[320px] bg-surface/95 backdrop-blur-sm border-l-2 border-primary/30 z-40 flex flex-col chat-sidebar">
      {/* Header */}
      <div className="bg-primary/20 p-3 border-b border-primary/30">
        <div className="flex items-center justify-between">
          <div className="pixel-font text-accent text-sm">💬 Chat del Torneo</div>
          <div className="flex items-center gap-2">
            <Link
              to={`/tournaments/${tournamentId}/chat`}
              className="text-secondary hover:text-accent text-lg"
              title="Abrir chat completo"
            >
              ⤢
            </Link>
            <button
              onClick={onToggle}
              className="text-accent hover:text-primary text-lg"
              title="Cerrar chat"
            >
              ✕
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2 chat-messages">
        {recentMessages.map((msg) => (
          <div key={msg.id} className="text-xs chat-message">
            <div className="flex items-start gap-2">
              <span className="text-sm">{getMessageIcon(msg.message_type)}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1">
                  <span className="font-bold text-accent pixel-font text-xs truncate">
                    {msg.display_name}
                  </span>
                  <span className="text-gray-500 text-xs">
                    {new Date(msg.created_at).toLocaleTimeString('es-ES', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </span>
                  {msg.user_type === 'admin' && (
                    <span className="text-xs bg-accent/20 text-accent px-1 rounded pixel-font">
                      👑
                    </span>
                  )}
                </div>
                <div className="text-white text-xs break-words">{msg.message}</div>
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-primary/30 p-3">
        <form onSubmit={handleSendMessage} className="space-y-2">
          <div className="flex gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Mensaje..."
              className="flex-1 p-2 bg-background border border-primary rounded text-blue-500 placeholder-gray-500 text-xs"
              autoComplete="off"
              disabled={sendMessageMutation.isPending || !user}
              required
            />
            <button
              type="submit"
              disabled={sendMessageMutation.isPending || !message.trim() || !user}
              className="bg-gradient-to-r from-primary to-secondary text-white px-3 py-2 rounded pixel-font text-xs hover:shadow-lg transition-all duration-200 disabled:opacity-50"
            >
              🚀
            </button>
          </div>
          {user && (
            <div className="text-xs text-gray-400 pixel-font">
              Como: <span className="text-accent">
                {user.profile ? `${user.profile.first_name} ${user.profile.last_name}` : user.username}
              </span>
            </div>
          )}
        </form>
      </div>
    </div>
  )
}
