import React from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import App from './pages/App.jsx'
import Chat from './pages/Chat.jsx'
import Login from './pages/Login.jsx'

const router = createBrowserRouter([
  { path: '/', element: <App /> },
  { path: '/chat', element: <Chat /> },
  { path: '/login', element: <Login /> }
])

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)


