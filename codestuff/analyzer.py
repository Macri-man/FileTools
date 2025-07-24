import os
import time
import subprocess
import resource
import argparse
import json
import logging
from collections import defaultdict
from multiprocessing import Pool, cpu_count
from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import ImageFormatter

SUPPORTED_EXTS = (".cpp", ".c", ".go", ".rs", ".py", ".java", ".hs")

# --- PNG Config Loader ---
def load_png_config(config_path="png_config.json"):
    default_config = {
        "style": "monokai",
        "font_name": "DejaVu Sans Mono",
        "line_numbers": True
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
            default_config.update(user_config)
        except Exception as e:
            logging.warning(f"Failed to load PNG config: {e}")
    return default_config

# --- Compilation Logic ---
def compile_and_get_binary(file_path, ext):
    base = os.path.splitext(file_path)[0]
    filename = os.path.basename(file_path)

    if ext == ".cpp":
        output = base + ".out"
        cmd = ["g++", file_path, "-o", output]
    elif ext == ".c":
        output = base + ".out"
        cmd = ["gcc", file_path, "-o", output]
    elif ext == ".go":
        output = base + ".out"
        cmd = ["go", "build", "-o", output, file_path]
    elif ext == ".rs":
        output = base + ".out"
        cmd = ["rustc", file_path, "-o", output]
    elif ext == ".java":
        class_name = os.path.splitext(filename)[0]
        cmd = ["javac", file_path]
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return class_name, None
        except subprocess.CalledProcessError as e:
            return None, e.stderr.decode()
    elif ext == ".py":
        return "python3", None
    elif ext == ".hs":
        output = base + ".out"
        cmd = ["ghc", "-o", output, file_path]
    else:
        return None, f"Unsupported file extension: {ext}"

    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return output, None
    except subprocess.CalledProcessError as e:
        return None, e.stderr.decode()

# --- Runtime Logic ---
def run_and_measure(command, stdout_path=None, stderr_path=None):
    start = time.time()
    usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)

    try:
        with open(stdout_path or os.devnull, "w") as out, open(stderr_path or os.devnull, "w") as err:
            subprocess.run(command, stdout=out, stderr=err, check=True)
    except subprocess.CalledProcessError:
        return None, None, "Runtime Error"

    end = time.time()
    usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)

    elapsed = end - start
    memory = usage_end.ru_maxrss - usage_start.ru_maxrss
    return elapsed, memory, None

# --- Code to PNG ---
def convert_code_to_png(file_path, out_folder="pngs", config=None):
    try:
        with open(file_path, "r") as f:
            code = f.read()
        lexer = get_lexer_for_filename(file_path)
        cfg = config or load_png_config()
        formatter = ImageFormatter(
            line_numbers=cfg.get("line_numbers", True),
            font_name=cfg.get("font_name", "DejaVu Sans Mono"),
            style=cfg.get("style", "monokai")
        )
        os.makedirs(out_folder, exist_ok=True)
        out_path = os.path.join(out_folder, os.path.basename(file_path) + ".png")
        with open(out_path, "wb") as img_file:
            img_file.write(highlight(code, lexer, formatter))
    except Exception as e:
        logging.warning(f"Failed to convert {file_path} to PNG: {e}")

# --- File Processor ---
def process_file(args):
    file_path, single_result_dir, png_dir, verbose, force, png_cfg = args
    ext = os.path.splitext(file_path)[1].lower()
    filename = os.path.basename(file_path)

    result_path = os.path.join(single_result_dir, filename + ".txt")
    if not force and os.path.exists(result_path):
        return (filename, "Skipped", "", "", ""), ext[1:]

    convert_code_to_png(file_path, png_dir, png_cfg)
    binary, compile_err = compile_and_get_binary(file_path, ext)

    if compile_err:
        result = (filename, "Compile Error", "", "", compile_err.strip())
    else:
        command = ([binary, file_path] if ext == ".py" else
                   ["java", binary] if ext == ".java" else
                   [binary])

        stdout_path = os.path.join(single_result_dir, filename + ".stdout")
        stderr_path = os.path.join(single_result_dir, filename + ".stderr")
        time_taken, mem_used, runtime_err = run_and_measure(command, stdout_path, stderr_path)

        if runtime_err:
            result = (filename, "Runtime Error", "", "", runtime_err)
        else:
            result = (filename, "Ran", f"{time_taken:.4f}", f"{mem_used}", "")

    os.makedirs(single_result_dir, exist_ok=True)
    with open(result_path, "w") as f:
        f.write(f"Status: {result[1]}\nTime: {result[2]}\nMemory: {result[3]}\nError: {result[4]}\n")

    return result, ext[1:]

# --- Analyzer Core ---
def analyze_folder(folder_path, result_file_path, per_file_results_dir, png_dir, verbose=False, force=False, json_summary=False):
    png_cfg = load_png_config()
    lang_stats = defaultdict(lambda: {
        "total": 0, "success": 0, "compile_fail": 0, "runtime_error": 0,
        "total_time": 0.0, "total_mem": 0, "filenames": []
    })

    file_args = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_EXTS:
                full_path = os.path.join(root, file)
                file_args.append((full_path, per_file_results_dir, png_dir, verbose, force, png_cfg))

    with Pool(cpu_count()) as pool:
        results = pool.map(process_file, file_args)

    with open(result_file_path, "w") as result_file:
        result_file.write("File, Status, Time (s), Memory (KB), Error\n")

        for (filename, status, time_taken, mem_used, error), lang in results:
            lang_stats[lang]["total"] += 1
            lang_stats[lang]["filenames"].append(filename)

            if status == "Compile Error":
                lang_stats[lang]["compile_fail"] += 1
                logging.warning(f"Compile failed: {filename}")
            elif status == "Runtime Error":
                lang_stats[lang]["runtime_error"] += 1
                logging.warning(f"Runtime error: {filename}")
            elif status == "Ran":
                lang_stats[lang]["success"] += 1
                lang_stats[lang]["total_time"] += float(time_taken)
                lang_stats[lang]["total_mem"] += int(mem_used)
                logging.info(f"Ran {filename}: {time_taken}s, {mem_used} KB")

            result_file.write(f"{filename}, {status}, {time_taken}, {mem_used}, {error}\n")

        result_file.write("\nSummary by Language:\n")
        result_file.write("Language, Files, Ran, Compile Fails, Runtime Errors, Avg Time (s), Avg Mem (KB), Files\n")

        for lang, data in lang_stats.items():
            files = data["total"]
            ran = data["success"]
            compile_fail = data["compile_fail"]
            runtime_error = data["runtime_error"]
            avg_time = data["total_time"] / ran if ran > 0 else 0
            avg_mem = data["total_mem"] / ran if ran > 0 else 0
            file_list = "; ".join(data["filenames"])
            result_file.write(f"{lang}, {files}, {ran}, {compile_fail}, {runtime_error}, {avg_time:.4f}, {avg_mem:.0f}, {file_list}\n")

    if json_summary:
        with open(result_file_path.replace(".txt", ".json"), "w") as jf:
            json.dump(lang_stats, jf, indent=2)

# --- CLI ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze source code in a folder.")
    parser.add_argument("folder", help="Path to folder containing source files")
    parser.add_argument("--results", default="results.txt", help="Main results file")
    parser.add_argument("--per-file", default="results", help="Directory for per-file results")
    parser.add_argument("--png-dir", default="pngs", help="Directory to save PNGs")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--force", action="store_true", help="Reprocess even if result exists")
    parser.add_argument("--json", action="store_true", help="Output JSON summary alongside results.txt")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    analyze_folder(args.folder, args.results, args.per_file, args.png_dir,
                   verbose=args.verbose, force=args.force, json_summary=args.json)
