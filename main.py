import json

from assistant import execute_tool, process_user_prompt


def main():
    
    print("Welcome to Ai assistant!  Type 'exit' to quit.\n")

    ### Add follow-up conversation loop in main.py
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        response = process_user_prompt(user_input)
        
        if response.get("missing_fields"):
            print(f"\n🤖: {response.get('follow_up_question')}")

            follow_up = input("You: ")
            combined = f"{user_input}. {follow_up}"
            response = process_user_prompt(combined)
        
        if not response.get("missing_fields"):
            result = execute_tool(response)
            print(f"\n✅ {result['message']}")
        
        print("\n" + json.dumps(response, indent=2))


if __name__ == "__main__":
    main()




