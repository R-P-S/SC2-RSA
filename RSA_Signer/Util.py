# Util.py
import os
import configparser

def get_file_path(relative_path, description):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, relative_path)
    file_path = os.path.normpath(file_path)

    if not os.path.exists(file_path):
        print(f"Error: {description} not found - {file_path}")
        return None
    return file_path

def process_file(relative_path, description, modification_function, *args):
    file_path = get_file_path(relative_path, description)
    if file_path:
        modification_function(file_path, *args)

def read_keys_from_ini(ini_path):
    config = configparser.ConfigParser()
    config.read(ini_path)

    n = int(config['Keys']['n'])
    e = int(config['Keys']['e'])
    d = int(config['Keys']['d'])

    return n, e, d