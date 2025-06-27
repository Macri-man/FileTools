import os
import sys
import json
from io import BytesIO
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.formatters import ImageFormatter

SETTINGS_FILE = "settings.json"

class CodeToPNGCLI:
    def __init__(self, input_folder="codefiles", output_folder="codeimages"):
        self.INPUT_FOLDER = input_folder
        self.OUTPUT_FOLDER = output_folder
        os.makedirs(self.INPUT_FOLDER, exist_ok=True)
        os.makedirs(self.OUTPUT_FOLDER, exist_ok=True)

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

    def load_settings(self):
        # Load settings from JSON if file exists
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data
            except Exception as e:
                print(f"⚠️ Warning: Could not load settings from {SETTINGS_FILE}: {e}")
        # Return defaults if no file or error
        return {
            "font_name": "Arial",
            "font_size": 38,
            "line_numbers": False,
            "style": "monokai",
            "image_pad": 20,
        }

    def run(self, input_path: str, all_mode: bool):
        input_path = os.path.join(self.INPUT_FOLDER, input_path)
        if not os.path.exists(input_path):
            print(f"❌ Folder or file '{input_path}' not found.")
            return

        # Load settings from file or use defaults
        settings = self.load_settings()
        font_name = settings.get("font_name", "Arial")
        font_size = settings.get("font_size", 38)
        image_pad = settings.get("image_pad", 20)
        line_numbers = settings.get("line_numbers", False)
        style = settings.get("style", "monokai")

        if all_mode:
            files = self.list_code_files(input_path)
            count = 0
            for f in files:
                file_path = os.path.join(input_path, f)
                output_path = os.path.join(self.OUTPUT_FOLDER, f)
                output_path = os.path.splitext(output_path)[0] + ".png"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                with open(file_path, 'r', encoding='utf-8') as file:
                    code = file.read()
                self.code_to_png(code, file_path, output_path,
                                 font_name, font_size, line_numbers, style, image_pad)
                print(f"✅ Generated: {output_path}")
                count += 1
            print(f"\n🎉 Done! {count} PNGs saved in '{self.OUTPUT_FOLDER}'")
        else:
            if not os.path.isfile(input_path):
                print("❌ Provide a valid file path when not using folder mode")
                return
            with open(input_path, 'r', encoding='utf-8') as f:
                code = f.read()
            output_file = os.path.splitext(os.path.basename(input_path))[0] + ".png"
            output_path = os.path.join(self.OUTPUT_FOLDER, output_file)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            self.code_to_png(code, input_path, output_path,
                             font_name, font_size, line_numbers, style, image_pad)
            print(f"✅ PNG saved: {output_path}")

def main():
    app = CodeToPNGCLI()

    args = sys.argv[1:]
    if not args:
        # No args = generate all PNGs from root input folder
        app.run("", all_mode=True)
    else:
        rel_path = args[0]
        full_path = os.path.join(app.INPUT_FOLDER, rel_path)
        if os.path.isdir(full_path):
            app.run(rel_path, all_mode=True)
        elif os.path.isfile(full_path):
            app.run(rel_path, all_mode=False)
        else:
            print(f"❌ Path '{rel_path}' not found in '{app.INPUT_FOLDER}'")

if __name__ == "__main__":
    main()
