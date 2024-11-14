# rsa_signer/utils.py
import os
from rich.console import Console

console = Console()

def sanitize_input(prompt, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if '|' in value:
            console.print("[red]Error:[/] Input cannot contain the '|' character. Please try again.")
        elif not allow_empty and not value:
            console.print("[red]Error:[/] Input cannot be empty. Please try again.")
        else:
            return value

def get_file_path(relative_path, description):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, relative_path)
    file_path = os.path.normpath(file_path)

    if not os.path.exists(file_path):
        console.print(f"[yellow]Error: {description} not found - {file_path}")
        return None
    return file_path
