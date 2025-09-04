import React, { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export default function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  async function sendMessage() {
    const text = input.trim()
    if (!text || loading) return
    setMessages(prev => [...prev, { role: 'user', text }])
    setInput('')
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      })
      const data = await res.json()
      const reply = data?.reply || 'I could not process that.'
      setMessages(prev => [...prev, { role: 'bot', text: reply }])
    } catch (e) {
      setMessages(prev => [...prev, { role: 'bot', text: 'Network error.' }])
    } finally {
      setLoading(false)
    }
  }

  async function sendSOS() {
    try {
      await fetch(`${API_BASE}/sos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ emergency: true, timestamp: new Date().toISOString() })
      })
      alert('SOS request sent')
    } catch (e) {
      alert('Failed to send SOS')
    }
  }

  function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: '0 auto' }}>
      <h2>Chatbot</h2>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          rows={2}
          style={{ flex: 1 }}
          placeholder="Describe your symptoms or ask a health question..."
        />
        <button onClick={sendMessage} disabled={loading}>Send</button>
        <button onClick={sendSOS}>SOS</button>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {messages.map((m, idx) => (
          <div key={idx} style={{
            alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
            background: m.role === 'user' ? '#e0ecff' : '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: 12,
            padding: 12,
            maxWidth: '70%'
          }}>
            <div style={{ fontSize: 12, opacity: 0.7, marginBottom: 4 }}>
              {m.role === 'user' ? 'You' : 'Aarogya AI'}
            </div>
            <div>{m.text}</div>
            <div style={{ fontSize: 10, opacity: 0.6, marginTop: 6 }}>
              This is general advice, not a medical diagnosis.
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}


