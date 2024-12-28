from getpass import getuser
import os
from pathlib import Path
import py7zr
import tqdm

def all(variables):
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
        if key != 'meta':  # We don't want to print the meta information
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