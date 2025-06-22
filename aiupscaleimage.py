import cv2
import numpy as np
import subprocess
import os

# Configuration
input_folder = os.path.abspath("inputupscaleimage")
temp_input_path = os.path.abspath("Real-ESRGAN/inputs/input_temp.jpg")
real_esrgan_script = os.path.abspath("Real-ESRGAN/inference_realesrgan.py")
real_esrgan_output_dir = os.path.abspath("Real-ESRGAN/results")
output_folder = os.path.abspath("outputupscaleimage")
model_name = "RealESRGAN_x4plus"

# Ensure necessary directories exist
os.makedirs(output_folder, exist_ok=True)
os.makedirs(os.path.dirname(temp_input_path), exist_ok=True)
os.makedirs(real_esrgan_output_dir, exist_ok=True)

# Valid image extensions
valid_exts = (".jpg", ".jpeg", ".png", ".bmp")

# Loop over input images
for filename in os.listdir(input_folder):
    if not filename.lower().endswith(valid_exts):
        continue

    input_path = os.path.join(input_folder, filename)
    output_filename = os.path.splitext(filename)[0] + "_upscaled.jpg"
    final_output_path = os.path.join(output_folder, output_filename)

    print(f"🔄 Processing {filename}...")

    # Load and check image
    img = cv2.imread(input_path)
    if img is None:
        print(f"❌ Failed to read: {input_path}")
        continue

    # Denoise
    denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

    # Sharpen
    sharpen_kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])
    sharpened = cv2.filter2D(denoised, -1, kernel=sharpen_kernel)

    # Save temp input
    cv2.imwrite(temp_input_path, sharpened)

    # Call Real-ESRGAN
    result = subprocess.run([
        "python", real_esrgan_script,
        "-i", temp_input_path,
        "-n", model_name,
        "--outscale", "4"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Real-ESRGAN failed:\n{result.stderr}")
        continue

    # Move generated output
    real_output = os.path.join(real_esrgan_output_dir, "input_temp_out.jpg")
    if not os.path.exists(real_output):
        print(f"❌ Output not found: {real_output}")
        continue

    os.rename(real_output, final_output_path)
    print(f"✅ Saved to: {final_output_path}")
