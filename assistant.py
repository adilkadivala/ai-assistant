
import json

from groq import Groq
from config import GROQ_API_KEY, MODEL
from schema import REQUIRED_FIELDS

client = Groq(api_key=GROQ_API_KEY)

## system prompt ...
SYSTEM_PROMPT = """
    You're a helpful assistant that process on the natural language,understands and procees user prompts, and replys just in the STRUCTURE JSON formate ONLY,

    SUPPORTED tools:
        - send_email
        - draft_email
        - schedule_meeting

    OUTPUT MUST BE STRICT JSON ONLY! 


    schema:{
        "tool": "...",
        "confidence": 0-1,
        "args": {},
        "missing_fields": [],
        "follow_up_question": null
    }


    required fields for each tool:
        - send_email: to, subject, body
        - draft_email: to, subject, body
        - schedule_meeting: participants, date_or_time, duration_minutes

    CRITICAL: Return RAW JSON only. No markdown. No backticks. No ```json. Just the JSON object starting with { and ending with }.

    IMPORTANT: participants must always be a JSON array e.g. ["Priya"], never a plain string.to must always be a JSON array e.g. ["Rahul"], never a plain string.

    
    RULES:    
        - If the user prompt is not clear, you should ask follow up question to get more information, and list the missing fields in the "missing_fields" array.
        
        - If the user prompt is clear and you have all the information you need, you should call the appropriate tool and fill in the "tool" and "args" fields accordingly.
        
        - The "confidence" field should reflect how confident you are in your understanding of the user's intent, with 1 being completely confident and 0 being not confident at all.
        
        - Always respond in the specified JSON format, and do not include any additional text or explanations outside of the JSON structure.
        
        - if user prompt is not supports any of the tools, you should respond with tool as null and confidence as 0, and ask follow up question to show your assist on the send_email, draft_email, schedule_metting , EXAMPLE :  user prompt : "I want to search for a restaurant", so your response should be :
        schema:{
            "tool": null,
            "confidence": 0,
            "args": {},
            "missing_fields": [],
            "follow_up_question": "Hey! sorry for the inconviniet! I can help with send_email, draft_email, and schedule_meeting."
        }
"""

### model calling ...
def call_model(user_prompt: str):
    response = client.chat.completions.create(
        model=MODEL,
        messages = [
            {"role":"system", "content":SYSTEM_PROMPT},
            {"role":"user", "content":user_prompt}
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return {
            "tool":None,
            "confidence":0,
            "args":{},
            "missing_fields":[],
            "follow_up_question":"Hey! I'm your assistant for send_email, draft_email, and schedule_meeting. How can I help?"
        }

#### check if the required fields are present, if not add the missing fields to the response and add follow up question to response ...
def validate_prompt(response: dict):
    tool = response.get("tool")
    args = response.get("args", {})

    ### Check if the tool is not supported, early return with
    if not tool:  
        return response 

    required = REQUIRED_FIELDS.get(tool, [])
    messing = []

    for field in required:
        if field not in args:
            messing.append(field)

    response["missing_fields"] = messing

    ### itrate over the missing fields and add follow up question to response
    if messing:
        if tool == "send_email":
            question = "Hey ! I need some more information to send the email, can you please provide the following details: "
            for field in messing:
                question += f"{field}, "
            response["follow_up_question"] = question.strip(", ")    
        elif tool == "draft_email":
            question = "Hey ! I need some more information to draft the email, can you please provide the following details: "
            for field in messing:
                question += f"{field}, "
            response["follow_up_question"] = question.strip(", ")
        elif tool == "schedule_meeting":
            question = "Hey ! I need some more information to schedule the meeting, can you please provide the following details: "
            for field in messing:
                question += f"{field}, "
            response["follow_up_question"] = question.strip(", ")
    else:
        response["follow_up_question"] = None

    return response

###  mock execution when fields are complete ...
def execute_tool(response: dict):
    tool = response.get("tool")
    args = response.get("args", {})
    confidence = response.get("confidence", 0)

    if confidence < 0.5:
        return {
            "status": "error",
            "message": "I'm not confident enough to execute this action. Can you please provide more details?"
        }

    if tool == "send_email":
        # Mock sending email
        return {
            "status": "success",
            "message": f"Email sent to {args.get('to')} with subject '{args.get('subject')}'"
        }
    elif tool == "draft_email":
        # Mock drafting email
        return {
            "status": "success",
            "message": f"Email drafted to {args.get('to')} with subject '{args.get('subject')}'"
        }
    elif tool == "schedule_meeting":
        # Mock scheduling meeting
        return {
            "status": "success",
            "message": f"Meeting scheduled on {args.get('date')} at {args.get('time')} with participants {', '.join(args.get('participants', []))}"
        }
    else:
        return {
            "status": "error",
            "message": "Unsupported tool."
        }


def process_user_prompt(user_prompt: str):
    raw = call_model(user_prompt)
    final = validate_prompt(raw)
    return final