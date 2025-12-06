import React, { useState, useRef, useEffect } from "react"
import { Send, Bot, User, Settings, MessageSquare } from "lucide-react"

type Message = {
  from: "user" | "assistant"
  text: string
  timestamp: Date
}

type WebSocketMessage = {
  info: string
  question: string
}

export default function Chat() {
  const [info, setInfo] = useState("")
  const [question, setQuestion] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Initialize WebSocket connection
    wsRef.current = new WebSocket('ws://localhost:8000/ws/chat/')

    wsRef.current.onopen = () => {
      console.log('WebSocket Connected')
    }

    wsRef.current.onmessage = (event) => {
      const response = JSON.parse(event.data)
      const assistantMessage: Message = {
        from: "assistant",
        text: response.answer || response.error || "An error occurred",
        timestamp: new Date()
      }
      setMessages(prev => [...prev, assistantMessage])
      setLoading(false)
    }

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error)
      setLoading(false)
    }

    wsRef.current.onclose = () => {
      console.log('WebSocket Disconnected')
    }

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
    }
  }, [question])

  function send() {
    if (!question.trim() || !wsRef.current) return

    const userMessage: Message = {
      from: "user",
      text: question,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setLoading(true)
    const currentQuestion = question
    setQuestion("")

    try {
      const message: WebSocketMessage = {
        info,
        question: currentQuestion
      }
      wsRef.current.send(JSON.stringify(message))
    } catch (e: any) {
      const errorMessage: Message = {
        from: "assistant",
        text: "❌ Connection error: " + e.message,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
      setLoading(false)
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const clearChat = () => {
    setMessages([])
  }

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-white">AI Assistant</h1>
            <p className="text-sm text-gray-400">Always here to help</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={clearChat}
            className="p-2 text-gray-400 hover:text-gray-300 hover:bg-gray-700 rounded-lg transition-colors"
            title="Clear chat"
          >
            <MessageSquare className="w-5 h-5" />
          </button>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 text-gray-400 hover:text-gray-300 hover:bg-gray-700 rounded-lg transition-colors"
            title="Settings"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </header>

      {/* Settings Panel */}
      {showSettings && (
        <div className="bg-gray-800 border-b border-gray-700 px-4 py-3">
          <div className="max-w-4xl mx-auto">
            <h3 className="text-sm font-medium text-gray-200 mb-2">Context Information</h3>
            <textarea
              className="w-full p-3 border border-gray-600 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-700 text-white placeholder-gray-400"
              placeholder="Add context information to help the AI understand your questions better..."
              value={info}
              onChange={e => setInfo(e.target.value)}
              rows={3}
            />
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-hidden">
        <div className="max-w-4xl mx-auto h-full flex flex-col">
          <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Bot className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-xl font-semibold text-white mb-2">How can I help you today?</h2>
                <p className="text-gray-400">Start a conversation by typing a message below.</p>
              </div>
            ) : (
              messages.map((message, idx) => (
                <div key={idx} className={`flex items-start space-x-3 ${message.from === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {message.from === 'assistant' && (
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                  )}
                  <div className={`group max-w-2xl ${message.from === 'user' ? 'order-first' : ''}`}>
                    <div className={`rounded-2xl px-4 py-3 ${
                      message.from === 'user' 
                        ? 'bg-blue-500 text-white ml-12' 
                        : 'bg-gray-800 border border-gray-700 shadow-sm text-white'
                    }`}>
                      <p className="whitespace-pre-wrap">{message.text}</p>
                    </div>
                    <div className={`text-xs text-gray-400 mt-1 ${message.from === 'user' ? 'text-right' : 'text-left'}`}>
                      {formatTime(message.timestamp)}
                    </div>
                  </div>
                  {message.from === 'user' && (
                    <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                      <User className="w-4 h-4 text-gray-600" />
                    </div>
                  )}
                </div>
              ))
            )}
            
            {loading && (
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="max-w-2xl">
                  <div className="bg-gray-800 border border-gray-700 shadow-sm rounded-2xl px-4 py-3">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                      <span className="text-sm text-gray-400">AI is thinking...</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input */}
      <div className="bg-gray-800 border-t border-gray-700 px-4 py-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end space-x-3">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                className="w-full p-4 pr-12 border border-gray-600 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent max-h-32 overflow-y-auto bg-gray-700 text-white placeholder-gray-400"
                placeholder="Type your message here..."
                value={question}
                onChange={e => setQuestion(e.target.value)}
                onKeyDown={e => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault()
                    send()
                  }
                }}
                rows={1}
              />
              <button
                onClick={send}
                disabled={loading || !question.trim()}
                className={`absolute right-2 bottom-2 p-2 rounded-full transition-all ${
                  loading || !question.trim()
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-blue-500 text-white hover:bg-blue-600 shadow-sm hover:shadow'
                }`}
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
          <div className="mt-2 text-xs text-gray-400 text-center">
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>
      </div>
    </div>
  )
}