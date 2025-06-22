import os
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.formatters import ImageFormatter
import streamlit as st
from PIL import Image
from io import BytesIO

# Absolute-style folders (without ./)
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
        image_pad=image_pad
    )

    img_io = BytesIO()
    img_io.write(highlight(code, lexer, formatter))
    img_io.seek(0)

    with open(output_path, 'wb') as f:
        f.write(img_io.getvalue())

    return img_io

# Streamlit app
st.set_page_config(page_title="Live Code to PNG", layout="wide")
st.title("🖋️ Live Code to PNG Converter")

col1, col2 = st.columns([2, 3])

with col1:
    files = list_code_files(INPUT_FOLDER)

    if not files:
        st.warning(f"No files found in '{INPUT_FOLDER}'. Please add code files.")
        st.stop()

    selected_file = st.selectbox("Choose a file from codefiles/", files)
    file_path = os.path.join(INPUT_FOLDER, selected_file)

    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    code = st.text_area("✏️ Edit Code", value=code, height=300)

    st.subheader("🎨 Style Settings")
    font_name = st.selectbox("Font", ["DejaVu Sans Mono", "Courier New", "Arial"])
    font_size = st.slider("Font Size", 10, 36, 18)
    image_pad = st.slider("Padding", 0, 50, 10)
    line_numbers = st.checkbox("Show Line Numbers", value=True)
    style = st.selectbox("Pygments Style", [
        "default", "monokai", "friendly", "colorful", "manni",
        "perldoc", "pastie", "borland", "trac", "native"
    ])

with col2:
    st.subheader("🖼️ PNG Preview")
    try:
        output_filename = selected_file + ".png"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        img_io = code_to_png(code, file_path, output_path,
                             font_name, font_size, line_numbers, style, image_pad)

        st.image(Image.open(img_io), caption="Rendered PNG", use_column_width=True)
        st.download_button("📥 Download PNG", data=img_io, file_name=output_filename, mime="image/png")

    except Exception as e:
        st.error(f"Error generating image: {e}")
