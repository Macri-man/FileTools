import os
from io import BytesIO
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, guess_lexer, get_lexer_by_name
from pygments.formatters import ImageFormatter
from pygments.styles import get_all_styles
from pygments.util import ClassNotFound

class CodeToPNGConverter:
    def __init__(self, input_folder="codefiles", output_folder="codeimages"):
        self.INPUT_FOLDER = input_folder
        self.OUTPUT_FOLDER = output_folder
        os.makedirs(self.INPUT_FOLDER, exist_ok=True)
        os.makedirs(self.OUTPUT_FOLDER, exist_ok=True)

    def list_subfolders(self, folder):
        return [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]

    def list_code_files(self, folder):
        all_files = []
        for root, _, files in os.walk(folder):
            for f in files:
                all_files.append(os.path.relpath(os.path.join(root, f), start=folder))
        return all_files

    def code_to_png(self, code: str, file_path: str, output_path: str,
                    font_name='Arial', font_size=38, line_numbers=False,
                    style='monokai', image_pad=20, border=10, dpi=300,
                    lang=None) -> BytesIO:
        # --- Detect lexer ---
        try:
            if lang:
                lexer = get_lexer_by_name(lang)
            else:
                lexer = get_lexer_for_filename(file_path)
        except ClassNotFound:
            try:
                lexer = guess_lexer(code)
            except ClassNotFound:
                raise ValueError(f"Cannot detect lexer for: {file_path}")

        # --- Validate style ---
        available_styles = list(get_all_styles())
        if style not in available_styles:
            print(f"⚠️ Warning: Style '{style}' not found. Using default 'monokai'.")
            style = 'monokai'

        # --- Generate PNG ---
        formatter = ImageFormatter(
            font_name=font_name,
            font_size=font_size,
            line_numbers=line_numbers,
            style=style,
            image_pad=image_pad,
            line_pad=2,
            image_border=border,
            dpi=dpi
        )

        img_io = BytesIO()
        try:
            img_io.write(highlight(code, lexer, formatter))
            img_io.seek(0)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(img_io.getvalue())
        except Exception as e:
            print(f"❌ Failed to generate PNG for {file_path}: {e}")
            return None

        return img_io
