# Import necessary modules
import subprocess  # Used to run external commands (ffmpeg and ffprobe)
import sys         # Used to read command-line arguments
import os          # Used to check file existence

# Define a class to handle video compression
class VideoCompressor:
    def __init__(self, input_path, output_path, target_size_mb=950):
        # Initialize the compressor with input/output paths and optional target size
        self.input_path = input_path
        self.output_path = output_path
        self.target_size_mb = target_size_mb  # Desired file size in megabytes

    # Get the duration of the video using ffprobe
    def get_duration(self):
        result = subprocess.run([
            'ffprobe', '-v', 'error',  # Suppress extra output
            '-show_entries', 'format=duration',  # Request duration info
            '-of', 'default=noprint_wrappers=1:nokey=1',  # Simplify output format
            self.input_path
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        # Convert result to float (seconds) and return
        return float(result.stdout)

    # Perform the compression using ffmpeg
    def compress(self):
        duration = self.get_duration()  # Get video duration in seconds

        # Calculate target bitrate in bits per second
        target_bitrate = (self.target_size_mb * 1024 * 1024 * 8) / duration
        
        # Convert target bitrate to kilobits per second
        video_bitrate_kbps = int(target_bitrate / 1000)

        # Run ffmpeg to compress the video with calculated bitrate
        subprocess.run([
            'ffmpeg', '-i', self.input_path,  # Input file
            '-b:v', f'{video_bitrate_kbps}k',  # Set video bitrate
            '-bufsize', f'{video_bitrate_kbps}k',  # Set buffer size
            '-maxrate', f'{video_bitrate_kbps}k',  # Set max bitrate
            '-preset', 'slow',  # Use slow preset for better compression
            '-c:a', 'aac', '-b:a', '128k',  # Use AAC audio codec with 128k bitrate
            self.output_path  # Output file
        ])

# Entry point of the script
def main():
    # Check if there are enough command-line arguments
    if len(sys.argv) < 3:
        print("Usage: python compress.py input.mp4 output.mp4 [target_size_mb]")
        return

    # Get input and output paths from arguments
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # Get target size from arguments if provided, else use default (950MB)
    target_size_mb = int(sys.argv[3]) if len(sys.argv) > 3 else 950

    # Check if input file exists
    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        return

    # Create a VideoCompressor instance and compress the video
    compressor = VideoCompressor(input_path, output_path, target_size_mb)
    compressor.compress()

    # Notify user that compression is complete
    print(f"Compression complete: {output_path}")

# Run main function if the script is executed directly
if __name__ == "__main__":
    main()
