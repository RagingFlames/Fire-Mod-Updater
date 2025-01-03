from getpass import getuser
import os
from pathlib import Path
import py7zr
import tqdm
import requests
from typing import Final

# Don't print these items as options in the menu navigator
EXCLUDED_MENU_ITEMS: Final[list] = ['prompt', 'meta']

def install(variables):
    # Print special message
    if variables['message']:
        print(variables['message'])

    meta, selected_mod = menu_navigator(variables)

    # Finding install directoryselected_game
    install_directory = get_install_directory(meta)

    # Use the selected key for the upcoming download
    archive_url = selected_mod[0]
    try:
        download_and_extract(archive_url, install_directory)
    except Exception as e:
        print(f"An error occurred: {e}")

    # Print the hash for this mod pack
    print("The hash for this mod pack is: " + str(selected_mod[1]))

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

def get_install_directory(game_variables):
    install_directory = game_variables.get('install_location')
    install_directory = install_directory.replace('~', str(os.path.expanduser('~')))

    while not os.path.isdir(install_directory):
        print(f"The directory '{install_directory}' does not exist.")
        print("This probably means you have a weird windows drive setup (Like having My Documents on a drive other than C)")
        directory = input("Please copy and paste the correct mod directory for your game, or push enter to just have the modpack download to the current directory: ")
        # Use the current directory if the user presses Enter
        if directory.strip() == "":
            directory = os.getcwd()
            break
        
    return install_directory

def menu_navigator(variables):
    navigate = True
    variables = variables['packs']
    meta = {}
    while navigate:
        if not isinstance(variables, list):
            if "prompt" in variables:
                print(variables["prompt"])
            else:
                print("make selection")
            for i, key in enumerate(variables.keys()):
                if key not in EXCLUDED_MENU_ITEMS:  # Make sure the key isn't an excluded item
                    print(f"{i}: {key}")
            selection = input("Enter the number on the left corresponding to the item you want: ")
            selected_item = list(variables.keys())[int(selection)]
            # Grab the latest metadata
            if "meta" in variables:
                meta = variables["meta"]
            # Set the new variables value
            variables = variables[selected_item]
        else:
            navigate = False
    return meta, variables
