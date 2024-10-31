import os
import configparser
import base64
import hashlib
import pyperclip
from sympy import nextprime
from Crypto.Util.number import getRandomNBitInteger, inverse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from Util import get_file_path, read_keys_from_ini

console = Console()

# Utility function to sanitize input strings
def sanitize_input(prompt):
    while True:
        value = input(prompt)
        if '|' in value:
            console.print("[red]Error:[/] Input cannot contain the '|' character. Please try again.")
        else:
            return value

# Function to generate RSA keys
def generate_rsa_keys(bit_length):
    p = nextprime(getRandomNBitInteger(bit_length // 2))
    q = nextprime(getRandomNBitInteger(bit_length // 2))
    n = p * q
    phi_n = (p - 1) * (q - 1)

    # Set the public exponent 'e' based on the bit length
    e = 65537 if bit_length == 1024 else 17
    d = inverse(e, phi_n)
    
    return n, e, d

# Function to save RSA keys to keys.ini
def save_keys_to_ini(n, e, d, ini_path):
    config = configparser.ConfigParser()
    config['Keys'] = {'n': str(n), 'e': str(e), 'd': str(d)}
    with open(ini_path, 'w') as configfile:
        config.write(configfile)

# Function to sign the message hash using the private key
def sign_message_hash(message_hash_int, d, n):
    return pow(message_hash_int, d, n)

# Function to verify signature
def verify_signature(signature, e, n, padded_msg):
    decrypted_hash_int = pow(signature, e, n)  # Decrypt with public key
    return decrypted_hash_int == padded_msg

# Function to generate a random salt for PSS
def generate_salt(length=8):
    return os.urandom(length)

# Function to create PSS padding for a message hash
def add_pss_padding(message_hash, salt, padded_len):
    padding_len = padded_len - len(message_hash) - len(salt) - 2
    padding = b'\x00' * padding_len + b'\x01'
    return padding + salt + message_hash

# Main function for RSA logic
def main():
    ini_path = get_file_path('keys.ini', 'RSA key file')

    if ini_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ini_path = os.path.join(script_dir, 'keys.ini')

    keys_exist = False

    if os.path.exists(ini_path):
        try:
            n, e, d = read_keys_from_ini(ini_path)
            keys_exist = True
        except (configparser.Error, KeyError):
            console.print("[red]Error:[/] keys.ini is missing or incorrect.")

    if not keys_exist:
        bit_length = None
        while bit_length not in [1024, 2048]:
            try:
                bit_length = int(input("Enter bit length for key generation (1024 or 2048): "))
            except ValueError:
                pass

        n, e, d = generate_rsa_keys(bit_length)
        save_keys_to_ini(n, e, d, ini_path)

        # Store the public key (n) to clipboard
        pyperclip.copy(str(n))
        console.print(f"[green]RSA keys generated and saved to {ini_path}[/]")
        console.print("[yellow]Public key (n) copied to clipboard![/]")

    message = sanitize_input("Write message: ")
    player_id = sanitize_input("Enter Player handle: ")

    # Default setting if player_id is empty
    if not player_id.strip():
        player_id = "SC2E-TEST-ACCOUNT"

    key_size = n.bit_length()

    combined_message = f"{message}|{player_id}"
    sha1 = hashlib.sha1()
    sha1.update(combined_message.encode())
    message_hash = sha1.digest()

    # Generate salt & padding for PSS
    salt = generate_salt()
    padded_len = 128 if len(bin(n)) <= 1024 else 256  # Key size bytes - SHA-1 bytes(20) - Salt bytes(20) - 2
    padded_message = add_pss_padding(message_hash, salt, padded_len=padded_len)
    padded_message_int = int.from_bytes(padded_message, byteorder='big')
    signature = sign_message_hash(padded_message_int, d, n)
    is_valid = verify_signature(signature,e,n,padded_message_int)
    
    # Format and display the info using `rich`
    table = Table(title="Overview", 
                  title_style="bold magenta",
                  show_lines=True)

    table.add_column("Field", style="cyan", vertical="middle", no_wrap=True)
    table.add_column("Value", style="white", no_wrap=False, overflow="fold")

    table.add_row("Key Size", f"{key_size} bit")
    table.add_row("Public Key (n)", str(n))
    table.add_row("Message", f"{message}")
    table.add_row("Player ID", f"{player_id}")
    table.add_row("Message Hash (SHA-1)", message_hash.hex().upper())
    table.add_row("Salt", salt.hex())
    table.add_row("PSS Padded Message", f"{padded_message_int}")
    table.add_row("Signature", str(signature))
    table.add_row("Signature Valid", f"{is_valid}")

    combined_string = f"{message}|{salt.hex()}|{signature}"
    final_base64 = base64.b64encode(combined_string.encode('utf-8')).decode('utf-8')

    # Create panel & left align
    encoded_message_panel = Panel(
        Text(final_base64, justify="left"),
        title="Encoded Message",
        title_align="left",
        border_style="green"
    )

    # Display the table and panel
    console.print(table)
    console.print(encoded_message_panel)

    # Prompt to copy msg or quit
    confirmation = Prompt.ask(
        "[bold green]Press Enter to copy the encoded message, or 'q' to quit:[/]"
    )

    if confirmation.lower() == 'q':
        console.print("[yellow]Exiting[/]")
    else:
        pyperclip.copy(final_base64)
        console.print("[yellow]Encoded message copied to clipboard![/]")

if __name__ == "__main__":
    main()