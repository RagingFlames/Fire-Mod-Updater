import math
import os
import sys
import modinstall

version = 3.0

# Check if required imports are available
try:
    from pathlib import Path
except ImportError:
    print("Error: The 'pathlib' module is missing. Please install it by running 'pip install pathlib'.")
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
        variables = {}
        with open(scriptVariablesFile, "r") as f:
            exec(f.read(), variables)
    else:
        print("An error has occurred, I could not acquire the variable file.")
        exit(9)

    # Check version number.
    compare_versions(str(variables['version']))

    # Mod selection logic
    if variables:
        modinstall.all(variables)
    else:
        print("Error: Failed to retrieve variables from the server.")

    print("Finished!")
    input("Press Enter to close the program...")
    sys.exit(1)

