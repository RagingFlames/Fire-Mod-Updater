import os
import importlib.util
import actions

def load_modules(directory):
    modules = {}

    for filename in os.listdir(directory):
        if filename.endswith(".py") and not filename.startswith("_"):
            module_name = filename[:-3]  # strip .py
            file_path = os.path.join(directory, filename)

            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            modules[module_name] = module

    return modules

def run_command(command, plugins):
    start = command.find("(")
    end = command.find(")", start)

    if start == -1 or end == -1:
        argument = []

    inside = command[start + 1:end]
    argument = [item.strip() for item in inside.split(",") if item.strip()]

    # Check actions.py
    if hasattr(actions, command):
        func = getattr(actions, command)
        if callable(func):
            return func(argument)

    # # Check plugins
    # for plugin in plugins:
    #     if hasattr(plugin, command):
    #         func = getattr(plugin, command)
    #         if callable(func):
    #             return func(argument)

    raise ValueError(f"Command '{command}' not found in actions or plugins")
