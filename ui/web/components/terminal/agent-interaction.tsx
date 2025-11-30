"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Send, Bot, User, Loader2 } from "lucide-react"
import type { AgentCommand } from "@/lib/types"
import { format } from "date-fns"

interface AgentInteractionProps {
  commands: AgentCommand[]
  onSendCommand: (command: string) => void
  isProcessing?: boolean
}

export function AgentInteraction({
  commands,
  onSendCommand,
  isProcessing = false,
}: AgentInteractionProps) {
  const [input, setInput] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isProcessing) {
      onSendCommand(input.trim())
      setInput("")
    }
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="border-b pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Bot className="h-5 w-5" />
          Agent Interaction
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0">
        {/* Command History */}
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {commands.length === 0 ? (
              <div className="text-center text-muted-foreground py-8 text-sm">
                <Bot className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>Send a command to the agent to start interacting.</p>
                <p className="text-xs mt-2">
                  Example: "Explain your current position in BTC" or "Run a backtest for MA Cross strategy"
                </p>
              </div>
            ) : (
              commands.map((cmd) => (
                <div key={cmd.id} className="space-y-2">
                  {/* User Command */}
                  <div className="flex items-start gap-3">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <User className="h-4 w-4 text-primary" />
                    </div>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">You</span>
                        <span className="text-xs text-muted-foreground">
                          {format(new Date(cmd.timestamp), "HH:mm:ss")}
                        </span>
                      </div>
                      <div className="bg-muted rounded-lg p-3 text-sm">
                        {cmd.command}
                      </div>
                    </div>
                  </div>

                  {/* Agent Response */}
                  {cmd.response && (
                    <div className="flex items-start gap-3 ml-11">
                      <div className="h-8 w-8 rounded-full bg-blue-500/10 flex items-center justify-center flex-shrink-0">
                        <Bot className="h-4 w-4 text-blue-500" />
                      </div>
                      <div className="flex-1 space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">Agent</span>
                          {cmd.status === "processing" && (
                            <Badge variant="outline" className="text-xs">
                              <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                              Processing
                            </Badge>
                          )}
                          {cmd.status === "completed" && (
                            <Badge variant="outline" className="text-xs text-green-500">
                              Completed
                            </Badge>
                          )}
                          {cmd.status === "failed" && (
                            <Badge variant="destructive" className="text-xs">
                              Failed
                            </Badge>
                          )}
                        </div>
                        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 text-sm whitespace-pre-wrap">
                          {cmd.response}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Processing Indicator */}
                  {cmd.status === "processing" && !cmd.response && (
                    <div className="flex items-start gap-3 ml-11">
                      <div className="h-8 w-8 rounded-full bg-blue-500/10 flex items-center justify-center flex-shrink-0">
                        <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Agent is thinking...
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </ScrollArea>

        {/* Command Input */}
        <div className="border-t p-4">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask the agent a question or give a command..."
              disabled={isProcessing}
              className="flex-1"
            />
            <Button type="submit" disabled={!input.trim() || isProcessing}>
              {isProcessing ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </div>
      </CardContent>
    </Card>
  )
}

