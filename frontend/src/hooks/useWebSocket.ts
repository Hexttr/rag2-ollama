import { useEffect, useRef, useState } from 'react'
import type { WebSocketMessage } from '../types'

export const useWebSocket = (documentId: number | null) => {
  const [status, setStatus] = useState<string>('')
  const [message, setMessage] = useState<string>('')
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!documentId) return

    const wsUrl = `ws://localhost:8000/ws/document/${documentId}`
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data)
        
        if (data.type === 'status_update') {
          setStatus(data.status || '')
          setMessage(data.message || '')
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
    }

    wsRef.current = ws

    return () => {
      ws.close()
    }
  }, [documentId])

  return { status, message }
}



