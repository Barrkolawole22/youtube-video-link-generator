#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install system dependencies
apt-get update
apt-get install -y --no-install-recommends \
  build-essential \
  gcc \
  python3-dev \
  libjpeg-dev \
  zlib1g-dev

# 2. Install your Python dependencies
pip install -r requirements.txt