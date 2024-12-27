def all():
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