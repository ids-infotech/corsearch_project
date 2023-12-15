import os
import glob

def delete_temp_files(temp_folder, delete_all=False, file_patterns=None):
    """
    Delete files in the temp folder based on the specified criteria.

    Parameters:
    - temp_folder (str): The path to the temp folder.
    - delete_all (bool): If True, delete all files in the temp folder.
    - file_patterns (list): List of file patterns (wildcards) to match for deletion.
    """
    if delete_all:
        files_to_delete = glob.glob(os.path.join(temp_folder, '*'))
    elif file_patterns:
        files_to_delete = []
        for pattern in file_patterns:
            files_to_delete.extend(glob.glob(os.path.join(temp_folder, pattern)))
    else:
        print("No files specified for deletion. Provide either file patterns or set delete_all to True.")
        return

    # Delete files
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except OSError as e:
            print(f"Error deleting {file_path}: {e}")

# Example usage:

# Your code to generate the final JSON output goes here

# Specify the path to your temp folder
# temp_folder_path = "/path/to/your/temp/folder"  # Replace this with the actual path to your temp folder

'''
# Use the function to delete specific files or all files
delete_temp_files(temp_folder_path, delete_all=True)  # Delete all files
# OR
delete_temp_files(temp_folder_path, file_patterns=["*.json", "temp_file.txt"])  # Delete specific files
'''