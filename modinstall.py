from getpass import getuser
import py7zr
from tqdm import tqdm
import requests
import json
import subprocess
import config
import os
import platform

# Don't print these items as options in the menu navigator
EXCLUDED_MENU_ITEMS = ['prompt', 'meta']
RUNTIME_CONFIG_PATH = str(os.path.join(os.path.expanduser("~"), ".modinstallrc"))

def install(variables, config_data):
    # Print special message
    if variables['message']:
        print(variables['message'])

    meta_data, selected_mod = menu_navigator(variables)
    # Finding install directoryselected_game
    install_directory = get_install_directory(meta_data, config_data)

    # Use the selected key for the upcoming download
    archive_url = selected_mod[0]
    try:
        download_and_extract(archive_url, install_directory, config_data)
    except Exception as e:
        print(f"An error occurred: {e}")

    # Print the hash for this mod pack
    print("The hash for this mod pack is: " + str(selected_mod[1]))


def extract_with_7zip_gui(archive_path, output_dir, config_data):
    seven_zip_path = os.path.abspath(config_data["7z_path"]) if config_data.get("7z_path") else config.find_7z_path()

    archive_path = os.path.abspath(archive_path)
    output_dir = os.path.abspath(output_dir)

    if not os.path.exists(archive_path):
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    if not os.path.exists(seven_zip_path):
        raise FileNotFoundError(f"7-Zip GUI not found at: {seven_zip_path}")

    os.makedirs(output_dir, exist_ok=True)

    command = [
        seven_zip_path,
        'x',
        archive_path,
        f'-o{output_dir}',
        '-y'
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stderr)

def download_and_extract(url, destination, config_data):
    quick_extract = config_data.get("quick_extract", True)
    if isinstance(quick_extract, bool):
        pass  # Value is already a boolean
    else:
        quick_extract = eval(str(quick_extract))
    try:
        # Ensure the destination directory exists
        os.makedirs(destination, exist_ok=True)

        # Download
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            print("Error: Failed to download the archive.")
            return

        archive_path = os.path.join(destination, "mod.7z")
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024

        with open(archive_path, "wb") as f, tqdm(
            total=total_size, unit="B", unit_scale=True, desc="Downloading"
        ) as download_bar:
            for data in response.iter_content(block_size):
                f.write(data)
                download_bar.update(len(data))

        print("Downloaded the archive.")
        print("Beginning extraction, this may take a few minutes.")

        # Extraction
        try:
            extract_with_7zip_gui(archive_path, destination, config_data)
        except (FileNotFoundError, NameError) as e:
            print(f"7-Zip unavailable ({e}), using py7zr...")
            with py7zr.SevenZipFile(archive_path, mode='r') as z:
                file_list = z.getnames()
                info = z.archiveinfo()
                if info.solid or quick_extract: # Check if this is a solid block archive
                    print("Please wait until extraction is complete, do not close this window.")
                    z.extractall(path=destination) # Quick extract
                else: # Extract with progress bar (Slower)
                    with tqdm(total=len(file_list), desc="Extracting", unit="file") as extract_bar:
                        for filename in file_list:
                            z.extract(targets=[filename], path=destination)
                            extract_bar.update(1)
                            z.reset()
        print("Extracted the contents.")

        os.remove(archive_path)
        print("Deleted the archive file.")

    except Exception as e:
        print(f"An error occurred: {e}")

def get_install_directory(meta_data, config_data):
    custom_install = False
    system = platform.system()
    if system == "Windows":
        install_directory = meta_data.get('win_install_location')
    elif system == "Linux":
        install_directory = meta_data.get('lin_install_location')
    elif system == "Darwin":
        install_directory = meta_data.get('mac_install_location')
    else:
        print("Unknown OS:", system)
        sys.exit(1)
    install_directory = install_directory.replace('~', str(os.path.expanduser('~')))

    # Check if an install location has been set in the config file
    game_name = meta_data.get("name")
    if game_name in config_data["custom_install_locations"]:
        install_directory = config_data["custom_install_locations"][game_name]

    while not os.path.isdir(install_directory):
        print(f"The directory '{install_directory}' does not exist.")
        print("This probably means you have a weird windows drive setup (Like having My Documents on a drive other than C)")
        install_directory = input("Please copy and paste the correct mod directory for your game, or push enter to just have the modpack download to the current directory: ")
        custom_install = True
        # Use the current directory if the user presses Enter
        if install_directory.strip() == "":
            print("Using current directory")
            install_directory = os.getcwd()
            break
        
    if custom_install:
        
        # Ask user if they want to write this custom directory to the config file
        response = input("Do you want to save this custom install location to your config? (y/n): ").lower()
        while response not in ['y', 'n']:
            print("Invalid input. Please answer with 'y' or 'n'.")
            response = input("Do you want to save this custom install location to your config? (y/n): ").lower()

        if response == 'y':
            # Update the config file
            game_name = meta_data.get("name")
            config_data["custom_install_locations"][game_name] = str(install_directory)
            with open(RUNTIME_CONFIG_PATH, "w") as f:
                json.dump(config_data, f, indent=4)
            print(f"Saved custom install location for {game_name} to your config file.")

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
            # Set the new variables value
            variables = variables[selected_item]
            # Grab the latest metadata
            if "meta" in variables:
                deep_merge(meta, variables["meta"])
        else:
            navigate = False
    return meta, variables

def deep_merge(original, new):
    for key, value in new.items():
        if key in original and isinstance(original[key], dict) and isinstance(value, dict):
            deep_merge(original[key], value)
        else:
            original[key] = value