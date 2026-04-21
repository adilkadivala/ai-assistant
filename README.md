#  Gmail + Calendar AI Assistant

A CLI-based AI assistant that understands natural language requests and converts them into structured actions for email and calendar operations.

Built for the WorkLLM Round 2 Assignment.

---

## What it does

Users type natural language requests like:

- _"Send an email to Rahul saying I will be late tomorrow"_
- _"Schedule a 30 minute meeting with Priya next Tuesday at 3pm"_
- _"Draft an email to the design team about Friday's release"_

The assistant interprets the request, extracts structured parameters, detects missing information, asks follow-up questions when needed, and returns a consistent JSON action.

---

## Architecture

```
User input (natural language)
        ↓
LLM (Groq / LLaMA 3.3) with structured system prompt
        ↓
Raw JSON response
        ↓
Validation layer (checks required fields per tool)
        ↓
Missing fields? → Ask follow-up question → Re-process combined input
        ↓
Complete? → Mock execute + print confirmation
```

---

## Project Structure

```
ai_assistant/
├── main.py          # Entry point — conversation loop and UI
├── assistant.py     # LLM call, validation, mock execution logic
├── schema.py        # Required fields per tool
├── config.py        # Environment variable loading
├── .env             # API keys (not committed)
└── README.md
```

---

## Supported Actions

### 1. `send_email`
Required fields: `to`, `subject`, `body`

### 2. `draft_email`
Required fields: `to`, `subject`, `body`

### 3. `schedule_meeting`
Required fields: `participants`, `date_or_time`

---

## Output Schema

Every response follows this consistent JSON structure:

```json
{
  "tool": "send_email | draft_email | schedule_meeting | null",
  "confidence": 0.0,
  "args": {},
  "missing_fields": [],
  "follow_up_question": null
}
```

---

## Missing Information Handling

When required fields are absent, the assistant asks exactly one concise follow-up question and re-processes the combined context.

**Example:**

```
You: Send an email to Priya
🤖: What is the subject and body of the email you want to send to Priya?
You: Tell her I won't attend today's meeting
✅ Email sent to Priya with subject 'Regarding today's meeting'
```

---

## Setup

**1. Clone the repo and create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**2. Install dependencies**
```bash
pip install groq python-dotenv
```

**3. Create a `.env` file**
```
GROQ_API_KEY=your_groq_api_key_here
MODEL=llama-3.3-70b-versatile
```

**4. Run**
```bash
python main.py
```

---

## Example Test Cases

**Complete request — executes directly:**
```
You: Schedule a meeting with Rahul and Priya next Tuesday at 3pm for 30 minutes
✅ Meeting scheduled on next Tuesday at 3pm with participants Rahul, Priya
```

**Incomplete request — asks follow-up:**
```
You: Send an email to John
🤖: What would you like the email to say?
You: Tell him the invoice is overdue
✅ Email sent to John with subject 'Regarding overdue invoice'
```

**Unsupported request — graceful fallback:**
```
You: Search for a restaurant near me
🤖: I can help with send_email, draft_email, and schedule_meeting. How can I assist?
```

**Draft email:**
```
You: Draft an email to the design team about Friday's release
✅ Email drafted to Design Team with subject 'Friday Release'
```


---

## Author

Adil Kadival — Full-Stack Engineer, GSoC 2025 Contributor