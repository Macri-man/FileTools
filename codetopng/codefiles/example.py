import os
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.formatters import ImageFormatter
import streamlit as st
from PIL import Image

INPUT_FOLDER = 'codefiles'
OUTPUT_FOLDER = 'codeimages'

def code_to_png(code: str, file_path: str, output_path: str,
                font_name='DejaVu Sans Mono', font_size=18,
                line_numbers=True, style='monokai', image_pad=10):
    try:
        lexer = get_lexer_for_filename(file_path)
    except Exception:
        lexer = guess_lexer(code)

    formatter = ImageFormatter(
        font_name=font_name,
        font_size=font_size,
        line_numbers=line_numbers,
        style=style,
        image_pad=image_pad
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'wb') as f:
        f.write(highlight(code, lexer, formatter))

    return output_path

def list_code_files(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        return []  # No files yet
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]


# --- Streamlit UI ---
st.title("📄 Code Snippet to PNG Converter")

files = list_code_files(INPUT_FOLDER)

if not files:
    st.warning(f"No code files found in {INPUT_FOLDER}. Please add files first.")
else:
    selected_file = st.selectbox("Choose a code file:", files)

    with open(os.path.join(INPUT_FOLDER, selected_file), 'r', encoding='utf-8') as f:
        code = f.read()

    st.subheader("📘 Code Preview")
    st.code(code, language='')

    if st.button("✨ Generate PNG"):
        input_path = os.path.join(INPUT_FOLDER, selected_file)
        output_path = os.path.join(OUTPUT_FOLDER, selected_file + ".png")

        img_path = code_to_png(code, input_path, output_path)

        st.success(f"PNG created at {img_path}")
        st.image(Image.open(img_path), caption="Preview of Generated PNG")
