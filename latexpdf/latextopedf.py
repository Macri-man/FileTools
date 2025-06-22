import os
import subprocess
from pathlib import Path

# --- Settings ---
input_root = Path("path/to/latex_files")      # CHANGE THIS
output_root = Path("path/to/pdf_files")       # CHANGE THIS
cleanup = True                                # Set to False to keep .aux/.log files

# --- Extensions to remove if cleanup is enabled ---
cleanup_exts = [".aux", ".log", ".out", ".toc", ".synctex.gz"]

# --- Make sure output folder exists ---
output_root.mkdir(parents=True, exist_ok=True)

# --- Find all .tex files in subdirectories ---
tex_files = list(input_root.rglob("*.tex"))

# --- Compile each .tex file ---
for tex_path in tex_files:
    relative_path = tex_path.relative_to(input_root)
    output_subdir = output_root / relative_path.parent
    output_subdir.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", f"-output-directory={output_subdir}", tex_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"✅ Compiled: {relative_path}")

        # --- Optional cleanup ---
        if cleanup:
            base_name = tex_path.stem
            for ext in cleanup_exts:
                aux_file = output_subdir / f"{base_name}{ext}"
                if aux_file.exists():
                    aux_file.unlink()

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {relative_path}")
        print(e.stderr.decode())
