import os
import argparse
from PIL import Image

def check_files(folder_path):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    if not files:
        print("No files found in the folder.")
        return

    # --- Check file sizes ---
    sizes = {}
    for f in files:
        path = os.path.join(folder_path, f)
        sizes[f] = os.path.getsize(path)

    unique_sizes = set(sizes.values())
    if len(unique_sizes) == 1:
        print(f"✅ All files are the same size: {unique_sizes.pop()} bytes")
    else:
        print("❌ Files have different sizes:")
        for f, s in sizes.items():
            print(f"  {f}: {s} bytes")

    # --- Check image resolutions ---
    resolutions = {}
    for f in files:
        path = os.path.join(folder_path, f)
        try:
            with Image.open(path) as img:
                resolutions[f] = img.size  # (width, height)
        except Exception:
            continue  # skip non-images

    if resolutions:
        unique_res = set(resolutions.values())
        if len(unique_res) == 1:
            print(f"✅ All images have the same resolution: {unique_res.pop()[0]}x{unique_res.pop()[1]}")
        else:
            print("❌ Images have different resolutions:")
            for f, r in resolutions.items():
                print(f"  {f}: {r[0]}x{r[1]}")
    else:
        print("ℹ️ No images found in the folder.")


def main():
    parser = argparse.ArgumentParser(
        description="Check if all files in a folder are the same size and if images have the same resolution."
    )
    parser.add_argument("folder", help="Path to the folder to check")
    args = parser.parse_args()

    check_files(args.folder)


if __name__ == "__main__":
    main()
