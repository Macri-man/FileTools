# analyzer.py

import os
import time
import subprocess
import resource  # Unix only
from collections import defaultdict

RESULT_FILE = "results.txt"
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

def analyze_folder(folder_path):
    lang_stats = defaultdict(lambda: {
        "total": 0, "success": 0, "compile_fail": 0, "runtime_error": 0,
        "total_time": 0.0, "total_mem": 0, "filenames": []
    })

    os.makedirs(folder_path, exist_ok=True)

    with open(RESULT_FILE, "w") as result_file:
        result_file.write("File, Compile Success, Time (s), Memory (KB), Error\n")

        for root, _, files in os.walk(folder_path):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in SUPPORTED_EXTS:
                    full_path = os.path.join(root, file)
                    lang = ext[1:]

                    lang_stats[lang]["total"] += 1
                    lang_stats[lang]["filenames"].append(file)

                    print(f"Processing {file}...")

                    filename, status, time_taken, mem_used, error = process_file(full_path)

                    if status == "Fail":
                        lang_stats[lang]["compile_fail"] += 1
                    elif time_taken == "Runtime Error":
                        lang_stats[lang]["runtime_error"] += 1
                    else:
                        lang_stats[lang]["success"] += 1
                        lang_stats[lang]["total_time"] += float(time_taken)
                        lang_stats[lang]["total_mem"] += int(mem_used)

                    result_file.write(f"{filename}, {status}, {time_taken}, {mem_used}, {error}\n")

                    if status == "Fail":
                        print(f"❌ Compile failed for {filename}")
                    elif time_taken == "Runtime Error":
                        print(f"⚠️ Runtime error in {filename}")
                    else:
                        print(f"✅ Ran {filename}: {time_taken}s, {mem_used} KB")

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
