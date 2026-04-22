
import json

from groq import Groq
from config import MODEL, MODEL_API_KEY
from schema import REQUIRED_FIELDS

client = Groq(api_key=MODEL_API_KEY)

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
        - schedule_meeting: participants, date_or_time, duration_minutes (date_or_time will not be in a specific format, it can be any string that represents date or time, e.g. "tomorrow at 5pm", "next monday", "2023-08-15 14:00", etc.)

    CRITICAL: Return only and only JSON . No markdown. No backticks. No ```json. Just the JSON object starting with { and ending with }.

    IMPORTANT: response in just JOSN formate, regardless the prompt is complete or you're follow_up_question, participants must always be a JSON array e.g. ["Priya"], never a plain string.to must always be a JSON array e.g. ["Rahul"], never a plain string.


    ANSWERING FORMAT:
        - If the user prompt is clear and complete, exm :: "Schedule a 45 minute meeting with Rahul and Priya next Tuesday afternoon:", then your response should be : 
            {
             "tool": "schedule_meeting",
             "confidence": 0.9,
             "args": {
               "participants": ["Rahul", "Priya"],
               "duration_minutes": 45,
               "date": "next Tuesday",
               "time_preference": "afternoon"
             },
             "missing_fields": [],
             "follow_up_question": null,
            }
            
        - If the user prompt is missing some required fields, exm :: "Schedule a meeting with Rahul and Priya next Tuesday afternoon:", then your response should be :
            {
             "tool": "schedule_meeting",
             "confidence": 0.7,
             "args": {
               "participants": ["Rahul", "Priya"],
               "date": "next Tuesday",
               "time_preference": "afternoon"
             },
             "missing_fields": ["duration_minutes"],
             "follow_up_question": "Hey! I need some more information to schedule the meeting, can you please provide the following details: duration_minutes"
            }
            
        - If the user prompt is not clear at all and doesn't support any of the tools, exm :: "I want to search for a restaurant", then your response should be :
            {
             "tool": null,
             "confidence": 0,
             "args": {},
             "missing_fields": [],
             "follow_up_question": "Hey! sorry for the inconviniet! I can help with send_email, draft_email, and schedule_meeting."
            }
    
    RULES:    
        - MUST follow the schema strictly, and respond in JSON format only, no markdown, no backticks, no explanations, just the JSON object, even messing fields and follow up question should be in JSON format.
        - The "confidence" field should reflect how confident you are in your understanding of the user's intent, with 1 being completely confident and 0 being not confident at all.
        
        
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

    def is_missing(value):
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        if isinstance(value, list) and len(value) == 0:
            return True
        return False

    for field in required:
        if field not in args or is_missing(args.get(field)):
            messing.append(field)

    response["missing_fields"] = messing

    ### itrate over the missing fields and add follow up question to response
    if messing:
        if tool == "send_email":
            if set(messing) == {"body"}:
                response["follow_up_question"] = "What would you like the email to say?"
            else:
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
            if set(messing) == {"date_or_time", "duration_minutes"}:
                response["follow_up_question"] = "When should I schedule the meeting and for how long?"
            else:
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
        meeting_time = args.get("date_or_time") or args.get("date") or args.get("time")
        return {
            "status": "success",
            "message": f"Meeting scheduled at {meeting_time} with participants {', '.join(args.get('participants', []))}"
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