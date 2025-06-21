import cv2
import numpy as np
from PIL import Image
import torch
from realesrgan import RealESRGAN

# === Load Image ===
input_path = "input.jpg"  # your RGB image
output_path = "output_upscaled.jpg"

# Read image (OpenCV loads in BGR)
bgr = cv2.imread(input_path)
rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)  # ensure it's RGB

# === Denoise (Optional) ===
denoised = cv2.fastNlMeansDenoisingColored(bgr, None, 10, 10, 7, 21)

# === Sharpen (helps with blurry text) ===
kernel = np.array([[0, -1, 0],
                   [-1, 5, -1],
                   [0, -1, 0]])
sharpened = cv2.filter2D(denoised, -1, kernel)

# Convert to RGB for PIL (RealESRGAN uses PIL images)
rgb_sharpened = cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB)
pil_img = Image.fromarray(rgb_sharpened)

# === Load Real-ESRGAN Model ===
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = RealESRGAN(device, scale=4)
model.load_weights('RealESRGAN_x4.pth')  # Download: https://github.com/xinntao/Real-ESRGAN

# === Upscale ===
sr_image = model.predict(pil_img)  # Super-resolved RGB PIL image

# === Save Output ===
sr_image.save(output_path)
print(f"Upscaled image saved to {output_path}")
