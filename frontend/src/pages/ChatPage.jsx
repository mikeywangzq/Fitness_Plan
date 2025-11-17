import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import VoiceInputButton from '../components/VoiceInputButton'
import '../styles/chat.css'

function ChatPage() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '你好！我是你的AI健身助手。我可以帮你制定训练计划、提供营养建议、追踪进度。你想从哪里开始？',
    },
  ])
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessageMutation = useMutation({
    mutationFn: async (message) => {
      const response = await axios.post('/api/chat/message', {
        message,
        conversation_id: conversationId,
        include_history: true,
      })
      return response.data
    },
    onSuccess: (data) => {
      setConversationId(data.conversation_id)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.message,
          intent: data.intent,
        },
      ])
    },
    onError: (error) => {
      console.error('Error sending message:', error)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '抱歉，发生了错误。请稍后再试。',
          error: true,
        },
      ])
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage = input.trim()
    setInput('')

    // Add user message to chat
    setMessages((prev) => [
      ...prev,
      {
        role: 'user',
        content: userMessage,
      },
    ])

    // Send to API
    sendMessageMutation.mutate(userMessage)
  }

  const quickActions = [
    '我想制定一个训练计划',
    '帮我分析今天的饮食',
    '查看我的进度',
    '我需要营养建议',
  ]

  const handleQuickAction = (action) => {
    setInput(action)
  }

  const handleVoiceTranscript = (transcript) => {
    setInput(transcript)
    // 自动聚焦到输入框
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }

  return (
    <div className="chat-page">
      <div className="chat-header">
        <h2>AI健身助手聊天</h2>
        <p>询问任何关于健身、训练、营养的问题</p>
      </div>

      <div className="chat-container">
        <div className="messages-container">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.role} ${message.error ? 'error' : ''}`}
            >
              <div className="message-avatar">
                {message.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <ReactMarkdown>{message.content}</ReactMarkdown>
                {message.intent && (
                  <span className="message-intent">意图: {message.intent}</span>
                )}
              </div>
            </div>
          ))}
          {sendMessageMutation.isPending && (
            <div className="message assistant">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {messages.length === 1 && (
          <div className="quick-actions">
            <p>快速开始：</p>
            <div className="quick-actions-grid">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickAction(action)}
                  className="quick-action-btn"
                >
                  {action}
                </button>
              ))}
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="chat-input-form">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="输入你的问题或点击麦克风..."
            disabled={sendMessageMutation.isPending}
            className="chat-input"
          />
          <VoiceInputButton
            onTranscript={handleVoiceTranscript}
            className="voice-button-inline"
          />
          <button
            type="submit"
            disabled={!input.trim() || sendMessageMutation.isPending}
            className="send-button"
          >
            发送
          </button>
        </form>
      </div>
    </div>
  )
}

export default ChatPage
