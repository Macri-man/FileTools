# app.py

import os
import json
import streamlit as st
from PIL import Image
from converter import CodeToPNGConverter
from analyzer import analyze_folder
from latexcompiler import compile_latex_files
from pathlib import Path

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

def run_ui():
    app = CodeToPNGConverter()

    st.set_page_config(page_title="Code to PNG", layout="wide")
    st.title("🧰 Code Tools Suite")

    tab1, tab2, tab3 = st.tabs(["🖼️ Code to PNG", "📊 Performance Analyzer", "📄 LaTeX Compiler"])

    persistent_settings = load_settings()
    for k, v in persistent_settings.items():
        if k not in st.session_state:
            st.session_state[k] = v


    with tab1:

      subfolders = [""] + app.list_subfolders(app.INPUT_FOLDER)
      selected_subfolder = st.selectbox("📁 Select Folder", subfolders)
      folder_path = os.path.join(app.INPUT_FOLDER, selected_subfolder) if selected_subfolder else app.INPUT_FOLDER

      files = app.list_code_files(folder_path)
      if not files:
          st.warning("No files found.")
          return



      col1, col2 = st.columns([2, 3])

      with col1:
          selected_file = st.selectbox("📄 Select a File", files)
          file_path = os.path.join(folder_path, selected_file)
          with open(file_path, 'r', encoding='utf-8') as f:
              code = f.read()

          code = st.text_area("✏️ Edit Code", value=code, height=300)

          font_name = st.selectbox("Font", ["Arial", "Courier New", "DejaVu Sans Mono"], key="font_name")
          font_size = st.slider("Font Size", 10, 100, key="font_size")
          image_pad = st.slider("Padding", 0, 100, key="image_pad")
          line_numbers = st.checkbox("Show Line Numbers", key="line_numbers")
          style = st.selectbox("Style", ["monokai", "default", "friendly", "native", "trac"], key="style")

          save_settings({
              "font_name": st.session_state.font_name,
              "font_size": st.session_state.font_size,
              "image_pad": st.session_state.image_pad,
              "line_numbers": st.session_state.line_numbers,
              "style": st.session_state.style
          })

          generate_all = st.button("📦 Generate All PNGs")

      with col2:
          st.subheader("🖼️ Preview")
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
              st.error(f"Error rendering image: {e}")

      if generate_all:
          st.subheader("📊 Generating PNGs...")
          count = 0
          for f in files:
              full_path = os.path.join(folder_path, f)
              output_path = os.path.join(app.OUTPUT_FOLDER, os.path.splitext(f)[0] + ".png")
              try:
                  with open(full_path, 'r', encoding='utf-8') as file:
                      content = file.read()
                  app.code_to_png(content, full_path, output_path,
                                  st.session_state.font_name,
                                  st.session_state.font_size,
                                  st.session_state.line_numbers,
                                  st.session_state.style,
                                  st.session_state.image_pad)
                  st.image(output_path, caption=f)
                  count += 1
              except Exception as e:
                  st.error(f"❌ Failed for {f}: {e}")
          st.success(f"✅ {count} images generated!")

    with tab2:
      st.subheader("📊 Performance Analyzer")
      st.markdown("Compile and measure time + memory for source files.")

      folders = [""] + app.list_subfolders(app.INPUT_FOLDER)
      selected_perf_folder = st.selectbox("📁 Select folder to analyze", folders, key="analyze_folder")
      folder_path = os.path.join(app.INPUT_FOLDER, selected_perf_folder) if selected_perf_folder else app.INPUT_FOLDER

      if st.button("▶️ Run Analyzer"):
          with st.spinner("Running performance analyzer..."):
              try:
                  analyze_folder(folder_path)
                  with open("results.txt", "r", encoding="utf-8") as f:
                      content = f.read()
                  st.success("✅ Analysis Complete")
                  st.download_button("📥 Download results.txt", data=content, file_name="results.txt")
                  st.text_area("📄 Results", content, height=400)
              except Exception as e:
                  st.error(f"❌ Failed to analyze: {e}")

    with tab3:
        st.subheader("📄 LaTeX Compiler")
        st.markdown("Compile `.tex` files to PDF using `pdflatex` and `bibtex`.")

        latex_input_dir = "latexinput"
        latex_output_dir = "latexoutput"
        input_folders = [""] + app.list_subfolders(latex_input_dir)
        selected_latex_subfolder = st.selectbox("📁 Select subfolder", input_folders, key="latex_folder")

        full_latex_path = os.path.join(latex_input_dir, selected_latex_subfolder) if selected_latex_subfolder else latex_input_dir
        tex_files = list(Path(full_latex_path).rglob("*.tex"))

        if not tex_files:
            st.warning("No `.tex` files found.")
        else:
            st.info(f"📄 Found {len(tex_files)} `.tex` file(s)")

            if st.button("▶️ Compile All LaTeX Files"):
                with st.spinner("Compiling..."):
                    try:
                        compile_latex_files(latex_input_dir, latex_output_dir)
                        st.success("✅ LaTeX compilation complete!")
                    except Exception as e:
                        st.error(f"❌ Compilation failed: {e}")

            pdf_files = list(Path(latex_output_dir).rglob("*.pdf"))
            if pdf_files:
                st.subheader("📥 Download PDFs")
                for pdf in pdf_files:
                    st.markdown(f"**{pdf.name}**")
                    with open(pdf, "rb") as f:
                        st.download_button("Download PDF", f.read(), file_name=pdf.name)

if __name__ == "__main__":
    run_ui()
