# analyzer.py

import os
import time
import subprocess
import resource
import argparse
from collections import defaultdict
from multiprocessing import Pool, cpu_count
from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import ImageFormatter

SUPPORTED_EXTS = (".cpp", ".c", ".go", ".rs", ".py", ".java", ".hs")

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

def run_and_measure(command):
    start = time.time()
    usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)

    try:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError:
        return None, None, "Runtime Error"

    end = time.time()
    usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)

    elapsed = end - start
    memory = usage_end.ru_maxrss - usage_start.ru_maxrss

    return elapsed, memory, None

def convert_code_to_png(file_path, out_folder="pngs"):
    try:
        with open(file_path, "r") as f:
            code = f.read()
        lexer = get_lexer_for_filename(file_path)
        formatter = ImageFormatter(line_numbers=True, font_name='DejaVu Sans Mono', style='monokai')

        os.makedirs(out_folder, exist_ok=True)
        out_path = os.path.join(out_folder, os.path.basename(file_path) + ".png")
        with open(out_path, "wb") as img_file:
            img_file.write(highlight(code, lexer, formatter))
    except Exception as e:
        print(f"❌ Failed to convert {file_path} to PNG: {e}")

def process_file(args):
    file_path, single_result_dir, png_dir, verbose = args
    ext = os.path.splitext(file_path)[1].lower()
    filename = os.path.basename(file_path)

    if verbose:
        print(f"Processing {filename}...")

    convert_code_to_png(file_path, png_dir)

    binary, compile_err = compile_and_get_binary(file_path, ext)

    if compile_err:
        result = (filename, "Fail", "", "", f"Compile Error: {compile_err.strip()}")
    else:
        if ext == ".py":
            command = [binary, file_path]
        elif ext == ".java":
            command = ["java", binary]
        else:
            command = [binary]

        time_taken, mem_used, runtime_err = run_and_measure(command)

        if runtime_err:
            result = (filename, "Success", "Runtime Error", "", runtime_err)
        else:
            result = (filename, "Success", f"{time_taken:.4f}", f"{mem_used}", "")

    if single_result_dir:
        os.makedirs(single_result_dir, exist_ok=True)
        result_path = os.path.join(single_result_dir, filename + ".txt")
        with open(result_path, "w") as f:
            f.write(f"Compile: {result[1]}\nTime: {result[2]}\nMemory: {result[3]}\nError: {result[4]}\n")

    return result, ext[1:]

def analyze_folder(folder_path, result_file_path, per_file_results_dir, png_dir, verbose=False):
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
                file_args.append((full_path, per_file_results_dir, png_dir, verbose))

    with Pool(cpu_count()) as pool:
        results = pool.map(process_file, file_args)

    with open(result_file_path, "w") as result_file:
        result_file.write("File, Compile Success, Time (s), Memory (KB), Error\n")

        for (filename, status, time_taken, mem_used, error), lang in results:
            lang_stats[lang]["total"] += 1
            lang_stats[lang]["filenames"].append(filename)

            if status == "Fail":
                lang_stats[lang]["compile_fail"] += 1
                if verbose:
                    print(f"❌ Compile failed for {filename}")
            elif time_taken == "Runtime Error":
                lang_stats[lang]["runtime_error"] += 1
                if verbose:
                    print(f"⚠️ Runtime error in {filename}")
            else:
                lang_stats[lang]["success"] += 1
                lang_stats[lang]["total_time"] += float(time_taken)
                lang_stats[lang]["total_mem"] += int(mem_used)
                if verbose:
                    print(f"✅ Ran {filename}: {time_taken}s, {mem_used} KB")

            result_file.write(f"{filename}, {status}, {time_taken}, {mem_used}, {error}\n")

        result_file.write("\n\nSummary by Language:\n")
        result_file.write("Language, Files, Successes, Compile Fails, Runtime Errors, Avg Time (s), Avg Mem (KB), Files\n")

        for lang, data in lang_stats.items():
            files = data["total"]
            success = data["success"]
            compile_fail = data["compile_fail"]
            runtime_error = data["runtime_error"]
            avg_time = data["total_time"] / success if success > 0 else 0
            avg_mem = data["total_mem"] / success if success > 0 else 0
            file_list = "; ".join(data["filenames"])

            result_file.write(f"{lang}, {files}, {success}, {compile_fail}, {runtime_error}, "
                              f"{avg_time:.4f}, {avg_mem:.0f}, {file_list}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze source code in a folder.")
    parser.add_argument("folder", help="Path to the folder containing source files")
    parser.add_argument("--results", default="results.txt", help="Path to write the main results file")
    parser.add_argument("--per-file", default="results", help="Directory for per-file results")
    parser.add_argument("--png-dir", default="pngs", help="Directory to save code PNGs")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    analyze_folder(args.folder, args.results, args.per_file, args.png_dir, args.verbose)
