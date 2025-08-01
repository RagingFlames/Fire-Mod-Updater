
import os
import sys
import json
import modinstall
import config
import requests
import os

VERSION = 3.2


def download_file(config_data: dict) -> bool:
    destination = current_dir = os.getcwd()
    url = config_data.get("scriptURL")
    # Check if the user added their script URL
    if url == "example.com":
        return config.get_user_url(config_data)
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print("Error: Failed to download the file.")
            return False
        file_path = os.path.join(destination, "scriptVariables.json")
        with open(file_path, "wb") as f:
            f.write(response.content)
        print("Downloaded server updates.")
        return True
    except Exception as e:
        print(f"An error occurred while downloading updates: {e}")
        return config.get_user_url(config_data)

def compare_versions(web_version, github_link):
    print("Using version " +  str(VERSION))
    if web_version != str(VERSION):
        print("It looks like there is an update available for this script.")
        print("You have version " + str(VERSION) + " but the latest version is " + str(variables['version']))
        print("Go to the following website to get the latest version")
        print(github_link)
        local_major, local_minor = map(int, str(VERSION).split('.'))
        web_major, web_minor = map(int, web_version.split('.'))

        if web_major - local_major >= 1:
            print("You are behind by at least 1 major revision, it is highly recommended that exit and download the newer version")
            while True:
                response = input("Do you want to continue? (y/n): ").lower()
                if response == 'y':
                    break
                elif response == 'n':
                    print("Exiting...")
                    sys.exit(1)
                else:
                    print("Invalid input. Please answer with 'y' or 'n'.")

if __name__ == "__main__":
    # Open the config file
    config_data = config.read_config_file()

    # Download the scriptVariables file
    scriptVariablesFile = download_file(config_data)

    # Read scriptVariables.json file and retrieve variables
    if scriptVariablesFile:
        config_data = config.read_config_file()
        variables = {}
        with open('scriptVariables.json', 'r') as f:
            variables = json.load(f)
    else:
        print("An error has occurred, I could not acquire the variable file.")
        input("Press enter to exit")
        sys.exit(9)

    # Check version number.
    compare_versions(str(variables['version']), config_data["github"])

    # Mod selection logic
    if variables:
        modinstall.install(variables, config_data)
    else:
        print("Error: Failed to retrieve variables from the server.")

    print("Finished!")
    input("Press Enter to close the program...")
    sys.exit(0)

