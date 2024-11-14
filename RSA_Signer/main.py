# rsa_signer/main.py
from rsa_signer.rsa_key_manager import RSAKeyManager
from rsa_signer.signer import RSASigner
from rsa_signer.utils import sanitize_input
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def main():
    # Init RSA Key Manager
    key_manager = RSAKeyManager()

    # Load or generate keys
    if not key_manager.load_keys():
        bit_length = None
        while bit_length not in [1024, 2048]:
            try:
                console.print("Enter [yellow]1[/] for [yellow]1024-bit[/] or [yellow]2[/] for [yellow]2048-bit[/]: ")
                choice = int(input())
                if choice == 1:
                    bit_length = 1024
                elif choice == 2:
                    bit_length = 2048
                else:
                    raise ValueError
            except ValueError:
                console.print("[red]Invalid input. Please enter 1 or 2.")

        key_manager.generate_keys(bit_length)
        key_manager.save_keys()
        key_manager.copy_public_key_to_clipboard()
    else:
        console.print("[green]RSA keys loaded successfully.[/]")

    # Create an RSA Signer with the loaded keys
    signer = RSASigner(key_manager.private_key)

    while True:
        # Get user input
        message = sanitize_input("Write message: ", allow_empty=False)
        player_id = sanitize_input("Enter Player Profile ID: ", allow_empty=True)

        if not player_id.strip():
            player_id = "SC2E-TEST-ACCOUNT"

        # Sign the message
        final_base64, overview_table, encoded_message_panel = signer.sign_message(message, player_id)

        # Display the information
        console.print(overview_table)
        console.print(encoded_message_panel)

        while True:
            return_to_message = False
            # Prompt to copy message, show options, or quit
            confirmation = Prompt.ask(
                "[bold green]Press [yellow]Enter[/] to copy the signed message, [yellow]'o'[/] for options, or [yellow]'q'[/] to quit[/]"
            )

            if confirmation.strip().lower() == '':
                # Copy the signed message to clipboard
                signer.copy_signed_message_to_clipboard(final_base64)
                break 
            elif confirmation.strip().lower() == 'o':
                # Show options menu
                while True:
                    console.print("\n[bold cyan]Options:[/]")
                    console.print("[yellow]1.[/] Delete PEM key and generate a new key pair")
                    console.print("[yellow]2.[/] Display public key")
                    console.print("[yellow]3.[/] Go back to signing")

                    option = Prompt.ask("[bold green]Enter your choice (1, 2 or 3)[/]")

                    if option.strip() == '1':
                        # Delete PEM key and generate new key pair
                        bit_length = None
                        while bit_length not in [1024, 2048]:
                            try:
                                console.print("Enter [yellow]1[/] for [yellow]1024-bit[/] or [yellow]2[/] for [yellow]2048-bit[/]")
                                choice = int(input())
                                if choice == 1:
                                    bit_length = 1024
                                elif choice == 2:
                                    bit_length = 2048
                                else:
                                    raise ValueError
                            except ValueError:
                                console.print("[red]Invalid input. Please enter 1 or 2.")

                        key_manager.regenerate_keys(bit_length)
                        # Update the signer with the new private key
                        signer = RSASigner(key_manager.private_key)
                        # Prompt the user to sign a message with the new key
                        continue_with_new_key = Prompt.ask(
                            "[bold green]Do you want to sign a message with the new key?[/] [yellow](y/n)[/]"
                        )
                        if continue_with_new_key.strip().lower() == 'y':
                            return_to_message = True
                            break  # Break the options loop to return to message signing
                        else:
                            console.print("[yellow]Exiting...[/]")
                            return  # Exit the program
                    elif option.strip() == '2':
                        # Display public key
                        base64_public_key = key_manager.get_public_key_base64()
                        if base64_public_key:
                            console.print(f"[bold green]\nPublic Key:[/][yellow]\n{base64_public_key}\n[/]")
                    elif option.strip() == '3':
                            break # Break the options loop to return to message signing
                        
                # After exiting the options loop
                if return_to_message:
                    break  # Break the confirmation loop to return to message signing
                else:
                    # Continue the confirmation loop
                    continue
            elif confirmation.strip().lower() == 'q':
                console.print("[yellow]Exiting...[/]")
                return  # Exit the main function
            else:
                console.print("[red]Invalid input. Please press Enter, 'o', or 'q'.")

        if return_to_message:
            continue
        else:
            # ask if the user wants to sign another message
            continue_prompt = Prompt.ask(
                "[bold green]Do you want to sign another message?[/] [yellow](y/n)[/]"
            )
            if continue_prompt.strip().lower() != 'y':
                console.print("[yellow]Exiting...[/]")
                break  # Exit the main loop

if __name__ == "__main__":
    main()