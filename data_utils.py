import os
import shutil
import json

ground_truth_data_path = "./data/ground_truth/"
run_data_root_path = "./data/run_data/"

def prepare_data_for_run():
    """Create a copy of test-data"""
    # print(get_run_data_path())
    run_data_path = get_run_data_path()
    copy_folder(ground_truth_data_path, run_data_path)
    return create_run_data_object(run_data_path)

def copy_folder(source, destination):
    print(f"copying from {source} to {destination}")
    try:
        shutil.copytree(source, destination)
        print(f"Folder copied successfully from {source} to {destination}")
    except FileExistsError:
        print(f"The destination folder '{destination}' already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_run_data_path():
    file_names_in_run_data_root = os.listdir(run_data_root_path)
    max_numeric_filename = get_max_numeric(file_names_in_run_data_root)
    next_numeric_filename = max_numeric_filename + 1 if max_numeric_filename is not None else 1
    return run_data_root_path + str(next_numeric_filename)

def get_max_numeric(filenames):
    numeric_filenames = [int(f) for f in filenames if f.isdigit()]
    print(f"numeric_filenames: {numeric_filenames}")
    if numeric_filenames:  # Check if there are any valid numbers
        max_number = max(numeric_filenames)
        print(f"The maximum number is: {max_number}")
        return max_number
    else:
        print("No numeric values found in the list.")
        return None

def create_run_data_object(run_folder_path):
    conversations = []
    conversation_folders = os.listdir(run_folder_path)
    for conversation_folder in conversation_folders:
        is_conversation_marked_for_skipping = os.path.basename(conversation_folder).startswith("skip")
        if (is_conversation_marked_for_skipping):
            continue

        conversation_data_path = f"{run_folder_path}/{conversation_folder}"
        input_path = f"{conversation_data_path}/input"
        sample_data_path = f"{input_path}/sample_data"
        parameters = read_json_from_file(f"{input_path}/input_params.json")
    
        input_files = [os.path.join(sample_data_path, file) for file in os.listdir(sample_data_path)] #os.listdir(sample_data_path) #FIXME

        conversation_data_path = None #FIXME
        conversation = {"parameters": parameters, "input_files": input_files, "data_path": conversation_data_path}
        conversations.append(conversation)

    return {"path": run_folder_path, "conversations": conversations}
   
def file_generator(folder_path):
    """
    A generator that yields files from a folder.

    :param folder_path: Path to the folder containing files.
    """
    try:
        # List all files in the directory
        files = os.listdir(folder_path)
        
        # Sort the files for consistent order (optional)
        files.sort()

        # Yield each file
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)

            # Check if it's a file (not a directory)
            if os.path.isfile(file_path):
                yield file_path
    except FileNotFoundError:
        print(f"Error: The folder '{folder_path}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied for folder '{folder_path}'.")

# Example usage
if __name__ == "__main__":
    folder_path = "./example_folder"  # Replace with the path to your folder

    # Create the generator
    file_gen = file_generator(folder_path)

    # Iterate through the generator
    for file in file_gen:
        print(f"Processing file: {file}")

def read_json_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    return data

def persist_assistant_output(conversation, data_model, comment):
    pass