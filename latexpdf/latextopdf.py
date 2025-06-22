import os
import shutil
import subprocess
from pathlib import Path

# --- Configuration ---
input_root = Path(os.path.abspath("latexfiles"))    # Source folder with .tex files
output_root = Path(os.path.abspath("output"))       # Destination folder for PDFs
cleanup = False                                     # Toggle cleanup of aux files

# --- Extensions to clean ---
cleanup_exts = [".aux", ".log", ".out", ".toc", ".bbl", ".blg", ".synctex.gz"]

# --- Check if the .tex file uses BibTeX ---
def uses_bibtex(tex_path: Path) -> bool:
    try:
        content = tex_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = tex_path.read_text(errors="ignore")
    return "\\bibliography" in content or "\\addbibresource" in content

# --- Find all .tex files ---
tex_files = list(input_root.rglob("*.tex"))
print(f"Input folder: {input_root}")
print(f"Output folder: {output_root}")
print(f"Found {len(tex_files)} .tex files")
print("Files:")
print(tex_files)

for tex_path in tex_files:
    relative_path = tex_path.relative_to(input_root)
    tex_dir = tex_path.parent
    basename = tex_path.stem

    print(f"\nCompiling {relative_path} ...")

    try:
        # Run pdflatex first time
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", str(tex_path)],
            cwd=tex_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ Failed to compile (1st run): {relative_path}")
            print("stdout:")
            print(result.stdout)
            print("stderr:")
            print(result.stderr)
            continue

        # Run bibtex if needed
        if uses_bibtex(tex_path):
            result_bib = subprocess.run(
                ["bibtex", basename],
                cwd=tex_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result_bib.returncode != 0:
                print(f"❌ Failed to run bibtex: {relative_path}")
                print("stdout:")
                print(result_bib.stdout)
                print("stderr:")
                print(result_bib.stderr)
                continue

        # Run pdflatex two more times to resolve references
        for i in range(2):
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", str(tex_path)],
                cwd=tex_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                print(f"❌ Failed to compile (run {i+2}): {relative_path}")
                print("stdout:")
                print(result.stdout)
                print("stderr:")
                print(result.stderr)
                break
        else:
            print(f"✅ Successfully compiled: {relative_path}")

            # Move the generated PDF to the output folder preserving structure
            pdf_file = tex_dir / f"{basename}.pdf"
            if pdf_file.exists():
                dest_pdf_path = output_root / relative_path.parent / f"{basename}.pdf"
                dest_pdf_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(pdf_file), str(dest_pdf_path))
                print(f"Moved PDF to: {dest_pdf_path}")
            else:
                print(f"⚠️ PDF not found for {relative_path} after compilation.")

            # Optional cleanup of aux files in the source folder
            if cleanup:
                for ext in cleanup_exts:
                    aux_file = tex_dir / f"{basename}{ext}"
                    if aux_file.exists():
                        aux_file.unlink()

    except Exception as e:
        print(f"❌ Exception while compiling {relative_path}: {e}")
