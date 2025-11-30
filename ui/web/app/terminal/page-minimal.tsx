"use client"

// Ultra-minimal terminal page to test if basic rendering works
export default function TerminalPageMinimal() {
  return (
    <div className="flex flex-col h-full w-full bg-background p-8">
      <h1 className="text-2xl font-bold mb-4">Trading Terminal (Test Page)</h1>
      <div className="p-4 border rounded bg-card">
        <p className="text-green-500">✅ If you see this, the page is working!</p>
        <p className="text-sm text-muted-foreground mt-2">
          This is a minimal test page to verify the route works.
        </p>
      </div>
    </div>
  )
}

