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
        except:
            pass
    return {
        "font_name": "Arial",
        "font_size": 38,
        "line_numbers": False,
        "style": "monokai",
        "image_pad": 20
    }

def main():
    parser = argparse.ArgumentParser(description="Code to PNG and/or Analyzer")
    parser.add_argument("path", nargs="?", default="", help="Folder or file path (relative to codefiles/)")
    parser.add_argument("--analyze", action="store_true", help="Analyze performance (compile, time, memory)")
    parser.add_argument("--latex", action="store_true", help="Compile all LaTeX files in latexinput/")
    args = parser.parse_args()

    app = CodeToPNGConverter()
    rel_path = args.path
    input_path = os.path.join(app.INPUT_FOLDER, rel_path or "")

    if args.analyze:
        print(f"🔬 Analyzing code in: {input_path}")
        analyze_folder(input_path)
        return
    
    if args.latex:
        print("🧪 Compiling LaTeX files...")
        compile_latex_files()
        return

    app = CodeToPNGConverter()
    args = sys.argv[1:]

    if not args:
        input_path = app.INPUT_FOLDER
        all_mode = True
    else:
        rel_path = args[0]
        input_path = os.path.join(app.INPUT_FOLDER, rel_path)
        all_mode = os.path.isdir(input_path)

    if not os.path.exists(input_path):
        print(f"❌ Path '{input_path}' not found.")
        return

    settings = load_settings()

    if all_mode:
        files = app.list_code_files(input_path)
        count = 0
        for f in files:
            file_path = os.path.join(input_path, f)
            output_path = os.path.join(app.OUTPUT_FOLDER, os.path.splitext(f)[0] + ".png")
            with open(file_path, 'r', encoding='utf-8') as file:
                code = file.read()
            app.code_to_png(code, file_path, output_path, **settings)
            print(f"✅ Generated: {output_path}")
            count += 1
        print(f"\n🎉 {count} PNGs saved to '{app.OUTPUT_FOLDER}'")
    else:
        if not os.path.isfile(input_path):
            print("❌ Invalid file path.")
            return
        with open(input_path, 'r', encoding='utf-8') as f:
            code = f.read()
        output_file = os.path.splitext(os.path.basename(input_path))[0] + ".png"
        output_path = os.path.join(app.OUTPUT_FOLDER, output_file)
        app.code_to_png(code, input_path, output_path, **settings)
        print(f"✅ PNG saved: {output_path}")

if __name__ == "__main__":
    main()
