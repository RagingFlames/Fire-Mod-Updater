import math
import os
import sys

version = 2.3

# Check if required imports are available
try:
    from pathlib import Path
except ImportError:
    print("Error: The 'pathlib' module is missing. Please install it by running 'pip install pathlib'.")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Error: The 'requests' module is missing. Please install it by running 'pip install requests'.")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    print("Error: The 'tqdm' module is missing. Please install it by running 'pip install tqdm'.")
    sys.exit(1)

try:
    import py7zr
except ImportError:
    print("Error: The 'py7zr' module is missing. Please install it by running 'pip install py7zr'.")
    sys.exit(1)

try:
    from getpass import getuser
except ImportError:
    print("Error: The 'getpass' module is missing which probably means something is very wrong.")
    sys.exit(1)


import os

def download_file(url: str, destination: str) -> bool:
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print("Error: Failed to download the file.")
            return False
        file_path = os.path.join(destination, "scriptVariables.py")
        with open(file_path, "wb") as f:
            f.write(response.content)
        print("Downloaded server updates.")
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


from pathlib import Path


def download_and_extract(url, destination):
    try:
        download_extract_response = requests.get(url, stream=True)
        if download_extract_response.status_code != 200:
            print("Error: Failed to download the archive.")
            return
        archive_path = os.path.join(destination, "mod.7z")
        total_size = int(download_extract_response.headers.get("content-length", 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size, unit="B", unit_scale=True, desc="Downloading")
        with open(archive_path, "wb") as f:
            for data in download_extract_response.iter_content(block_size):
                progress_bar.update(len(data))
                f.write(data)
        progress_bar.close()
        print("Downloaded the archive.")
        print("Beginning extraction, this may take a few minutes.")
        with py7zr.SevenZipFile(archive_path, mode='r') as z:
            z.extractall(path=destination)
        print("Extracted the contents.")

        os.remove(archive_path)  # Delete the archive file
        print("Deleted the archive file.")
    except Exception as e:
        print(f"An error occurred: {e}")


def compare_versions(web_version):
    if 'version' in variables:
        if variables['version'] != str(version):
            print("It looks like there is an update available for this script.")
            print("You have version " + str(version) + " but the latest version is " + str(variables['version']))
            print("Go to the following website to get the latest version")
            print("https://github.com/RagingFlames/Paradox-Mod-Updater/releases")
            local_major, local_minor = map(int, str(version).split('.'))
            web_major, web_minor = map(int, web_version.split('.'))

            if web_major - local_major >= 1:
                print("You are behind by at least 1 major revision, it is highly recommended that exit and download the newer version")
                while True:
                    response = input("Do you want to continue? (y/n): ").lower()
                    if response == 'y':
                        print("Continuing...")
                        # Perform additional tasks or actions here
                        break
                    elif response == 'n':
                        print("Exiting...")
                        sys.exit(1)
                    else:
                        print("Invalid input. Please answer with 'y' or 'n'.")

if __name__ == "__main__":
    scriptVariables = "https://downloads.mclemo.re/Public/ModUpdater/scriptVariables.py"
    archive_url = None

    # Download the scriptVariables file
    current_dir = os.getcwd()
    scriptVariablesFile = download_file(scriptVariables, current_dir)

    # Execute the scriptVariables.py file and retrieve variables
    if scriptVariablesFile:
        url_module = {}
        with open(scriptVariablesFile, "r") as f:
            exec(f.read(), url_module)
        variables = url_module.copy()
    else:
        print("An error has occurred, I could not acquire the variable file.")
        exit(9)

    # Check version number.
    compare_versions(str(variables['version']))

    # Mod selection logic
    if variables:

        # Print special message
        if variables['message']:
            print(variables['message'])

        # Select a game
        print("What game would you like to install a mod for?")
        for i, key in enumerate(variables['packs'].keys()):
            print(f"{i}: {key}")

        selection = input("Enter the number on the left corresponding to the game you want to install a modpack for: ")
        selected_game = list(variables['packs'].keys())[int(selection)]

        print("Mod packs available for:", selected_game)

        # Select a Mod
        for i, key in enumerate(variables['packs'].get(selected_game).keys()):
            print(f"{i}: {key}")
        selection = input("Enter the number on the left corresponding to the mod pack you want to install, 0 is the latest one: ")
        selected_mod = list(variables['packs'].get(selected_game).keys())[int(selection)]

        # Finding directory
        username = getuser()
        documents_path = Path.home() / "Documents"
        destination = documents_path / "Paradox Interactive" / selected_game / "mod"
        if os.path.exists(destination):
            print("Using C drive for installation")
        else:
            destination = os.path.join("D:\\", "Users", username, "Documents", "Paradox Interactive", selected_game, "mod")
            if os.path.exists(destination):
                print("Using D drive for installation")
            else:
                print("I couldn't find your game folder on your C or D drive")
                print("The mod pack will be downloaded to the current directory")
                destination = os.getcwd()

        # Use the selected key for the upcoming download
        archive_url = variables['packs'].get(selected_game).get(selected_mod)[0]
        try:
            download_and_extract(archive_url, destination)
        except Exception as e:
            print(f"An error occurred: {e}")

        # Print the hash for this mod pack
        print("The hash for this mod pack is: " + str(variables['packs'].get(selected_game).get(selected_mod)[1]))

    else:
        print("Error: Failed to retrieve variables from the server.")

    print("Finished!")
    input("Press Enter to close the program...")
    sys.exit(1)

