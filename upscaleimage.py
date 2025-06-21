import cv2
import numpy as np

# --- Parameters ---
input_filename = "piccode.jpg"                # Input image file (change if needed)
output_filename = "output_colored_image.jpg" # Output file name
brightness_threshold = 80                      # Threshold for dark pixel removal (0-255)
upscale_factor = 2                             # Upscale multiplier (e.g., 2 for double size)

# Step 1: Load image in BGR, convert to RGB for processing
img_bgr = cv2.imread(input_filename)
if img_bgr is None:
    raise FileNotFoundError(f"Input image not found: {input_filename}")
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

# Step 2: Convert to LAB color space to apply CLAHE only on luminance channel
img_lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
l, a, b = cv2.split(img_lab)

# Apply CLAHE on the L channel (luminance)
clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
l_clahe = clahe.apply(l)

# Merge back the enhanced L with original a and b channels
img_lab_clahe = cv2.merge((l_clahe, a, b))
enhanced_rgb = cv2.cvtColor(img_lab_clahe, cv2.COLOR_LAB2RGB)

# Step 3: Denoise the color image to reduce noise/artifacts
denoised_rgb = cv2.fastNlMeansDenoisingColored(enhanced_rgb, None, h=7, hColor=7,
                                               templateWindowSize=7, searchWindowSize=21)

# Step 4: Sharpen the denoised image with a sharpening kernel
sharpen_kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]], dtype=np.float32)
sharpened_rgb = cv2.filter2D(denoised_rgb, -1, sharpen_kernel)

# Step 5: Calculate perceived brightness (luminance) for masking in float for accuracy
brightness = (0.2126 * sharpened_rgb[:, :, 0].astype(np.float32) +
              0.7152 * sharpened_rgb[:, :, 1].astype(np.float32) +
              0.0722 * sharpened_rgb[:, :, 2].astype(np.float32))

# Step 6: Mask out low-brightness pixels by setting them to black
mask = brightness < brightness_threshold
sharpened_rgb[mask] = [0, 0, 0]

# Step 7: Upscale the cleaned, sharpened image using high-quality interpolation
new_size = (int(sharpened_rgb.shape[1] * upscale_factor), int(sharpened_rgb.shape[0] * upscale_factor))
upscaled_rgb = cv2.resize(sharpened_rgb, new_size, interpolation=cv2.INTER_LANCZOS4)

# Step 8: Convert back to BGR for saving with OpenCV
final_bgr = cv2.cvtColor(upscaled_rgb, cv2.COLOR_RGB2BGR)

# Step 9: Save the output image
cv2.imwrite(output_filename, final_bgr)
print(f"Processed image saved as: {output_filename}")

# Step 10: Optional — display the result image in a window
cv2.imshow("Enhanced and Upscaled Image", final_bgr)
cv2.waitKey(0)
cv2.destroyAllWindows()
