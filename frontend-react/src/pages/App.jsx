import React from 'react'
import { Link } from 'react-router-dom'

export default function App() {
  return (
    <div style={{ padding: 24 }}>
      <h1>Aarogya AI</h1>
      <p>Intelligent Healthcare Assistant</p>
      <div style={{ display: 'flex', gap: 12 }}>
        <Link to="/chat">Start Chat</Link>
        <Link to="/login">Login</Link>
      </div>
    </div>
  )
}


