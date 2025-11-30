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
        onOpen?.()
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          setLastMessage(data)
          onMessage?.(data)
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error)
        }
      }

      ws.onerror = (error) => {
        console.error("🔌 WebSocket error:", error)
        console.error("WebSocket URL:", url)
        console.error("WebSocket readyState:", ws.readyState)
        onError?.(error)
      }

      ws.onclose = () => {
        setIsConnected(false)
        onClose?.()

        if (shouldReconnectRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, reconnectInterval)
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
  }
}

