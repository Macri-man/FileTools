import os
import shutil
import subprocess
from pathlib import Path

# --- Configuration ---
cleanup_exts = [".aux", ".log", ".out", ".toc", ".bbl", ".blg", ".synctex.gz"]

def uses_bibtex(tex_path: Path) -> bool:
    try:
        content = tex_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = tex_path.read_text(errors="ignore")
    return "\\bibliography" in content or "\\addbibresource" in content

def compile_latex_files(input_root="latexinput", output_root="latexoutput", cleanup=True):
    input_root = Path(os.path.abspath(input_root))
    output_root = Path(os.path.abspath(output_root))
    tex_files = list(input_root.rglob("*.tex"))

    print(f"📁 Input folder: {input_root}")
    print(f"📂 Output folder: {output_root}")
    print(f"🧾 Found {len(tex_files)} .tex files")
    for tex_path in tex_files:
        relative_path = tex_path.relative_to(input_root)
        tex_dir = tex_path.parent
        basename = tex_path.stem

        print(f"\n📄 Compiling {relative_path} ...")

        try:
            def run_latex():
                return subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", str(tex_path)],
                    cwd=tex_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

            result = run_latex()
            if result.returncode != 0:
                print(f"❌ Failed to compile (1st run): {relative_path}")
                continue

            if uses_bibtex(tex_path):
                result_bib = subprocess.run(["bibtex", basename], cwd=tex_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result_bib.returncode != 0:
                    print(f"❌ BibTeX failed: {relative_path}")
                    continue

            for i in range(2):
                result = run_latex()
                if result.returncode != 0:
                    print(f"❌ Failed to compile (run {i+2}): {relative_path}")
                    break
            else:
                print(f"✅ Successfully compiled: {relative_path}")
                pdf_file = tex_dir / f"{basename}.pdf"
                if pdf_file.exists():
                    dest_pdf_path = output_root / relative_path.parent / f"{basename}.pdf"
                    dest_pdf_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(pdf_file), str(dest_pdf_path))
                    print(f"📦 Moved PDF to: {dest_pdf_path}")
                else:
                    print(f"⚠️ PDF not found for {relative_path}")

            if cleanup:
                for ext in cleanup_exts:
                    aux_file = tex_dir / f"{basename}{ext}"
                    if aux_file.exists():
                        aux_file.unlink()

        except Exception as e:
            print(f"❌ Exception while compiling {relative_path}: {e}")
