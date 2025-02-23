import * as React from 'react'
import { createRoot } from 'react-dom/client'
import ClaudeInterface from './components/claude_interface'

createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <ClaudeInterface />
  </React.StrictMode>
)