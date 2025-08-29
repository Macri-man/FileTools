import os
import math
import argparse
import random
from PIL import Image


def parse_color(color_str):
    """Parse color string (name, RGB tuple, or hex)."""
    if color_str.startswith("#"):
        color_str = color_str.lstrip("#")
        if len(color_str) == 6:
            r, g, b = tuple(int(color_str[i:i+2], 16) for i in (0, 2, 4))
            return (r, g, b)
        else:
            raise ValueError("Hex color must be in format #RRGGBB")
    elif "," in color_str:
        parts = color_str.split(",")
        if len(parts) == 3:
            return tuple(int(p.strip()) for p in parts)
        else:
            raise ValueError("RGB color must have 3 components (R,G,B)")
    else:
        named_colors = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "gray": (128, 128, 128),
        }
        return named_colors.get(color_str.lower(), (255, 255, 255))


def make_collage(folder_path, output_path="collage.jpg", total_size=1024,
                 padding=5, bg_color=(255, 255, 255), shuffle=False,
                 cols=None, rows=None):
    # Collect images
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f))]
    image_paths = []
    for f in files:
        try:
            Image.open(f).close()
            image_paths.append(f)
        except Exception:
            continue

    if not image_paths:
        print("❌ No images found in folder.")
        return

    if shuffle:
        random.shuffle(image_paths)
    else:
        image_paths.sort()

    num_images = len(image_paths)

    # Determine grid size
    if cols is None and rows is None:
        grid_cols = math.ceil(math.sqrt(num_images))
        grid_rows = math.ceil(num_images / grid_cols)
    elif cols is not None:
        grid_cols = cols
        grid_rows = math.ceil(num_images / grid_cols)
    elif rows is not None:
        grid_rows = rows
        grid_cols = math.ceil(num_images / grid_rows)

    # Calculate per-thumbnail size based on total width
    thumb_size = (total_size - (grid_cols - 1) * padding) // grid_cols
    collage_width = total_size
    collage_height = grid_rows * thumb_size + (grid_rows - 1) * padding

    collage = Image.new("RGB", (collage_width, collage_height), bg_color)

    # Place images
    for index, path in enumerate(image_paths):
        try:
            img = Image.open(path).convert("RGB")
            img.thumbnail((thumb_size, thumb_size), Image.LANCZOS)

            square_img = Image.new("RGB", (thumb_size, thumb_size), bg_color)
            offset_x = (thumb_size - img.size[0]) // 2
            offset_y = (thumb_size - img.size[1]) // 2
            square_img.paste(img, (offset_x, offset_y))

            row = index // grid_cols
            col = index % grid_cols
            x = col * (thumb_size + padding)
            y = row * (thumb_size + padding)

            collage.paste(square_img, (x, y))
        except Exception as e:
            print(f"⚠️ Skipping {path}: {e}")

    collage.save(output_path)
    print(f"✅ Collage saved as {output_path} ({collage_width}x{collage_height})")


def main():
    parser = argparse.ArgumentParser(description="Create a collage from all images in a folder.")
    parser.add_argument("folder", help="Path to the folder with images")
    parser.add_argument("-o", "--output", default="collage.jpg", help="Output collage filename")
    parser.add_argument("-s", "--size", type=int, default=1024,
                        help="Total width of the final collage (default: 1024)")
    parser.add_argument("-p", "--padding", type=int, default=5, help="Padding between images")
    parser.add_argument("-b", "--bgcolor", default="white", help="Background color")
    parser.add_argument("--shuffle", action="store_true", help="Shuffle images")
    parser.add_argument("--cols", type=int, help="Number of columns")
    parser.add_argument("--rows", type=int, help="Number of rows")

    args = parser.parse_args()
    bg_color = parse_color(args.bgcolor)

    make_collage(args.folder, args.output, args.size, args.padding,
                 bg_color, args.shuffle, args.cols, args.rows)


if __name__ == "__main__":
    main()
