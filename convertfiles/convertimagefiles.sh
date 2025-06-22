#!/bin/bash

# Usage: ./convert_images.sh input_folder output_folder target_extension
# Example: ./convert_images.sh ./input ./output jpg

input_folder="$1"
output_folder="$2"
target_ext="$3"

if [ -z "$input_folder" ] || [ -z "$output_folder" ] || [ -z "$target_ext" ]; then
  echo "Usage: $0 input_folder output_folder target_extension"
  exit 1
fi

mkdir -p "$output_folder"

shopt -s nullglob
for input_file in "$input_folder"/*; do
  filename=$(basename -- "$input_file")
  base="${filename%.*}"
  output_file="$output_folder/$base.$target_ext"
  
  echo "Converting $input_file to $output_file"
  magick "$input_file" "$output_file"
  
  if [ $? -ne 0 ]; then
    echo "Failed to convert $input_file"
  fi
done

echo "Conversion complete!"
