import requests
import os.path
import tqdm
import random
import string

# Print message to the screen
def prompt(message):
        print(message)

# Ask the user for information and store it in the specified variable
def ask(message):
    response = input(message)

# Download file to downloads folder
def download(url, file_name):
        #random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
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

# Download a single file and move it somewhere
def move(file, destination):
     

