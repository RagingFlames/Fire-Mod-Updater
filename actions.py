import requests
import os.path
import tqdm
import shutil
import random
import string

# Print message to the screen
def print(message):
        print(message[0])

# Ask the user for information and store it in the specified variable
def ask(message):
    response = input(message[0])

# Download file to downloads folder
def download(arguments):
        url = arguments[0]
        file_name = arguments[1]
        try:
            download_response = requests.get(url, stream=True)
            if download_response.status_code != 200:
                print("Error: Failed to download the archive.")
                return
            archive_path = os.path.join(".", file_name)
            total_size = int(download_response.headers.get("content-length", 0))
            block_size = 1024
            progress_bar = tqdm(total=total_size, unit="B", unit_scale=True, desc="Downloading")
            with open(archive_path, "wb") as f:
                for data in download_response.iter_content(block_size):
                    progress_bar.update(len(data))
                    f.write(data)
            progress_bar.close()
        except Exception as e:
            print(f"An error occurred while downloading: {e}")
            return False

# move a file or folder somewhere
def move(arguments):
    # Flags (case-sensitive, any order):
    #     f - force overwrite
    #     n - no clobber
    #     p - create parent directories
    #     b - backup existing destination
    #     d - dry run
    file = arguments[0]
    destination = arguments[1]
    flags = set(arguments[2])

    # Conflict checks
    if 'f' in flags and 'n' in flags:
        raise ValueError("Conflicting flags: 'f' (force) and 'n' (no-clobber)")

    if 'b' in flags and 'n' in flags:
        raise ValueError("Conflicting flags: 'b' (backup) and 'n' (no-clobber)")

    # Check source
    if not os.path.exists(file):
        raise FileNotFoundError(f"Source file does not exist: {file}")

    # If destination is a directory, preserve filename
    if os.path.isdir(destination):
        destination = os.path.join(destination, os.path.basename(file))

    dest_dir = os.path.dirname(destination) or "."

    # Create parent directories
    if 'p' in flags and not os.path.exists(dest_dir):
        if 'd' not in flags:
            os.makedirs(dest_dir, exist_ok=True)

    # Setup destination
    if os.path.exists(destination):
        if 'b' in flags:
            backup = destination + ".bak"
            if 'd' not in flags:
                shutil.move(destination, backup)

        elif 'n' in flags:
            raise FileExistsError(f"Destination exists (no-clobber): {destination}")

        elif 'f' not in flags:
            raise FileExistsError(
                f"Destination exists (use 'f' to overwrite): {destination}"
            )

    if 'd' not in flags:
        shutil.move(file, destination)
