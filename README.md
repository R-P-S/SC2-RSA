# SC2 RSA Signature Verification

This project provides a custom implementation of RSA signature verification in SC2, enabling secure message validation through RSA signatures. RSA signatures work by encrypting a hash of the message with a private key, allowing the recipient to verify its authenticity by decrypting it with the corresponding public key.

The project includes:

- **BigNum Library**: An arbitrary-precision arithmetic library to handle large integers beyond Galaxy Script’s 32-bit limit.

- **SHA1 Library**: A hashing library to provide the necessary functionality for message hashing in RSA signature verification.

- **RSA Signature Verification**: Verifies RSA-signed messages by decrypting the signature and comparing it to a hashed and padded message.

- **Python Signing Tool**: Generates RSA key pairs, signs messages, and outputs a Base64-encoded string for use in SC2.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Example](#example)
- [License](#license)

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/R-P-S/SC2-RSA.git
    cd SC2-RSA
    ```
2. **Requirements:**

   - Python 3
    
        If Python is not installed, [download and install it here.](https://www.python.org/downloads/)

3. **Install Required Python Package**
    ```bash
     pip install https://github.com/R-P-S/SC2-RSA/archive/master.zip
    ```

    This command installs all necessary Python dependencies for the signing tool.

## Usage

1. **Initial Run of the Python Signing Tool**
      ```bash
      $ sc2signer
      ```
      The tool will guide you through the setup. On the first run, you’ll be asked to select an RSA key size:
  
    - **Select 1024 or 2048 bits**. A 1024-bit key is recommended for optimal performance. If you're using a 2048-bit key, set the constant `KEY_SIZE_MULTIPLIER` to `2` in `bignum.galaxy` or in the trigger library if using the GUI.

        Once keys are generated, the script saves them to a `.pem` file and copies the public key to your clipboard. Paste this key into the `PUBLIC_KEY` constant in `rsa.galaxy` or, if using the GUI, into the `PUBLIC_KEY` constant in the trigger module.
  
  2. **Signing Messages with the Python Script**

      - Enter a message and player ID when prompted.
      - The script outputs a signed message in Base64 format.

3. **Verifying Signatures in SC2**

      Once a signed message is generated, it can be verified in-game. The included example trigger `gt_DecryptSignature` listens for the chat command (e.g., -m {signed_message}) and verifies the signature by:

    - Decrypting the RSA signature.
    - Comparing it with the expected hash of the padded message and player profile ID.

4. **Key File Location**

    The RSA key pair is stored in a user-specific directory. Make sure to keep this file secure, as it contains the private key used for signing.

    - **Windows:** `C:\Users\<Username>\AppData\Local\SC2Signer\rsa_keys.pem`
    - **macOS:** `/Users/<Username>/Library/Application Support/SC2Signer/rsa_keys.pem`
    - **Linux:** `/home/<Username>/.local/share/SC2Signer/rsa_keys.pem`

## Example
**Python Signing Tool**

Example run:
```bash
$ sc2signer
Write message: Marine 5
Enter Player Profile ID: SC2E-TEST-ACCOUNT
```

![console](https://i.imgur.com/3naWNjW.png)   

**Verification**

In Starcraft 2's chat console:
```bash
-m {signed_message}
```

![screenshot](https://imgur.com/ydlltMV.jpeg)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.