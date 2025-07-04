import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path='dotenv.env')

# Configure the Gemini API key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in your dotenv.env file.")
    print("Please ensure your dotenv.env file contains the following line:")
    print("GEMINI_API_KEY='your_api_key_here'")
    sys.exit(1)

genai.configure(api_key=api_key)

def get_powershell_command(prompt: str) -> dict:
    """
    Uses the Gemini API to convert a natural language prompt into a PowerShell command.

    Args:
        prompt: The natural language input from the user.

    Returns:
        A dictionary containing the PowerShell command and an explanation.
        Example: {'command': 'Get-Process', 'explanation': 'Lists all running processes.'}
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-pro')
    except Exception as e:
        print(f"Error creating Gemini model: {e}")
        return {}
    
    # We can improve this prompt with more context and examples
    full_prompt = f"""
    You are an expert in PowerShell. Your task is to translate the following 
    natural language request into a single, executable PowerShell command.

    Request: "{prompt}"

    Provide the command and a brief, one-line explanation of what it does.
    Return the output in a JSON format with two keys: 'command' and 'explanation'.
    
    Example:
    Request: "list all running processes"
    {{
        "command": "Get-Process",
        "explanation": "This command lists all the currently running processes on the system."
    }}
    """
    
    response = model.generate_content(full_prompt)
    
    try:
        # The response text might be in a markdown block, so we need to clean it
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        import json
        return json.loads(cleaned_response)
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error decoding Gemini response: {e}")
        return {}

if __name__ == '__main__':
    # Example usage for testing
    test_prompt = "Find all files in the current directory larger than 10MB"
    command_data = get_powershell_command(test_prompt)
    if command_data:
        print(f"Command: {command_data.get('command')}")
        print(f"Explanation: {command_data.get('explanation')}")
