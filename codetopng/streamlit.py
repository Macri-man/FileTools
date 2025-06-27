import os
import json
from io import BytesIO
import streamlit as st
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.formatters import ImageFormatter
from PIL import Image

SETTINGS_FILE = "settings.json"

class CodeToPNGStreamlit:
    def __init__(self, input_folder="codefiles", output_folder="codeimages"):
        self.INPUT_FOLDER = input_folder
        self.OUTPUT_FOLDER = output_folder
        os.makedirs(self.INPUT_FOLDER, exist_ok=True)
        os.makedirs(self.OUTPUT_FOLDER, exist_ok=True)

    def list_subfolders(self, folder):
        return [f for f in os.listdir(folder)
                if os.path.isdir(os.path.join(folder, f))]

    def list_code_files(self, folder):
        all_files = []
        for root, _, files in os.walk(folder):
            for f in files:
                all_files.append(os.path.relpath(os.path.join(root, f), start=folder))
        return all_files

    def code_to_png(self, code: str, file_path: str, output_path: str,
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

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(img_io.getvalue())

        return img_io

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Defaults if no file or error
    return {
        "font_name": "Arial",
        "font_size": 38,
        "image_pad": 20,
        "line_numbers": False,
        "style": "monokai"
    }

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f)
    except Exception as e:
        st.error(f"Failed to save settings: {e}")

def run_streamlit_ui():
    app = CodeToPNGStreamlit()

    st.set_page_config(page_title="Live Code to PNG", layout="wide")
    st.title("🖋️ Code to PNG Converter")

    # Load persistent settings from file
    persistent_settings = load_settings()

    # Initialize session_state with persistent settings if not present
    for key, val in persistent_settings.items():
        if key not in st.session_state:
            st.session_state[key] = val

    subfolders = [""] + app.list_subfolders(app.INPUT_FOLDER)
    selected_subfolder = st.selectbox("📁 Choose a subfolder (or root):", subfolders)
    folder_path = os.path.join(app.INPUT_FOLDER, selected_subfolder) if selected_subfolder else app.INPUT_FOLDER

    files = app.list_code_files(folder_path)
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

        font_name = st.selectbox(
            "Font",
            ["DejaVu Sans Mono", "Courier New", "Arial", "Arial Unicode MS"],
            index=["DejaVu Sans Mono", "Courier New", "Arial", "Arial Unicode MS"].index(st.session_state.font_name),
            key="font_name"
        )
        font_size = st.slider("Font Size", 10, 100, st.session_state.font_size, key="font_size")
        image_pad = st.slider("Padding", 0, 100, st.session_state.image_pad, key="image_pad")
        line_numbers = st.checkbox("Show Line Numbers", value=st.session_state.line_numbers, key="line_numbers")
        style = st.selectbox(
            "Pygments Style",
            [
                "default", "monokai", "friendly", "colorful", "manni",
                "perldoc", "pastie", "borland", "trac", "native"
            ],
            index=["default", "monokai", "friendly", "colorful", "manni",
                   "perldoc", "pastie", "borland", "trac", "native"].index(st.session_state.style),
            key="style"
        )

        # Save settings anytime they change
        save_settings({
            "font_name": st.session_state.font_name,
            "font_size": st.session_state.font_size,
            "image_pad": st.session_state.image_pad,
            "line_numbers": st.session_state.line_numbers,
            "style": st.session_state.style,
        })

        generate_all = st.button("📦 Generate All PNGs from folder")

    with col2:
        st.subheader("🖼️ Live Preview")
        try:
            output_file = os.path.splitext(selected_file)[0] + ".png"
            output_path = os.path.join(app.OUTPUT_FOLDER, output_file)

            img_io = app.code_to_png(code, file_path, output_path,
                                     st.session_state.font_name,
                                     st.session_state.font_size,
                                     st.session_state.line_numbers,
                                     st.session_state.style,
                                     st.session_state.image_pad)

            st.image(img_io, caption=output_file, use_container_width=True)
            st.download_button("📥 Download PNG", data=img_io, file_name=output_file, mime="image/png")

        except Exception as e:
            st.error(f"Error generating image: {e}")

    if generate_all:
        st.subheader("📊 Generating PNGs...")
        generated = 0
        for filename in files:
            full_path = os.path.join(folder_path, filename)
            output_file = os.path.splitext(filename)[0] + ".png"
            output_path = os.path.join(app.OUTPUT_FOLDER, filename)
            output_path = os.path.splitext(output_path)[0] + ".png"

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                app.code_to_png(content, full_path, output_path,
                                st.session_state.font_name,
                                st.session_state.font_size,
                                st.session_state.line_numbers,
                                st.session_state.style,
                                st.session_state.image_pad)
                st.image(output_path, caption=output_file, use_container_width=True)
                generated += 1
            except Exception as e:
                st.error(f"❌ Failed: {filename}: {e}")

        st.success(f"✅ {generated} image(s) created in '{app.OUTPUT_FOLDER}'")

if __name__ == "__main__":
    run_streamlit_ui()
