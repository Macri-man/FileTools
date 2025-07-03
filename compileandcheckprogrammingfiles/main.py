import os
import subprocess
import time
import resource  # Unix only
import sys
from collections import defaultdict
import argparse


RESULT_FILE = "results.txt"

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
    start_time = time.time()
    usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)

    try:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError:
        return None, None, "Runtime Error"

    end_time = time.time()
    usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)

    elapsed_time = end_time - start_time
    memory_used_kb = usage_end.ru_maxrss - usage_start.ru_maxrss

    return elapsed_time, memory_used_kb, None

def process_file(file_path):
    ext = os.path.splitext(file_path)[1]
    filename = os.path.basename(file_path)

    binary, compile_err = compile_and_get_binary(file_path, ext)

    if compile_err:
        return filename, "Fail", "", "", f"Compile Error: {compile_err.strip()}"

    if ext == ".py":
        command = [binary, file_path]
    elif ext == ".java":
        command = ["java", binary]
    else:
        command = [binary]

    time_taken, mem_used, runtime_err = run_and_measure(command)

    if runtime_err:
        return filename, "Success", "Runtime Error", "", runtime_err

    return filename, "Success", f"{time_taken:.4f}", f"{mem_used}", ""

def summarize_language_stats(stats, result_file):
    result_file.write("\n\nSummary by Language:\n")
    result_file.write("Language, Files, Successes, Compile Fails, Runtime Errors, Avg Time (s), Avg Memory (KB), Files Processed\n")

    for lang, data in stats.items():
        files = data["total"]
        success = data["success"]
        compile_fail = data["compile_fail"]
        runtime_error = data["runtime_error"]
        avg_time = data["total_time"] / success if success > 0 else 0
        avg_mem = data["total_mem"] / success if success > 0 else 0
        file_list = "; ".join(data["filenames"])

        result_file.write(f"{lang}, {files}, {success}, {compile_fail}, {runtime_error}, "
                          f"{avg_time:.4f}, {avg_mem:.0f}, {file_list}\n")

def main(folder_path):
    lang_stats = defaultdict(lambda: {
        "total": 0,
        "success": 0,
        "compile_fail": 0,
        "runtime_error": 0,
        "total_time": 0.0,
        "total_mem": 0,
        "filenames": []
    })

    with open(RESULT_FILE, "w") as result_file:
        result_file.write("File, Compile Success, Time (s), Memory (KB), Error\n")

        for root, _, files in os.walk(folder_path):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in (".cpp", ".c", ".go", ".rs", ".py", ".java", ".hs"):
                    full_path = os.path.join(root, file)
                    print(f"Processing {file}...")

                    lang = ext[1:]  # e.g. ".cpp" -> "cpp"
                    lang_stats[lang]["total"] += 1
                    lang_stats[lang]["filenames"].append(file)

                    filename, status, time_taken, memory_used, error = process_file(full_path)

                    if status == "Fail":
                        lang_stats[lang]["compile_fail"] += 1
                    elif time_taken == "Runtime Error":
                        lang_stats[lang]["runtime_error"] += 1
                    else:
                        lang_stats[lang]["success"] += 1
                        lang_stats[lang]["total_time"] += float(time_taken)
                        lang_stats[lang]["total_mem"] += int(memory_used)

                    result_file.write(f"{filename}, {status}, {time_taken}, {memory_used}, {error}\n")

                    if status == "Fail":
                        print(f"❌ Compile failed for {filename}")
                    elif time_taken == "Runtime Error":
                        print(f"⚠️ Runtime error in {filename}")
                    else:
                        print(f"✅ Ran {filename}: {time_taken}s, {memory_used} KB")

        summarize_language_stats(lang_stats, result_file)

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        print("⚠️ Warning: Accurate memory measurement is only supported on Unix-like systems.")

    parser = argparse.ArgumentParser(description="Compile and run multiple language files, measuring time and memory.")
    parser.add_argument(
        "folder",
        nargs="?",
        default="inputs",
        help=f"Path to folder containing source files (default: '{"inputs"}')"
    )
    args = parser.parse_args()

    folder = os.path.abspath(args.folder)
    print(f"Using source folder: {folder}")

    if not os.path.exists(folder):
        print(f"📁 Folder '{folder}' not found. Creating it...")
        os.makedirs(folder, exist_ok=True)

    main(folder)