import os            # To interact with the file system (list files, check paths)
import subprocess    # To run external commands/programs
import sys           # To access command-line arguments and exit program

class EpubToPdfConverter:
    def __init__(self, folder_path):
        # Initialize the converter with the folder containing EPUB files
        self.folder_path = folder_path

    def convert_all(self):
        # List all files in the folder ending with .epub (case-sensitive)
        epub_files = [f for f in os.listdir(self.folder_path) if f.endswith(".epub")]

        # Iterate over each EPUB file found
        for epub in epub_files:
            # Construct full path to the input EPUB file
            epub_path = os.path.join(self.folder_path, epub)
            # Generate the output PDF filename by replacing the .epub extension with .pdf
            pdf_name = os.path.splitext(epub)[0] + ".pdf"
            # Construct full path for the output PDF file
            pdf_path = os.path.join(self.folder_path, pdf_name)

            print(f"Converting: {epub} → {pdf_name}")
            try:
                # Run the external 'ebook-convert' command to convert EPUB to PDF
                # 'check=True' causes subprocess to raise an error if command fails
                subprocess.run([
                    "ebook-convert",  # Calibre's command-line conversion tool
                    epub_path,        # Input EPUB file path
                    pdf_path          # Output PDF file path
                ], check=True)
                print(f"Success: {pdf_name}")
            except subprocess.CalledProcessError as e:
                # If the conversion command fails, catch the error and print failure message
                print(f"Failed: {epub}\n{e}")

def main():
    # Check if the user provided the folder path as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python script.py /path/to/epub/folder")
        sys.exit(1)  # Exit program with error code 1 (indicating incorrect usage)

    folder = sys.argv[1]  # Get folder path from the first argument
    # Verify that the provided path is a directory that exists
    if not os.path.isdir(folder):
        print(f"Error: Folder '{folder}' does not exist.")
        sys.exit(1)  # Exit with error if folder invalid

    # Create an instance of the converter and run the conversion on all EPUB files
    converter = EpubToPdfConverter(folder)
    converter.convert_all()

if __name__ == "__main__":
    # Run the main function only if this script is executed directly (not imported)
    main()
