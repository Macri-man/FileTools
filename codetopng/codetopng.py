import os
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.formatters import ImageFormatter
import streamlit as st
from PIL import Image
from io import BytesIO

# Input/Output folders
INPUT_FOLDER = "codefiles"
OUTPUT_FOLDER = "codeimages"

os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def list_code_files(folder):
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

def code_to_png(code: str, file_path: str, output_path: str,
                font_name='DejaVu Sans Mono',
                font_size=18,
                line_numbers=True,
                style='monokai',
                image_pad=10) -> BytesIO:
    try:
        lexer = get_lexer_for_filename(file_path)
    except Exception:
        lexer = guess_lexer(code)

    formatter = ImageFormatter(
        font_name=font_name,
        font_size=font_size,
        line_numbers=line_numbers,
        style=style,
        image_pad=image_pad,
        dpi=300
    )

    img_io = BytesIO()
    img_io.write(highlight(code, lexer, formatter))
    img_io.seek(0)

    with open(output_path, 'wb') as f:
        f.write(img_io.getvalue())

    return img_io

# Streamlit app
st.set_page_config(page_title="Live Code to PNG", layout="wide")
st.title("🖋️ Code to PNG Converter")

col1, col2 = st.columns([2, 3])

with col1:
    files = list_code_files(INPUT_FOLDER)

    if not files:
        st.warning(f"No files found in '{INPUT_FOLDER}'. Please add code files.")
        st.stop()

    selected_file = st.selectbox("Choose a file to preview:", files)
    file_path = os.path.join(INPUT_FOLDER, selected_file)

    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    code = st.text_area("✏️ Edit Code", value=code, height=300)

    st.subheader("🎨 Style Settings")
    font_name = st.selectbox("Font", ["DejaVu Sans Mono", "Courier New", "Arial"])
    font_size = st.slider("Font Size", 10, 40, 18)
    image_pad = st.slider("Padding", 0, 100, 10)
    line_numbers = st.checkbox("Show Line Numbers", value=True)
    style = st.selectbox("Pygments Style", [
        "default", "monokai", "friendly", "colorful", "manni",
        "perldoc", "pastie", "borland", "trac", "native"
    ])

    generate_all = st.button("📦 Generate All PNGs from codefiles")

with col2:
    st.subheader("🖼️ Live Preview of Selected File")

    try:
        output_filename = selected_file + ".png"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        img_io = code_to_png(code, file_path, output_path,
                             font_name, font_size, line_numbers, style, image_pad)

        st.image(Image.open(img_io), caption=f"{output_filename}", use_column_width=True)
        st.download_button("📥 Download This PNG", data=img_io, file_name=output_filename, mime="image/png")

    except Exception as e:
        st.error(f"Error generating image for selected file: {e}")

# --- Bulk Generation ---
if generate_all:
    st.subheader("📊 Generating All PNGs from codefiles/")
    generated = 0
    for filename in files:
        file_path = os.path.join(INPUT_FOLDER, filename)
        output_file = filename + ".png"
        output_path = os.path.join(OUTPUT_FOLDER, output_file)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            code_to_png(content, file_path, output_path,
                        font_name, font_size, line_numbers, style, image_pad)
            st.image(output_path, caption=output_file, use_column_width=True)
            generated += 1
        except Exception as e:
            st.error(f"Failed to generate {filename}: {e}")

    st.success(f"✅ Generated {generated} PNG file(s) into '{OUTPUT_FOLDER}'")
