import subprocess
import sys
import re

DANGEROUS_KEYWORDS = [
    "Remove-Item",       # Deletes files/directories
    "Format-Drive",      # Formats a disk
    "shutdown",          # Shuts down the computer
    "Set-ExecutionPolicy", # Changes script execution policies
    "Invoke-WebRequest", # Can be used to download malicious files
    "Start-Process"      # Can be used to run executables or open URLs
]

URL_PATTERN = re.compile(r'https?://\S+')

def is_safe_command(command: str) -> bool:
    """
    Checks if a command is safe to execute by looking for dangerous keywords.

    Args:
        command: The PowerShell command to check.

    Returns:
        True if the command is considered safe, False otherwise.
    """
    # Check for exact keywords (case-insensitive)
    for keyword in DANGEROUS_KEYWORDS:
        if keyword.lower() in command.lower():
            # Special handling for Start-Process and Invoke-WebRequest to allow local file operations
            if keyword.lower() == "start-process" or keyword.lower() == "invoke-webrequest":
                if URL_PATTERN.search(command):
                    print(f"Warning: Dangerous keyword '{keyword}' found with a URL.")
                    return False
            else:
                print(f"Warning: Dangerous keyword '{keyword}' found.")
                return False
    return True

def run_powershell_command(command: str) -> str:
    """
    Runs a PowerShell command and returns its output.

    Args:
        command: The PowerShell command to execute.

    Returns:
        The standard output of the command, or an error message if it fails.
    """
    # Ensure the command is not empty
    if not command.strip():
        return "Error: Command cannot be empty."

    try:
        # For Windows, we can directly use 'powershell.exe'
        if sys.platform == "win32":
            process = subprocess.run(
                ["powershell.exe", "-Command", command],
                capture_output=True,
                text=True,
                check=True,  # Raise an exception for non-zero exit codes
                encoding='utf-8'
            )
            return process.stdout
        else:
            # For non-Windows systems, you might need to use 'pwsh'
            # This requires PowerShell Core to be installed.
            process = subprocess.run(
                ["pwsh", "-Command", command],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )
            return process.stdout

    except FileNotFoundError:
        return "Error: PowerShell is not installed or not in the system's PATH."
    except subprocess.CalledProcessError as e:
        # This catches errors from the command itself (non-zero exit code)
        return f"Error executing command:\n{e.stderr}"
    except Exception as e:
        # Catch any other unexpected errors
        return f"An unexpected error occurred: {e}"

if __name__ == '__main__':
    # Example usage for testing
    # Note: This command is safe and just gets the current date.
    test_command = "Get-Date"
    output = run_powershell_command(test_command)
    print("--- PowerShell Output ---")
    print(output)
    print("-------------------------")

    # Example of a command that might produce an error
    error_command = "Get-NonExistentCmdlet"
    error_output = run_powershell_command(error_command)
    print("\n--- PowerShell Error Output ---")
    print(error_output)
    print("-----------------------------")

    # Example of a dangerous command
    dangerous_command = "Remove-Item C:\\Windows"
    dangerous_output = run_powershell_command(dangerous_command)
    print("\n--- Dangerous Command Output ---")
    print(dangerous_output)
    print("------------------------------")
