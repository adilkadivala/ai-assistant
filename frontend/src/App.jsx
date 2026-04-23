import { useMemo, useState } from 'react'

function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Hi! I can help with send_email, draft_email, and schedule_meeting.',
      json: null,
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [combinedPrompt, setCombinedPrompt] = useState('')
  const [awaitingFollowUp, setAwaitingFollowUp] = useState(false)

  const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/chat'
  const canSend = useMemo(() => input.trim().length > 0 && !loading, [input, loading])

  const sendMessage = async (event) => {
    event.preventDefault()
    const prompt = input.trim()
    if (!prompt) {
      return
    }

    setMessages((prev) => [...prev, { role: 'user', text: prompt, json: null }])
    setInput('')
    setLoading(true)

    const promptToSend = awaitingFollowUp && combinedPrompt ? `${combinedPrompt}. ${prompt}` : prompt

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: promptToSend }),
      })
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`)
      }

      const data = await response.json()
      const hasMissingFields = Array.isArray(data.missing_fields) && data.missing_fields.length > 0
      const assistantText = data.follow_up_question || 'Action parsed successfully.'

      if (hasMissingFields) {
        setCombinedPrompt(promptToSend)
        setAwaitingFollowUp(true)
      } else {
        setCombinedPrompt('')
        setAwaitingFollowUp(false)
      }

      setMessages((prev) => [...prev, { role: 'assistant', text: assistantText, json: data }])
    } catch {
      setCombinedPrompt('')
      setAwaitingFollowUp(false)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: 'Could not reach backend API. Start `uvicorn api:app --reload` and retry.',
          json: null,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto flex h-full w-full max-w-5xl flex-col p-4 md:p-6">
      <header className="mb-4 rounded-xl bg-slate-900 px-5 py-4 text-white shadow-sm">
        <h1 className="text-xl font-semibold md:text-2xl">Gmail + Calendar AI Assistant</h1>
        <p className="mt-1 text-sm text-slate-300">Frontend connected to Python backend API</p>
      </header>

      <main className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="flex-1 space-y-4 overflow-y-auto p-4 md:p-6">
          {messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`max-w-3xl rounded-lg px-4 py-3 ${
                message.role === 'user'
                  ? 'ml-auto bg-indigo-600 text-white'
                  : 'mr-auto bg-slate-100 text-slate-900'
              }`}
            >
              <p className="text-sm md:text-base">{message.text}</p>
              {message.json && (
                <pre className="mt-3 overflow-x-auto rounded-md bg-slate-950 p-3 text-xs text-slate-100">
                  {JSON.stringify(message.json, null, 2)}
                </pre>
              )}
            </div>
          ))}
          {loading && (
            <div className="mr-auto rounded-lg bg-slate-100 px-4 py-3 text-sm text-slate-500">
              Thinking...
            </div>
          )}
        </div>
        <form onSubmit={sendMessage} className="flex gap-3 border-t border-slate-200 p-4 md:p-5">
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder={
              awaitingFollowUp
                ? 'Answer the follow-up question...'
                : 'Type your request...'
            }
            className="flex-1 rounded-lg border border-slate-300 px-4 py-3 text-sm outline-none ring-indigo-500 transition focus:ring-2 md:text-base"
          />
          <button
            type="submit"
            disabled={!canSend}
            className="rounded-lg bg-indigo-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-indigo-300 md:text-base"
          >
            Send
          </button>
        </form>
      </main>

      <footer className="mt-3 text-center text-xs text-slate-500">
        API endpoint: <code>{apiUrl}</code>
      </footer>
    </div>
  )
}

export default App
