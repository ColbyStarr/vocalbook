#!/bin/bash

# Exit immediately if a command fails
set -e

# Define variables
VENV_DIR=".venv"
TARGET_DIR="services/rvc/models/predictors"
FILE_NAME="rmvpe.pt"

INPUT_DIR="input"
JOBS_DIR="jobs"
RVC_MODELS_DIR="rvc_models"
SAMPLE_AUDIO="sample_audio"
COQUI_SAMPLES="coqui_samples"

CONFIGS_FILE="configs.json"
JOBS_FILE="jobs.json"

echo "Cleaning up VocalBook project..."

# Remove virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "Removing virtual environment: $VENV_DIR"
    rm -rf "$VENV_DIR"
else
    echo "No virtual environment found at $VENV_DIR"
fi

# Remove created directories
for dir in "$INPUT_DIR" "$JOBS_DIR" "$RVC_MODELS_DIR" "$SAMPLE_AUDIO" "$COQUI_SAMPLES"; do
    if [ -d "$dir" ]; then
        echo "Removing directory: $dir"
        rm -rf "$dir"
    else
        echo "Directory not found: $dir"
    fi
done

# Remove JSON files
for file in "$CONFIGS_FILE" "$JOBS_FILE"; do
    if [ -f "$file" ]; then
        echo "Removing file: $file"
        rm "$file"
    else
        echo "File not found: $file"
    fi
done

# Remove rmvpe.pt if it exists
if [ -f "$TARGET_DIR/$FILE_NAME" ]; then
    echo "Removing file: $TARGET_DIR/$FILE_NAME"
    rm "$TARGET_DIR/$FILE_NAME"
else
    echo "rmvpe.pt not found at $TARGET_DIR"
