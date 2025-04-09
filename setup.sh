#!/bin/bash

# Exit immediately if a command fails
set -e

# Define variables
PYTHON_VERSION="3.11"  # Specify the exact Python 3.9 version
VENV_DIR=".venv"
REQUIREMENTS="requirements.txt"
DOWNLOAD_URL="https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt"
TARGET_DIR="services/rvc/models/predictors"
FILE_NAME="rmvpe.pt"


INPUT_DIR="input"
JOBS_DIR="jobs"
RVC_MODELS_DIR="rvc_models"
SAMPLE_AUDIO="sample_audio"
COQUI_SAMPLES="coqui_samples"

CONFIGS_FILE="configs.json"
JOBS_FILE="jobs.json"

# Create directories if they don't exist
for dir in "$INPUT_DIR" "$JOBS_DIR" "$RVC_MODELS_DIR" "$SAMPLE_AUDIO" "$COQUI_SAMPLES"; do
    if [ ! -d "$dir" ]; then
        echo "Creating directory: $dir"
        mkdir -p "$dir"
    else
        echo "Directory already exists: $dir"
    fi
done

# Create empty JSON files if they don't exist
for file in "$CONFIGS_FILE" "$JOBS_FILE"; do
    if [ ! -f "$file" ]; then
        echo "Creating file: $file"
        echo "{}" > "$file"
    else
        echo "File already exists: $file"
    fi
done

echo "Checking for pyenv..."

# Install pyenv if it's not installed
if ! command -v pyenv &>/dev/null; then
    echo "pyenv not found! Please install pyenv first."
    exit 1
fi

# Install Python 3.9 using pyenv if not installed
if ! pyenv versions | grep -q "$PYTHON_VERSION"; then
    echo "Installing Python $PYTHON_VERSION via pyenv..."
    pyenv install "$PYTHON_VERSION"
fi

# Set local Python version for this project
pyenv local "$PYTHON_VERSION"

echo "Setting up virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    python3.11 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r "$REQUIREMENTS"
pip install TTS
# Ensure the target directory exists
mkdir -p "$TARGET_DIR"

# Download the rmvpe.pt file if it's not already in place
if [ ! -f "$TARGET_DIR/$FILE_NAME" ]; then
    echo "Downloading rmvpe.pt..."
    curl -L "$DOWNLOAD_URL" -o "$TARGET_DIR/$FILE_NAME"
else
    echo "rmvpe.pt already exists in the target directory."
fi

echo "Setup complete!"
