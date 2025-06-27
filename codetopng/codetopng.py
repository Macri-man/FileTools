import os
import sys
from io import BytesIO
from PIL import Image
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.formatters import ImageFormatter

# Attempt to import streamlit
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


class CodeToPNGApp:
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

        # Ensure output folder exists (including subfolders)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(img_io.getvalue())

        return img_io

    def run_streamlit(self):
        st.set_page_config(page_title="Live Code to PNG", layout="wide")
        st.title("🖋️ Code to PNG Converter")

        subfolders = [""] + self.list_subfolders(self.INPUT_FOLDER)
        selected_subfolder = st.selectbox("📁 Choose a subfolder (or root):", subfolders)
        folder_path = os.path.join(self.INPUT_FOLDER, selected_subfolder) if selected_subfolder else self.INPUT_FOLDER

        files = self.list_code_files(folder_path)
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
                output_file = os.path.splitext(selected_file)[0] + ".png"
                output_path = os.path.join(self.OUTPUT_FOLDER, output_file)

                img_io = self.code_to_png(code, file_path, output_path,
                                          font_name, font_size, line_numbers, style, image_pad)

                st.image(Image.open(img_io), caption=output_file, use_container_width=True)
                st.download_button("📥 Download PNG", data=img_io, file_name=output_file, mime="image/png")

            except Exception as e:
                st.error(f"Error generating image: {e}")

        if generate_all:
            st.subheader("📊 Generating PNGs...")
            generated = 0
            for filename in files:
                full_path = os.path.join(folder_path, filename)
                output_file = os.path.splitext(filename)[0] + ".png"
                output_path = os.path.join(self.OUTPUT_FOLDER, output_file)

                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.code_to_png(content, full_path, output_path,
                                     font_name, font_size, line_numbers, style, image_pad)
                    st.image(output_path, caption=output_file, use_container_width=True)
                    generated += 1
                except Exception as e:
                    st.error(f"❌ Failed: {filename}: {e}")

            st.success(f"✅ {generated} image(s) created in '{self.OUTPUT_FOLDER}'")

    def run_cli(self, input_path: str, all_mode: bool):
        input_path = os.path.join(self.INPUT_FOLDER, input_path)
        if not os.path.exists(input_path):
            print(f"❌ Folder or file '{input_path}' not found.")
            return

        font_name = "Arial"
        font_size = 38
        image_pad = 20
        line_numbers = False
        style = "monokai"

        if all_mode:
            files = self.list_code_files(input_path)
            count = 0
            for f in files:
                file_path = os.path.join(input_path, f)
                output_file = os.path.splitext(f)[0] + ".png"
                output_path = os.path.join(self.OUTPUT_FOLDER, output_file)

                with open(file_path, 'r', encoding='utf-8') as file:
                    code = file.read()
                self.code_to_png(code, file_path, output_path,
                                 font_name, font_size, line_numbers, style, image_pad)
                print(f"✅ Generated: {output_file}")
                count += 1
            print(f"\n🎉 Done! {count} PNGs saved in '{self.OUTPUT_FOLDER}'")
        else:
            if not os.path.isfile(input_path):
                print("❌ Provide a valid file path when not using folder mode")
                return
            with open(input_path, 'r', encoding='utf-8') as f:
                code = f.read()
            output_file = os.path.basename(input_path) + ".png"
            output_path = os.path.join(self.OUTPUT_FOLDER, output_file)
            self.code_to_png(code, input_path, output_path,
                             font_name, font_size, line_numbers, style, image_pad)
            print(f"✅ PNG saved: {output_path}")


def is_running_streamlit() -> bool:
    # Streamlit sets this env var when running your app
    if os.environ.get("STREAMLIT_SERVER_RUNNING") == "1":
        return True
    # Also check if script was launched via 'streamlit run' command (argv contains 'streamlit')
    if any("streamlit" in arg for arg in sys.argv):
        return True
    return False


def main():
    app = CodeToPNGApp()

    if STREAMLIT_AVAILABLE and is_running_streamlit():
        # Run Streamlit UI only
        app.run_streamlit()
    else:
        # CLI mode
        args = sys.argv[1:]
        if not args:
            # No args = generate all PNGs from root input folder
            app.run_cli("", all_mode=True)
        else:
            rel_path = args[0]
            full_path = os.path.join(app.INPUT_FOLDER, rel_path)
            if os.path.isdir(full_path):
                app.run_cli(rel_path, all_mode=True)
            elif os.path.isfile(full_path):
                app.run_cli(rel_path, all_mode=False)
            else:
                print(f"❌ Path '{rel_path}' not found in '{app.INPUT_FOLDER}'")


if __name__ == "__main__":
    main()
