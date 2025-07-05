# converter.py

import os
from io import BytesIO
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.formatters import ImageFormatter

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
                    style='monokai', image_pad=20) -> BytesIO:
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
