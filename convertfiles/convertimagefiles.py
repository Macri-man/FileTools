import os
from PIL import Image

def convert_images(input_folder, output_folder, target_format):
    os.makedirs(output_folder, exist_ok=True)
    
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        
        # Skip if not a file
        if not os.path.isfile(input_path):
            continue
        
        try:
            with Image.open(input_path) as img:
                base_name = os.path.splitext(filename)[0]
                output_path = os.path.join(output_folder, base_name + '.' + target_format.lower())
                
                # Convert to RGB if saving to JPEG (which doesn't support transparency)
                if target_format.lower() in ['jpg', 'jpeg'] and img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                img.save(output_path, target_format.upper())
                print(f"Converted {filename} -> {output_path}")
        
        except Exception as e:
            print(f"Failed to convert {filename}: {e}")

if __name__ == "__main__":
    input_folder = "input_images"
    output_folder = "output_images"
    target_format = "png"  # Change to your target format, e.g., jpg, bmp, tiff, webp
    
    convert_images(input_folder, output_folder, target_format)
