#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status.
set -e

echo "Installing dependencies..."
pip install -U pip
pip install -r requirements.txt