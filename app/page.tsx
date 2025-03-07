"use client"

import type React from "react"

import { useChat } from "@ai-sdk/react"
import { useState } from "react"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { ChatMessage } from "@/components/ChatMessage"
import { ChatInput } from "@/components/ChatInput"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { InfoIcon } from "lucide-react"

export default function Home() {
  const { messages, input, handleInputChange, handleSubmit, isLoading, error } = useChat()
  const [showDisclaimer, setShowDisclaimer] = useState(true)

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    handleSubmit(e)
    setShowDisclaimer(false)
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center">AI Counseling</CardTitle>
        </CardHeader>
        <CardContent className="h-[60vh] overflow-y-auto space-y-4">
          {showDisclaimer && (
            <Alert>
              <InfoIcon className="h-4 w-4" />
              <AlertTitle>Disclaimer</AlertTitle>
              <AlertDescription>
                This AI counselor is for informational purposes only and does not replace professional mental health
                support. If you're experiencing a crisis or need immediate help, please contact a qualified mental
                health professional or emergency services.
              </AlertDescription>
            </Alert>
          )}
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          {isLoading && <ChatMessage message={{ role: "assistant", content: "Thinking...", id: "loading" }} />}
          {error && (
            <Alert variant="destructive">
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error.message}</AlertDescription>
            </Alert>
          )}
        </CardContent>
        <CardFooter>
          <ChatInput
            input={input}
            handleInputChange={handleInputChange}
            handleSubmit={onSubmit}
            isLoading={isLoading}
          />
        </CardFooter>
      </Card>
    </div>
  )
}

