import os
import configparser
from Util import get_file_path, read_keys_from_ini
from sympy import nextprime
from Crypto.Util.number import getRandomNBitInteger, inverse
import base64
import hashlib

# Utility function to sanitize input strings
def sanitize_input(prompt):
    while True:
        value = input(prompt)
        if '|' in value:
            print("Error: Input cannot contain the '|' character. Please try again.")
        else:
            return value

# Function to generate RSA keys
def generate_rsa_keys(bit_length):
    p = nextprime(getRandomNBitInteger(bit_length // 2))
    q = nextprime(getRandomNBitInteger(bit_length // 2))
    n = p * q
    phi_n = (p - 1) * (q - 1)
    e = 65537
    d = inverse(e, phi_n)
    return n, e, d

# Function to save RSA keys to keys.ini
def save_keys_to_ini(n, e, d, ini_path):
    config = configparser.ConfigParser()
    config['Keys'] = {
        'n': str(n),
        'e': str(e),
        'd': str(d)
    }
    with open(ini_path, 'w') as configfile:
        config.write(configfile)

# Function to sign the message hash using the private key
def sign_message_hash(message_hash_int, d, n):
    signature = pow(message_hash_int, d, n)
    return signature

# Function to verify the signature using the public key
def verify_signature(signature, message_hash_int, e, n):
    decrypted_hash_int = pow(signature, e, n)
    return decrypted_hash_int == message_hash_int

# Main function to orchestrate RSA logic
def main():
    ini_path = get_file_path('keys.ini', 'RSA key file')

    # If ini_path is None, set it to the expected path for saving
    if ini_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ini_path = os.path.join(script_dir, 'keys.ini')

    keys_exist = False

    # Check if keys.ini exists and load keys
    if os.path.exists(ini_path):
        try:
            n, e, d = read_keys_from_ini(ini_path)
            keys_exist = True
        except (configparser.Error, KeyError):
            print("Error: keys.ini is missing or incorrect.")

    # If keys do not exist, prompt the user to generate them
    if not keys_exist:
        bit_length = None
        while bit_length not in [1024, 2048]:
            try:
                bit_length = int(input("Enter bit length for key generation (1024 or 2048): "))
            except ValueError:
                pass

        n, e, d = generate_rsa_keys(bit_length)
        save_keys_to_ini(n, e, d, ini_path)
        print(f"RSA keys generated and saved to {ini_path}")
        print("Public Key (n):", n)  # Print Public Key only when keys are generated

    # Prompt the user for a message and player handle
    message = sanitize_input("Write message: ")
    player_id = sanitize_input("Enter Player handle: ")

    # Combine message and Player ID
    combined_message = f"{message}|{player_id}"

    # Hash the combined message
    sha1 = hashlib.sha1()
    sha1.update(combined_message.encode())
    message_hash = sha1.digest()
    message_hash_int = int.from_bytes(message_hash, byteorder='big')

    # Sign the hash using the private key
    signature = sign_message_hash(message_hash_int, d, n)

    # Combine Player ID and Signature
    combined_string = f"{message}|{player_id}|{signature}"
    combined_bytes = combined_string.encode('utf-8')
    final_base64 = base64.b64encode(combined_bytes).decode('utf-8')

    # Print the encoded message
    print("Signed Message:", final_base64)

if __name__ == "__main__":
    main()

