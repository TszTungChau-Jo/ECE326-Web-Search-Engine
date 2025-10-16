#!/usr/bin/env bash
set -euxo pipefail

# Update and install essentials
sudo apt update -y
sudo apt install -y git python3 python3-venv python3-pip

# Clone your project (skip if already there)
cd /home/ubuntu
if [ ! -d "ECE326-Web-Search-Engine" ]; then
  git clone https://github.com/TszTungChau-Jo/ECE326-Web-Search-Engine.git
  chown -R ubuntu:ubuntu ECE326-Web-Search-Engine # Ensure ubuntu user permissions
fi

# Set up Python virtual environment
cd ECE326-Web-Search-Engine
sudo -u ubuntu python3 -m venv .venv
sudo -u ubuntu /home/ubuntu/ECE326-Web-Search-Engine/.venv/bin/python -m pip install --upgrade pip
sudo -u ubuntu /home/ubuntu/ECE326-Web-Search-Engine/.venv/bin/pip install -r requirements.txt
