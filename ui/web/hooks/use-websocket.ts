"use client"

import { useEffect, useRef, useState, useCallback } from "react"

interface UseWebSocketOptions {
  url: string
  onMessage?: (data: any) => void
  onError?: (error: Event) => void
  onOpen?: () => void
  onClose?: () => void
  reconnect?: boolean
  reconnectInterval?: number
}

export function useWebSocket({
  url,
  onMessage,
  onError,
  onOpen,
  onClose,
  reconnect = true,
  reconnectInterval = 5000,
}: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<any>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const shouldReconnectRef = useRef(reconnect)
  const reconnectAttemptsRef = useRef(0)
  const maxReconnectAttempts = 2 // Reduce attempts - fail fast and use polling
  const [reconnectAttempts, setReconnectAttempts] = useState(0) // Expose to component

  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }, [])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    // Don't try to connect if URL is invalid
    if (!url || !url.startsWith("ws")) {
      setIsConnected(false)
      return
    }
    
    // Allow localhost in development
    const isLocalhost = typeof window !== "undefined" && window.location.origin.includes("localhost")
    if (!isLocalhost && url.includes("localhost")) {
      setIsConnected(false)
      return
    }

    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        reconnectAttemptsRef.current = 0 // Reset on successful connection
        onOpen?.()
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          // Handle ping/pong for keepalive
          if (data.type === "ping") {
            // Respond with pong if needed (server handles it)
            return
          }
          
          setLastMessage(data)
          onMessage?.(data)
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error)
        }
      }

      ws.onerror = (error) => {
        // Only log once - don't spam
        if (reconnectAttemptsRef.current === 0) {
          console.warn("🔌 WebSocket connection error (will use polling fallback)")
        }
        // Don't call onError to avoid spam
      }

      ws.onclose = (event) => {
        setIsConnected(false)
        onClose?.()

        // Only reconnect if we haven't exceeded max attempts and should reconnect
        if (shouldReconnectRef.current && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1
          setReconnectAttemptsState(reconnectAttemptsRef.current) // Update state
          // Exponential backoff: 1s, 2s, 4s, 8s, 16s
          const backoffDelay = Math.min(reconnectInterval * Math.pow(2, reconnectAttemptsRef.current - 1), 30000)
          if (reconnectAttemptsRef.current <= 2) {
            console.log(`🔌 WebSocket: Reconnecting in ${backoffDelay/1000}s (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`)
          }
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, backoffDelay)
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          // Stop trying after max attempts, but don't spam console
          if (reconnectAttemptsRef.current === maxReconnectAttempts) {
            console.warn("🔌 WebSocket: Stopped reconnecting after", maxReconnectAttempts, "attempts. Using polling fallback.")
          }
          setReconnectAttemptsState(maxReconnectAttempts) // Update state for UI
        }
      }
    } catch (error) {
      console.error("Failed to create WebSocket connection:", error)
      if (shouldReconnectRef.current) {
        reconnectTimeoutRef.current = setTimeout(() => {
          connect()
        }, reconnectInterval)
      }
    }
  }, [url, onMessage, onError, onOpen, onClose, reconnectInterval])

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  useEffect(() => {
    shouldReconnectRef.current = reconnect
  }, [reconnect])

  useEffect(() => {
    connect()

    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  return {
    isConnected,
    lastMessage,
    send,
    connect,
    disconnect,
    reconnectAttempts: reconnectAttemptsState, // Expose attempt count
  }
}

