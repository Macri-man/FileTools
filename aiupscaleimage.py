import cv2
import numpy as np
import subprocess
import os

# Configuration
input_folder = os.path.abspath("inputupscaleimage")
temp_input_dir = os.path.abspath("Real-ESRGAN/inputs")
real_esrgan_script = os.path.abspath("Real-ESRGAN/inference_realesrgan.py")
real_esrgan_output_dir = os.path.abspath("Real-ESRGAN/results")
output_folder = os.path.abspath("outputupscaleimage")
model_name = "RealESRGAN_x4plus"

# Ensure necessary directories exist
os.makedirs(output_folder, exist_ok=True)
os.makedirs(temp_input_dir, exist_ok=True)
os.makedirs(real_esrgan_output_dir, exist_ok=True)

print(f"Input folder: {input_folder}")
print(f"Output folder: {output_folder}")
print(f"Real-ESRGAN script: {real_esrgan_script}")
print(f"Real-ESRGAN output dir: {real_esrgan_output_dir}")
print(f"Model name: {model_name}")

# Valid image extensions
valid_exts = (".jpg", ".jpeg", ".png", ".bmp")

# Loop over input images
for filename in os.listdir(input_folder):
    if not filename.lower().endswith(valid_exts):
        continue

    input_path = os.path.join(input_folder, filename)
    base_name = os.path.splitext(filename)[0]
    temp_input_path = os.path.join(temp_input_dir, f"input_{base_name}.jpg")
    output_filename = f"{base_name}_upscaled.jpg"
    final_output_path = os.path.join(output_folder, output_filename)

    print(f"\n🔄 Processing {filename}...")
    print(f"Input:  {input_path}")
    print(f"Output: {final_output_path}")

    if os.path.exists(final_output_path):
        print(f"✅ Skipping: {filename} (already processed)")
        continue

    # Load and check image
    img = cv2.imread(input_path)
    if img is None:
        print(f"❌ Failed to read: {input_path}")
        continue

    # Denoise color image
    denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

    # Sharpen
    sharpen_kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])
    sharpened = cv2.filter2D(denoised, -1, kernel=sharpen_kernel)

    # Save preprocessed temp image
    cv2.imwrite(temp_input_path, sharpened)
    print(f"✅ Saved to: {temp_input_path}")

    # Call Real-ESRGAN
    result = subprocess.run([
        "python", real_esrgan_script,
        "-i", temp_input_path,
        "-n", model_name,
        "--outscale", "4",
        "--suffix", "out"
    ], capture_output=True, text=True)

    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    if result.returncode != 0:
        print(f"❌ Real-ESRGAN failed:\n{result.stderr}")
        continue

    # Look for expected output
    real_output_filename = f"input_{base_name}_out.jpg"
    real_output_path = os.path.join(real_esrgan_output_dir, real_output_filename)

    if not os.path.exists(real_output_path):
        print(f"❌ Output not found: {real_output_path}")
        continue

    os.rename(real_output_path, final_output_path)
    print(f"✅ Upscaled image saved to: {final_output_path}")
