export default function ChatToggle({ isOpen, onToggle, messageCount = 0 }) {
  return (
    <button
      onClick={onToggle}
      className="fixed right-4 top-1/2 transform -translate-y-1/2 z-30 bg-gradient-to-r from-primary to-secondary text-white p-3 rounded-l-xl shadow-2xl hover:shadow-primary/50 transition-all duration-300 hover:scale-110 pixel-font chat-toggle"
      title={isOpen ? "Cerrar chat" : "Abrir chat"}
    >
      <div className="flex flex-col items-center gap-1">
        <span className="text-lg">{isOpen ? '✕' : '💬'}</span>
        <span className="text-xs">Chat</span>
        {messageCount > 0 && !isOpen && (
          <div className="absolute -top-2 -right-2 bg-accent text-background rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold">
            {messageCount > 99 ? '99+' : messageCount}
          </div>
        )}
      </div>
    </button>
  )
}
