import math
import os
import sys
import json
from typing import Final
from pathlib import Path
import modinstall
import os

VERSION: Final[float] = 3.0
RUNTIME_CONFIG_PATH: Final[str] = str(os.path.join(os.path.expanduser("~"), ".modinstallrc"))

def read_config_file(): 
    try:
        # Check if the file exists
        if os.path.exists(RUNTIME_CONFIG_PATH):
            with open(RUNTIME_CONFIG_PATH, "r") as file:
                try:
                    config_data = json.load(file)
                except json.JSONDecodeError:
                    print("Error decoding JSON, resetting to default config.")
                    write_config(RUNTIME_CONFIG_PATH)
        else:
            print(f"Config file not found. Creating {RUNTIME_CONFIG_PATH} with default values.")
            write_config(RUNTIME_CONFIG_PATH)
    except Exception as e:
        print("An error occurred:", str(e))
    return config_data

def write_config(file_path):
    # Default dictionary to populate the JSON file if it doesn't exist
    DEFAULT_CONFIG: Final = {
        "scriptURL": "example.com",
        "custom_install_locations": {}
    }
    # Write the default config to the file
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    print("Please go update your config with the default settings your group uses.")
    input("Press any key to exit...")
    sys.exit(0)

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

def compare_versions(web_version):
    if 'version' in variables:
        if variables['version'] != str(VERSION):
            print("It looks like there is an update available for this script.")
            print("You have version " + str(VERSION) + " but the latest version is " + str(variables['version']))
            print("Go to the following website to get the latest version")
            print("https://github.com/RagingFlames/Paradox-Mod-Updater/releases")
            local_major, local_minor = map(int, str(VERSION).split('.'))
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
    # Open the config file
    config_data = read_config_file()
    scriptVariables = "https://downloads.mclemo.re/scripts/modUpdater/scriptVariables.json"

    # Download the scriptVariables file
    current_dir = os.getcwd()
    scriptVariablesFile = download_file(scriptVariables, current_dir)

    # Execute the scriptVariables.py file and retrieve variables
    if scriptVariablesFile:
        config_data = read_config_file()
        variables = {}
        with open('scriptVariables.json', 'r') as f:
            variables = json.load(f)
    else:
        print("An error has occurred, I could not acquire the variable file.")
        exit(9)

    # Check version number.
    compare_versions(str(variables['version']))

    # Mod selection logic
    if variables:
        modinstall.install(variables, config_data)
    else:
        print("Error: Failed to retrieve variables from the server.")

    print("Finished!")
    input("Press Enter to close the program...")
    sys.exit(0)

