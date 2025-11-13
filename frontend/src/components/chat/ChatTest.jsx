import { useState } from 'react'
import { chatAPI } from '../../services/api'

export default function ChatTest({ tournamentId }) {
  const [username, setUsername] = useState('')
  const [message, setMessage] = useState('')
  const [response, setResponse] = useState(null)
  const [error, setError] = useState(null)

  const handleTest = async () => {
    try {
      setError(null)
      setResponse(null)
      
      console.log('Testing with:', { tournament: parseInt(tournamentId), username, message })
      
      const result = await chatAPI.sendMessage({
        tournament: parseInt(tournamentId),
        username: username,
        message: message
      })
      
      setResponse(result.data)
      setMessage('')
      console.log('Success:', result.data)
    } catch (err) {
      setError(err.response?.data || err.message)
      console.error('Error:', err)
    }
  }

  return (
    <div className="bg-red-900/20 border-2 border-red-500 rounded-lg p-4 m-4">
      <h3 className="text-red-400 pixel-font mb-4">🔧 Chat Debug Test</h3>
      
      <div className="space-y-3">
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          className="w-full p-2 bg-background border border-accent rounded text-white"
        />
        
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Message"
          className="w-full p-2 bg-background border border-accent rounded text-white"
        />
        
        <button
          onClick={handleTest}
          className="bg-red-500 text-white px-4 py-2 rounded pixel-font"
        >
          Test Send
        </button>
      </div>

      {response && (
        <div className="mt-4 p-3 bg-green-900/20 border border-green-500 rounded">
          <h4 className="text-green-400 pixel-font">Success:</h4>
          <pre className="text-xs text-white">{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-900/20 border border-red-500 rounded">
          <h4 className="text-red-400 pixel-font">Error:</h4>
          <pre className="text-xs text-white">{JSON.stringify(error, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
