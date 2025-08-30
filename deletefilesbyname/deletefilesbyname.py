import os
import argparse

def delete_files(folder_path, include_elements=None, exclude_elements=None):
    """
    Delete files in a folder based on filename elements.

    Parameters:
    - folder_path (str): Path to the folder.
    - include_elements (list of str): Only delete files that contain any of these elements.
    - exclude_elements (list of str): Only delete files that DO NOT contain any of these elements.
    """
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if not os.path.isfile(file_path):
            continue  # Skip subfolders

        # Check inclusion
        if include_elements and not any(elem in filename for elem in include_elements):
            continue  # Skip if filename doesn't have required elements

        # Check exclusion
        if exclude_elements and any(elem in filename for elem in exclude_elements):
            continue  # Skip if filename has excluded elements

        # Delete the file
        try:
            os.remove(file_path)
            print(f"Deleted: {filename}")
        except Exception as e:
            print(f"Failed to delete {filename}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Delete files based on filename elements.")
    parser.add_argument("folder", help="Path to the folder containing files")
    parser.add_argument("--include", "-i", help="Comma-separated words to include in filenames", default="")
    parser.add_argument("--exclude", "-e", help="Comma-separated words to exclude from filenames", default="")

    args = parser.parse_args()

    include_elements = [x.strip() for x in args.include.split(",")] if args.include else None
    exclude_elements = [x.strip() for x in args.exclude.split(",")] if args.exclude else None

    delete_files(args.folder, include_elements, exclude_elements)

if __name__ == "__main__":
    main()
