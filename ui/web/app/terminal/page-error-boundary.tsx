"use client"

import React from "react"

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class TerminalErrorBoundary extends React.Component<
  { children: React.ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Terminal page error:", error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center h-full p-8">
          <div className="text-center space-y-4 max-w-md">
            <h1 className="text-2xl font-bold text-destructive">Terminal Error</h1>
            <p className="text-muted-foreground">
              {this.state.error?.message || "An error occurred loading the terminal"}
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null })
                window.location.reload()
              }}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md"
            >
              Reload Page
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

