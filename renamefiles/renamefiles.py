import os
import argparse

def rename_files_in_folder(folder_path, recursive=False, padding=0):
    if recursive:
        walker = os.walk(folder_path)
    else:
        walker = [(folder_path, [], [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])]

    for root, _, files in walker:
        files.sort()

        if not files:
            continue

        # Determine padding automatically if not given
        total_files = len(files)
        if padding == 0:
            pad = len(str(total_files))
        else:
            pad = padding

        # Step 1: rename to temporary names
        temp_names = []
        for idx, filename in enumerate(files, start=1):
            ext = os.path.splitext(filename)[1]
            temp_name = f"__temp_{idx}{ext}"
            old_path = os.path.join(root, filename)
            temp_path = os.path.join(root, temp_name)
            os.rename(old_path, temp_path)
            temp_names.append(temp_name)

        # Step 2: rename to final numbered names
        for idx, temp_name in enumerate(temp_names, start=1):
            ext = os.path.splitext(temp_name)[1]
            new_name = f"{str(idx).zfill(pad)}{ext}"
            old_path = os.path.join(root, temp_name)
            new_path = os.path.join(root, new_name)
            os.rename(old_path, new_path)
            print(f"Renamed: {old_path} -> {new_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Rename all files in a folder (and optionally subfolders) sequentially starting from 1."
    )
    parser.add_argument("folder", help="Path to the folder containing files to rename")
    parser.add_argument("-r", "--recursive", action="store_true", help="Include subfolders")
    parser.add_argument("-p", "--padding", type=int, default=0,
                        help="Number of digits for zero-padding (default auto based on file count)")

    args = parser.parse_args()
    rename_files_in_folder(args.folder, args.recursive, args.padding)


if __name__ == "__main__":
    main()
