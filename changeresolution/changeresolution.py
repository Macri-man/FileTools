import os
import argparse
from PIL import Image

def resize_images(folder_path, width, height, overwrite=False):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    for f in files:
        path = os.path.join(folder_path, f)
        try:
            with Image.open(path) as img:
                if img.size == (width, height):
                    print(f"⏭ Skipping {f} (already {width}x{height})")
                    continue

                # Resize with high-quality resampling
                resized = img.resize((width, height), Image.LANCZOS)

                if overwrite:
                    save_path = path
                else:
                    name, ext = os.path.splitext(f)
                    save_path = os.path.join(folder_path, f"{name}_{width}x{height}{ext}")

                resized.save(save_path)
                print(f"✅ Resized {f} -> {save_path}")

        except Exception as e:
            print(f"⚠️ Skipping {f}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Resize all images in a folder to a given resolution. Skips images already at that resolution."
    )
    parser.add_argument("folder", help="Path to the folder with images")
    parser.add_argument("width", type=int, help="Target width")
    parser.add_argument("height", type=int, help="Target height")
    parser.add_argument("-o", "--overwrite", action="store_true", help="Overwrite original files instead of saving new ones")

    args = parser.parse_args()
    resize_images(args.folder, args.width, args.height, args.overwrite)


if __name__ == "__main__":
    main()
