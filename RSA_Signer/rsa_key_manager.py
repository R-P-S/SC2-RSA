# rsa_signer/rsa_key_manager.py
from appdirs import user_data_dir
import os
import base64
from Crypto.PublicKey import RSA
from rich.console import Console

console = Console()

class RSAKeyManager:
    """
    Manages RSA key generation, saving, and loading.
    """

    def __init__(self, key_file='rsa_keys.pem'):
        config_dir = user_data_dir(appname='SC2Signer', appauthor=False)
        os.makedirs(config_dir, exist_ok=True)
        self.key_file = os.path.join(config_dir, key_file)
        self.private_key = None
        self.n = None
        self.e = None
        self.d = None

    def generate_keys(self, bit_length):
        import time
        start_time = time.time()

        e_value = 65537 if bit_length == 1024 else 17

        # Generate the RSA key pair
        key = RSA.generate(bit_length, e=e_value)
        self.private_key = key
        public_key = key.publickey()

        # Extract modulus and exponents
        self.n = public_key.n
        self.e = public_key.e
        self.d = key.d

        duration = time.time() - start_time
        console.print(f"[blue]Key pair generation took {duration:.2f} seconds.")

    def save_keys(self):
        # Export the private key to PEM format
        private_key_pem = self.private_key.export_key(format="PEM").decode('utf-8')
        with open(self.key_file, 'w') as key_file:
            key_file.write(private_key_pem)
        console.print(f"[green]RSA keys saved to {self.key_file}[/]")

    def load_keys(self):
        if os.path.exists(self.key_file):
            try:
                with open(self.key_file, 'r') as key_file:
                    private_key_pem = key_file.read()
                self.private_key = RSA.import_key(private_key_pem.encode('utf-8'))
                self.n = self.private_key.n
                self.e = self.private_key.e
                self.d = self.private_key.d
                return True
            except Exception as e:
                console.print(f"[red]Error loading keys:[/] {e}")
                return False
        else:
            console.print(f"[yellow]Key file not found: {self.key_file}[/]")
            return False

    def copy_public_key_to_clipboard(self):
        base64_public_key = base64.b64encode(
            self.n.to_bytes((self.n.bit_length() + 7) // 8, byteorder='big')
        ).decode('utf-8')
        try:
            import pyperclip
            pyperclip.copy(base64_public_key)
            console.print("[yellow]Public key copied to clipboard![/]")
        except ImportError:
            console.print("[red]pyperclip module not found. Unable to copy public key to clipboard.[/]")
    
    def get_public_key_base64(self):
        if self.n is None:
            console.print("[red]Public key not available.[/]")
            return None
        base64_public_key = base64.b64encode(self.n.to_bytes((self.n.bit_length() + 7) // 8, byteorder='big')).decode('utf-8')
        return base64_public_key

    def regenerate_keys(self, bit_length):
        # Delete existing key file
        if os.path.exists(self.key_file):
            os.remove(self.key_file)
            console.print(f"[yellow]Deleted existing key file: {self.key_file}[/]")
        else:
            console.print("[yellow]No key file found to delete.[/]")

        # Generate new keys
        self.generate_keys(bit_length)
        self.save_keys()
        self.copy_public_key_to_clipboard()

