import winreg
import os
import sys
import json
import main


RUNTIME_CONFIG_PATH = str(os.path.join(os.path.expanduser("~"), ".modinstallrc"))
# Default dictionary to populate the JSON file if it doesn't exist
DEFAULT_CONFIG = {
    "scriptURL": "example.com",
    "github": "https://github.com/RagingFlames/Fire-Mod-Updater/releases/latest",
    "custom_install_locations": {},
    "quick_extract": "True",
    "actions": "False"
}
REQUIRED_KEYS = ["scriptURL", "github"]

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

    # Check and make sure the required variables are present
    make_changes = False
    for key in REQUIRED_KEYS:
        if key not in config_data:
            print(f"Adding required key '{key}' to your config file.")
            config_data[key] = DEFAULT_CONFIG[key]
            make_changes = True
    # Write changes back to the config file
    if make_changes:
        with open(RUNTIME_CONFIG_PATH, "w") as file:
            json.dump(config_data, file)
    
    return config_data

def write_config(file_path):
    # Write the default config to the file
    with open(file_path, "w") as file:
        json.dump(DEFAULT_CONFIG, file, indent=4)
    print("Please go update your config with the default settings your group uses.")
    input("Press Enter to exit...")
    sys.exit(0)

def add_to_config(key, value):
    config_data = read_config_file()
    if key in config_data:
        print(f"Updating '{key}' from {config_data[key]} to {value}.")
    else:
        print(f"Adding new configuration option '{key}': {value}.")  
    config_data[key] = value
    with open(RUNTIME_CONFIG_PATH, "w") as file:
        json.dump(config_data, file, indent=4)

def get_user_url(config_data):
    print("The updates link is not working. Who ever is making modpacks for you should know what the url is.")
    url = input("Please enter the correct URL: ")
    config_data["scriptURL"] = url
    
    with open(RUNTIME_CONFIG_PATH, "w") as f:
        json.dump(config_data, f, indent=4)
    
    print(f"Updated scriptURL in config file to {url}")
    
    return main.download_file(config_data)

def find_7z_path():
    registry_paths = [
        r"SOFTWARE\7-Zip",
        r"SOFTWARE\WOW6432Node\7-Zip",  # for 32-bit 7-Zip on 64-bit Windows
    ]

    for reg_path in registry_paths:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                install_path, _ = winreg.QueryValueEx(key, "Path")
                exe_path = os.path.join(install_path, "7zG.exe")
                if os.path.isfile(exe_path):
                    add_to_config("7z_path", exe_path)
                    return exe_path
        except FileNotFoundError:
            continue  # Try the next registry path

    return None  # Not found

