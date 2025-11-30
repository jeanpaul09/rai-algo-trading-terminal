"use client"

// Minimal terminal page to test if it loads
export default function TerminalPageSimple() {
  return (
    <div className="flex flex-col h-full w-full bg-background p-8">
      <h1 className="text-2xl font-bold mb-4">Trading Terminal</h1>
      <p className="text-muted-foreground">Terminal page is loading...</p>
      <div className="mt-4 p-4 border rounded">
        <p>If you see this, the page component is working!</p>
        <p className="text-sm text-muted-foreground mt-2">
          Check the browser console (F12) for any errors.
        </p>
      </div>
    </div>
  )
}

