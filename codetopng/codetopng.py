import os
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.formatters import ImageFormatter

def code_file_to_png(input_path, output_path, font_name='DejaVu Sans Mono', font_size=18,
                     line_numbers=True, style='monokai', image_pad=10):
    # Read code from file
    with open(input_path, 'r', encoding='utf-8') as f:
        code = f.read()

    try:
        # Try to get lexer based on filename
        lexer = get_lexer_for_filename(input_path)
    except Exception:
        # If fails, guess lexer from code content
        lexer = guess_lexer(code)

    formatter = ImageFormatter(
        font_name=font_name,
        font_size=font_size,
        line_numbers=line_numbers,
        style=style,
        image_pad=image_pad
    )

    # Create output directory if doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'wb') as f:
        f.write(highlight(code, lexer, formatter))

    print(f"Saved image: {output_path}")

def batch_convert_code_folder(input_folder, output_folder,
                              font_name='DejaVu Sans Mono', font_size=18,
                              line_numbers=True, style='monokai', image_pad=10):
    # Loop through all files in input_folder (non-recursive)
    for filename in os.listdir(input_folder):
        full_input_path = os.path.join(input_folder, filename)

        # Skip if not a file
        if not os.path.isfile(full_input_path):
            continue

        # Create PNG filename with same base name
        base_name, _ = os.path.splitext(filename)
        output_file = base_name + '.png'
        full_output_path = os.path.join(output_folder, output_file)

        # Convert and save PNG
        try:
            code_file_to_png(full_input_path, full_output_path,
                             font_name, font_size, line_numbers, style, image_pad)
        except Exception as e:
            print(f"Failed to convert {filename}: {e}")

if __name__ == '__main__':
    # Customize input/output folders and styling here:
    input_folder = 'code_files'      # Folder with your code files
    output_folder = 'code_images'    # Where PNGs will be saved

    batch_convert_code_folder(input_folder, output_folder)
