# cli.py

import os
import sys
import json
import argparse
from converter import CodeToPNGConverter
from analyzer import analyze_folder
from latexcompiler import compile_latex_files

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load settings, using defaults. Reason: {e}")
    return {
        "font_name": "Arial",
        "font_size": 38,
        "line_numbers": False,
        "style": "monokai",
        "image_pad": 20,
        "border": False,
        "dpi": 300,
        "lang": None
    }

def apply_overrides(settings, args):
    if args.border:
        settings["border"] = True
    if args.dpi is not None:
        settings["dpi"] = args.dpi
    if args.lang:
        settings["lang"] = args.lang
    return settings

def main():
    parser = argparse.ArgumentParser(description="📦 Code Tool CLI")
    parser.add_argument("path", nargs="?", default="", help="Relative path inside codefiles/")
    parser.add_argument("--analyze", action="store_true", help="Analyze code performance")
    parser.add_argument("--latex", action="store_true", help="Compile LaTeX files from latexinput/")
    parser.add_argument("--border", action="store_true", help="Add a border to the PNG image")
    parser.add_argument("--dpi", type=int, help="Set DPI (resolution) for PNG output")
    parser.add_argument("--lang", type=str, help="Manually set language for syntax highlighting")
    args = parser.parse_args()

    app = CodeToPNGConverter()
    rel_path = args.path
    input_path = os.path.join(app.INPUT_FOLDER, rel_path or "")

    if args.analyze:
        print(f"🔬 Analyzing code in: {input_path}")
        analyze_folder(input_path)
        return
    
    if args.latex:
        print("📄 Compiling LaTeX files...")
        compile_latex_files()
        return

    if not os.path.exists(input_path):
        print(f"❌ Path '{input_path}' not found.")
        return

    settings = load_settings()
    settings = apply_overrides(settings, args)

    def convert_and_save(file_path, output_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
        app.code_to_png(code, file_path, output_path, **settings)

    if os.path.isdir(input_path):
        files = app.list_code_files(input_path)
        count = 0
        for f in files:
            file_path = os.path.join(input_path, f)
            output_file = os.path.splitext(f)[0] + ".png"
            output_path = os.path.join(app.OUTPUT_FOLDER, output_file)
            convert_and_save(file_path, output_path)
            print(f"✅ Generated: {output_path}")
            count += 1
        print(f"\n🎉 {count} PNGs saved to '{app.OUTPUT_FOLDER}'")
    else:
        if not os.path.isfile(input_path):
            print("❌ Invalid file path.")
            return
        output_file = os.path.splitext(os.path.basename(input_path))[0] + ".png"
        output_path = os.path.join(app.OUTPUT_FOLDER, output_file)
        convert_and_save(input_path, output_path)
        print(f"✅ PNG saved: {output_path}")

if __name__ == "__main__":
    main()
