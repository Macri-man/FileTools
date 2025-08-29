import os
import shutil
import subprocess
import argparse
import json
from pathlib import Path
from shutil import which
from concurrent.futures import ProcessPoolExecutor, as_completed

# --- Configuration ---
cleanup_exts = [".aux", ".log", ".out", ".toc", ".bbl", ".blg", ".synctex.gz"]

PDFLATEX = which("pdflatex") or "/usr/bin/pdflatex"
BIBTEX = which("bibtex") or "/usr/bin/bibtex"

def uses_bibtex(tex_path: Path) -> bool:
    try:
        content = tex_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = tex_path.read_text(errors="ignore")
    return "\\bibliography" in content or "\\addbibresource" in content

def run_latex_file(tex_path_str, input_root_str, output_root_str, cleanup=True):
    tex_path = Path(tex_path_str)
    input_root = Path(input_root_str)
    output_root = Path(output_root_str)

    relative_path = tex_path.relative_to(input_root)
    tex_dir = tex_path.parent
    basename = tex_path.stem

    result_data = {
        "file": str(relative_path),
        "success": False,
        "pdf_path": None,
        "error": "",
    }

    try:
        def run_latex():
            return subprocess.run(
                [PDFLATEX, "-interaction=nonstopmode", str(tex_path)],
                cwd=tex_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

        result = run_latex()
        if result.returncode != 0:
            result_data["error"] = result.stdout + "\n" + result.stderr
            return result_data

        if uses_bibtex(tex_path):
            bibtex_result = subprocess.run(
                [BIBTEX, basename],
                cwd=tex_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if bibtex_result.returncode != 0:
                result_data["error"] = bibtex_result.stdout + "\n" + bibtex_result.stderr
                return result_data

        for _ in range(2):
            result = run_latex()
            if result.returncode != 0:
                result_data["error"] = result.stdout + "\n" + result.stderr
                return result_data

        pdf_file = tex_dir / f"{basename}.pdf"
        if pdf_file.exists():
            dest_pdf_path = output_root / relative_path.parent / f"{basename}.pdf"
            dest_pdf_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(pdf_file), str(dest_pdf_path))
            result_data["success"] = True
            result_data["pdf_path"] = str(dest_pdf_path)
        else:
            result_data["error"] = "PDF not found after compilation."

    except Exception as e:
        result_data["error"] = str(e)

    if cleanup:
        for ext in cleanup_exts:
            aux_file = tex_dir / f"{basename}{ext}"
            if aux_file.exists():
                aux_file.unlink()

    return result_data

def log_result(result):
    if result["success"]:
        print(f"✅ Compiled: {result['file']}")
    else:
        print(f"❌ Failed: {result['file']}\n   Error: {result['error'][:200].strip()}...")

def save_results(results, output_file="latexoutput/results.json"):
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

def compile_latex_files(input_root="latexinput", output_root="latexoutput", cleanup=True, max_workers=None):
    input_root = Path(os.path.abspath(input_root))
    output_root = Path(os.path.abspath(output_root))
    tex_files = list(input_root.rglob("*.tex"))

    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_tex = {
            executor.submit(run_latex_file, str(tex_path), str(input_root), str(output_root), cleanup): tex_path
            for tex_path in tex_files
        }

        for future in as_completed(future_to_tex):
            result = future.result()
            results.append(result)
            log_result(result)

    return results

def parse_args():
    parser = argparse.ArgumentParser(description="Compile LaTeX files recursively in parallel.")
    parser.add_argument("--input", default="latexinput", help="Input root directory")
    parser.add_argument("--output", default="latexoutput", help="Output root directory")
    parser.add_argument("--no-cleanup", action="store_true", help="Disable cleanup of auxiliary files")
    parser.add_argument("--log", default="results.json", help="Output JSON log filename (within output directory)")
    parser.add_argument("--workers", type=int, default=None, help="Number of parallel workers (default: number of CPUs)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    results = compile_latex_files(
        input_root=args.input,
        output_root=args.output,
        cleanup=not args.no_cleanup,
        max_workers=args.workers
    )
    save_results(results, output_file=os.path.join(args.output, args.log))
