import os
import argparse
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.formatters import ImageFormatter
from PIL import Image
from io import BytesIO

# Try to import Streamlit if available
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

INPUT_FOLDER = "codefiles"
OUTPUT_FOLDER = "codeimages"

os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def list_subfolders(folder):
    return [f for f in os.listdir(folder)
            if os.path.isdir(os.path.join(folder, f))]


def list_code_files(folder):
    all_files = []
    for root, _, files in os.walk(folder):
        for f in files:
            all_files.append(os.path.relpath(os.path.join(root, f), start=folder))
    return all_files


def code_to_png(code: str, file_path: str, output_path: str,
                font_name='Arial',
                font_size=38,
                line_numbers=False,
                style='monokai',
                image_pad=20) -> BytesIO:
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


# === STREAMLIT MODE ===
def run_streamlit():
    st.set_page_config(page_title="Live Code to PNG", layout="wide")
    st.title("🖋️ Code to PNG Converter")

    subfolders = [""] + list_subfolders(INPUT_FOLDER)
    selected_subfolder = st.selectbox("📁 Choose a subfolder (or root):", subfolders)
    folder_path = os.path.join(INPUT_FOLDER, selected_subfolder) if selected_subfolder else INPUT_FOLDER

    files = list_code_files(folder_path)

    if not files:
        st.warning(f"No files found in '{folder_path}'. Please add code files.")
        st.stop()

    col1, col2 = st.columns([2, 3])

    with col1:
        selected_file = st.selectbox("📄 Choose a file to preview:", files)
        file_path = os.path.join(folder_path, selected_file)

        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        code = st.text_area("✏️ Edit Code", value=code, height=300)

        st.subheader("🎨 Style Settings")
        font_name = st.selectbox("Font", ["DejaVu Sans Mono", "Courier New", "Arial", "Arial Unicode MS"], index=2)
        font_size = st.slider("Font Size", 10, 100, 38)
        image_pad = st.slider("Padding", 0, 100, 20)
        line_numbers = st.checkbox("Show Line Numbers", value=False)
        style = st.selectbox("Pygments Style", [
            "default", "monokai", "friendly", "colorful", "manni",
            "perldoc", "pastie", "borland", "trac", "native"
        ], index=1)

        generate_all = st.button("📦 Generate All PNGs from folder")

    with col2:
        st.subheader("🖼️ Live Preview")

        try:
            output_filename = selected_file.replace(os.sep, "_") + ".png"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            img_io = code_to_png(code, file_path, output_path,
                                 font_name, font_size, line_numbers, style, image_pad)

            st.image(Image.open(img_io), caption=output_filename, use_container_width=True)
            st.download_button("📥 Download PNG", data=img_io, file_name=output_filename, mime="image/png")

        except Exception as e:
            st.error(f"Error generating image: {e}")

    if generate_all:
        st.subheader("📊 Generating PNGs...")
        generated = 0
        for filename in files:
            full_path = os.path.join(folder_path, filename)
            output_file  = os.path.splitext(filename)[0] + ".png"
            output_path = os.path.join(OUTPUT_FOLDER, output_file)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                code_to_png(content, full_path, output_path,
                            font_name, font_size, line_numbers, style, image_pad)
                st.image(output_path, caption=output_file, use_container_width=True)
                generated += 1
            except Exception as e:
                st.error(f"❌ Failed: {filename}: {e}")

        st.success(f"✅ {generated} image(s) created in '{OUTPUT_FOLDER}'")


# === CLI MODE ===
def run_cli(input_path, all_mode):
    input_path = os.path.join(INPUT_FOLDER, input_path)
    if not os.path.exists(input_path):
        print(f"❌ Folder or file '{input_path}' not found.")
        return

    font_name = "Arial"
    font_size = 38
    image_pad = 20
    line_numbers = False
    style = "monokai"

    if all_mode:
        files = list_code_files(input_path)
        count = 0
        for f in files:
            file_path = os.path.join(input_path, f)
            output_file  = os.path.splitext(f)[0] + ".png"
            output_path = os.path.join(OUTPUT_FOLDER, output_file )
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(file_path, 'r', encoding='utf-8') as file:
                code = file.read()
            code_to_png(code, file_path, output_path,
                        font_name, font_size, line_numbers, style, image_pad)
            print(f"✅ Generated: {output_file}")
            count += 1
        print(f"\n🎉 Done! {count} PNGs saved in '{OUTPUT_FOLDER}'")
    else:
        if not os.path.isfile(input_path):
            print("❌ Provide a valid file path when not using --all")
            return
        with open(input_path, 'r', encoding='utf-8') as f:
            code = f.read()
        output_file = os.path.basename(input_path).replace(os.sep, "_") + ".png"
        output_path = os.path.join(OUTPUT_FOLDER, output_file)
        code_to_png(code, input_path, output_path,
                    font_name, font_size, line_numbers, style, image_pad)
        print(f"✅ PNG saved: {output_path}")


# === MAIN ENTRY ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Code to PNG converter")
    parser.add_argument("--cli", action="store_true", help="Run as CLI instead of Streamlit UI")
    parser.add_argument("--input", type=str, default="", help="Input file or folder inside codefiles/")
    parser.add_argument("--all", action="store_true", help="Generate PNGs for all code files in the folder")

    args = parser.parse_args()

    if args.cli:
        run_cli(args.input, args.all)
    elif STREAMLIT_AVAILABLE:
        run_streamlit()
    else:
        print("❌ Streamlit is not installed. Install it or use CLI mode with --cli.")
