import json

from backend.assistant import execute_tool, process_user_prompt


def main():
    print("Welcome to AI assistant! Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        combined = user_input
        response = process_user_prompt(combined)

        while response.get("missing_fields"):
            print("\n" + json.dumps(response, indent=2))
            follow_up = input("You: ")
            combined = f"{combined}. {follow_up}"
            response = process_user_prompt(combined)

        execute_tool(response)
        print("\n" + json.dumps(response, indent=2))


if __name__ == "__main__":
    main()
