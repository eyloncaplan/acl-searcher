#!/bin/bash

set -e

# Constants
FILE_ID="1gTJlj4knfkxdTMgxZP4OGpK4yiCxeqSd"
OUTPUT_DIR="data"
OUTPUT_ZIP="$OUTPUT_DIR/data.zip"

# Create data directory if it doesn't exist
mkdir -p $OUTPUT_DIR

# Download
echo "Downloading dataset to $OUTPUT_ZIP..."
gdown $FILE_ID -O $OUTPUT_ZIP

# Unzip
echo "Unzipping into $OUTPUT_DIR..."
unzip -o $OUTPUT_ZIP -d $OUTPUT_DIR

# Clean up
rm $OUTPUT_ZIP

echo "✅ Done! Files are in $OUTPUT_DIR/"

