#!/usr/bin/env bash
# Safe recursive decompression script - one file at a time
# Each archive is extracted into its own subfolder
# Supports Linux, macOS, and Windows (Git Bash / WSL / MSYS2 / Cygwin)

set -euo pipefail

DELETE_AFTER=false

TOTAL=0
SUCCESS=0
SKIPPED=0
FAILED=0

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
    case $1 in
        --delete) DELETE_AFTER=true; shift ;;
        --keep)   DELETE_AFTER=false; shift ;;
        -h|--help)
            echo "Usage: $0 [folder] [--delete|--keep]"
            echo "  folder   : Folder to scan (default: current directory)"
            echo "  --delete : Delete compressed files after extraction"
            echo "  --keep   : Keep compressed files (default)"
            exit 0
            ;;
        *)
            FOLDER=$1; shift ;;
    esac
done

FOLDER=${FOLDER:-.}

# --- Detect OS and package manager ---
detect_pkg_manager() {
    local OS
    OS=$(uname -s 2>/dev/null || echo "Windows")

    case "$OS" in
        Linux)
            if command -v apt-get &>/dev/null; then
                echo "apt-get"
            elif command -v yum &>/dev/null; then
                echo "yum"
            elif command -v dnf &>/dev/null; then
                echo "dnf"
            elif command -v pacman &>/dev/null; then
                echo "pacman"
            else
                echo "unknown"
            fi
            ;;
        Darwin)
            if command -v brew &>/dev/null; then
                echo "brew"
            else
                echo "unknown"
            fi
            ;;
        CYGWIN*|MINGW*|MSYS*|Windows_NT)
            if command -v choco &>/dev/null; then
                echo "choco"
            elif command -v winget &>/dev/null; then
                echo "winget"
            else
                echo "unknown"
            fi
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

PKG_MANAGER=$(detect_pkg_manager)

# --- Install missing tools ---
install_tool() {
    local tool=$1
    echo "Installing missing tool: $tool"

    case $PKG_MANAGER in
        apt-get) sudo apt-get update && sudo apt-get install -y "$tool" ;;
        yum)     sudo yum install -y "$tool" ;;
        dnf)     sudo dnf install -y "$tool" ;;
        pacman)  sudo pacman -Sy --noconfirm "$tool" ;;
        brew)    brew install "$tool" ;;
        choco)   choco install -y "$tool" ;;
        winget)  winget install --id "$tool" -e --accept-package-agreements --accept-source-agreements ;;
        *)
            echo "❌ Could not detect package manager. Please install $tool manually."
            exit 1
            ;;
    esac
}

ensure_tool() {
    local tool=$1
    if ! command -v "$tool" &>/dev/null; then
        install_tool "$tool"
    fi
}

# --- Decompress single file into its own folder ---
decompress_file() {
    local file=$1
    TOTAL=$((TOTAL + 1))

    local dir
    dir=$(dirname "$file")
    local base
    base=$(basename "$file")
    local name="${base%.*}"  # Remove extension for folder name

    # Handle double extensions like .tar.gz
    case "$file" in
        *.tar.gz|*.tar.bz2|*.tar.xz) name="${base%.*.*}" ;; 
    esac

    local out_dir="$dir/$name"
    mkdir -p "$out_dir"

    echo "📂 Processing: $file -> $out_dir"

    if ! output=$( { 
        case "$file" in
            *.tar.gz|*.tgz)    ensure_tool tar; tar -xzf "$file" -C "$out_dir" ;;
            *.tar.bz2|*.tbz2)  ensure_tool tar; tar -xjf "$file" -C "$out_dir" ;;
            *.tar.xz)          ensure_tool tar; ensure_tool xz; tar -xJf "$file" -C "$out_dir" ;;
            *.zip)             ensure_tool unzip; unzip -o "$file" -d "$out_dir" ;;
            *.rar)             ensure_tool unrar; unrar x -o+ "$file" "$out_dir" ;;
            *.7z)              ensure_tool 7z; 7z x "$file" -o"$out_dir" ;;
            *.gz)              ensure_tool gunzip; gunzip -c "$file" > "$out_dir/${base%.gz}" ;;
            *.bz2)             ensure_tool bunzip2; bunzip2 -c "$file" > "$out_dir/${base%.bz2}" ;;
            *.xz)              ensure_tool xz; xz -dc "$file" > "$out_dir/${base%.xz}" ;;
            *) echo "SKIP";;
        esac
    } 2>&1 ); then
        if [[ "$output" == "SKIP" ]]; then
            echo -e "${YELLOW}⚠️ Unknown format: $file (skipped)${NC}"
            SKIPPED=$((SKIPPED + 1))
        else
            echo -e "${RED}❌ Failed: $file${NC}"
            echo "$output"
            FAILED=$((FAILED + 1))
        fi
        return
    fi

    if $DELETE_AFTER; then
        echo "🗑 Deleting original: $file"
        rm -f "$file"
    fi

    echo -e "${GREEN}✅ Done: $file${NC}"
    SUCCESS=$((SUCCESS + 1))
}

# --- Main loop (recursive) ---
main() {
    while IFS= read -r -d '' file; do
        decompress_file "$file"
    done < <(find "$FOLDER" -type f -print0)

    # --- Summary ---
    echo
    echo "📊 Decompression Summary"
    echo "------------------------"
    echo -e "Total archives found  : ${TOTAL}"
    echo -e "Successfully extracted: ${GREEN}${SUCCESS}${NC}"
    echo -e "Skipped (unknown)    : ${YELLOW}${SKIPPED}${NC}"
    echo -e "Failed               : ${RED}${FAILED}${NC}"
    echo "------------------------"
}

main
