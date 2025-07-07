# file: math2eng_cli.py
import argparse
from mathtoeng import translate_latex_to_english

def main():
    parser = argparse.ArgumentParser(description="Convert LaTeX math to English using SymPy")
    parser.add_argument("latex", type=str, help="LaTeX math expression (e.g. '\\sum_{i=1}^n i^2')")
    args = parser.parse_args()

    result = translate_latex_to_english(args.latex)
    print("English:", result)

if __name__ == "__main__":
    main()
