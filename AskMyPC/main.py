import os
import sys
import argparse
from datetime import datetime
import gemini
import powershell

DANGEROUS_KEYWORDS = [
    "shutdown", 
    "restart", 
    "format", 
    "del", 
    "remove-item", 
    "rd /s", 
    "diskpart"
]

def is_dangerous(command):
    """Checks if a command contains any dangerous keywords."""
    return any(keyword in command.lower() for keyword in DANGEROUS_KEYWORDS)

def log_command(command):
    """Logs the executed command with a timestamp."""
    with open("command_log.txt", "a") as log_file:
        log_file.write(f"{datetime.now()}: {command}\n")

def main():
    """
    Main function to run the AskMyPC CLI application.
    """
    parser = argparse.ArgumentParser(
        description="Translate natural language to PowerShell commands and execute them."
    )
    parser.add_argument(
        "prompt", 
        nargs="?", 
        default=None, 
        help="The natural language prompt. If not provided, runs in interactive mode."
    )
    parser.add_argument(
        "--safe", 
        action="store_true", 
        help="Enable Safe Mode to block potentially dangerous commands."
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Simulate command execution without actually running anything."
    )
    args = parser.parse_args()

    if args.prompt:
        prompt = args.prompt
    else:
        print("Welcome to AskMyPC! Running in interactive mode.")
        print("Type your request, or 'exit'/'quit' to leave.")
        prompt = input("\n> ")
        if prompt.lower() in ['exit', 'quit']:
            sys.exit(0)

    # Get the PowerShell command from Gemini
    command_data = gemini.get_powershell_command(prompt)
    if not command_data or 'command' not in command_data:
        print("❌ Sorry, I couldn't generate a command for that.")
        return

    command = command_data['command']
    
    # Show the suggested command and ask for confirmation
    print(f"\n⚠️  The AI suggests running this command:\n{command}\n")
    
    # In non-interactive mode, we might want to auto-confirm or have another flag
    # For now, we always ask.
    confirm = input("Do you want to run this? (y/n): ").lower()
    if confirm != "y":
        print("❌ Command cancelled.")
        return

    # Log the confirmed command
    log_command(command)

    # Safety check for --safe mode
    if args.safe and is_dangerous(command):
        print("❌ This command is considered dangerous and was blocked in Safe Mode.")
        return

    # Dry run check
    if args.dry_run:
        print("🧪 Dry run mode: Command not actually executed.")
        return
        
    # Execute the command
    print("\n🚀 Executing command...")
    result = powershell.run_powershell_command(command)
    print("\n🖥️ Output:")
    print(result.strip())

if __name__ == "__main__":
    main()
