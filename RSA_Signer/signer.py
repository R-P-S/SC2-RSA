# rsa_signer/signer.py
import base64
import hashlib
import os
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

console = Console()

class RSASigner:
    """
    Handles RSA signing and verification.
    """

    def __init__(self, private_key):
        self.private_key = private_key
        self.n = private_key.n
        self.e = private_key.e
        self.d = private_key.d

    def generate_salt(self, length=8):
        return os.urandom(length)

    def add_padding(self, message_hash, salt, padded_len):
        padding_len = padded_len - len(message_hash) - len(salt) - 2
        padding = b'\x00\x01' + (b'\xFF' * padding_len) + b'\x00'
        padded_message = padding + salt + message_hash
        return padded_message

    def sign_message_hash(self, message_hash_int):
        return pow(message_hash_int, self.d, self.n)

    def verify_signature(self, signature, padded_msg_int):
        decrypted_hash_int = pow(signature, self.e, self.n)
        return decrypted_hash_int == padded_msg_int

    def sign_message(self, message, player_id):
        key_size = self.n.bit_length()
        combined_message = f"{message}|{player_id}"
        sha1 = hashlib.sha1()
        sha1.update(combined_message.encode())
        message_hash = sha1.digest()

        # Generate salt & padding for PSS
        salt = self.generate_salt()
        padded_len = 128 if key_size <= 1024 else 256
        padded_message = self.add_padding(message_hash, salt, padded_len)
        padded_message_int = int.from_bytes(padded_message, byteorder='big')

        signature = self.sign_message_hash(padded_message_int)
        is_valid = self.verify_signature(signature, padded_message_int)

        # Convert signature to base64
        signature_base64 = base64.b64encode(
            signature.to_bytes((signature.bit_length() + 7) // 8, byteorder='big')
        ).decode('utf-8')

        # For debugging signature
        padded_message_bytes = padded_message
        padding_end = padded_message_bytes.find(b'\x00', 2) + 1
        decrypted_hash = padded_message_bytes[padding_end:]
        decrypted_hash_int = int.from_bytes(decrypted_hash, byteorder='big')

        # Prepare the overview table
        overview_table = Table(title="Overview", title_style="bold magenta", show_lines=True)
        overview_table.add_column("Field", style="cyan", vertical="middle", no_wrap=True)
        overview_table.add_column("Value", style="white", no_wrap=False, overflow="fold")

        base64_public_key = base64.b64encode(
            self.n.to_bytes((self.n.bit_length() + 7) // 8, byteorder='big')
        ).decode('utf-8')

        overview_table.add_row("Key Size", f"{key_size} bit")
        overview_table.add_row("Public Key", base64_public_key)
        overview_table.add_row("Message", message)
        overview_table.add_row("Player Profile ID", player_id)
        overview_table.add_row("Message Digest (SHA-1)", message_hash.hex().upper())
        overview_table.add_row("Salt", salt.hex())
        overview_table.add_row("RSA Signature", signature_base64)
        if player_id.strip().upper() == "SC2E-TEST-ACCOUNT":
            overview_table.add_row("Decrypted Signature", str(decrypted_hash_int))         
        overview_table.add_row("Signature Valid", f"{is_valid}")

        msg_salt = f"{message}|{salt.hex()}"
        msg_base64 = base64.b64encode(msg_salt.encode('utf-8')).decode('utf-8')
        final_base64 = f"{msg_base64}|{signature_base64}"

        # Create panel & left align
        encoded_message_panel = Panel(
            Text(final_base64, justify="left"),
            title="Signed Message",
            title_align="left",
            border_style="green",
            expand=False
        )

        return final_base64, overview_table, encoded_message_panel

    def copy_signed_message_to_clipboard(self, signed_message):
        try:
            import pyperclip
            pyperclip.copy(signed_message)
            console.print("[yellow]Signed message copied to clipboard![/]")
        except ImportError:
            console.print("[red]pyperclip module not found. Unable to copy signed message to clipboard.[/]")
