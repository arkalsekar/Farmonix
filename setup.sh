#!/bin/bash

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y python3-pip python3-opencv libatlas-base-dev libjasper-dev libqtgui4 libqt4-test

# Install Python packages
pip3 install tensorflow opencv-python pillow streamlit fastapi uvicorn requests numpy

# Enable camera interface
sudo raspi-config nonint do_camera 0

# Create project directory
mkdir -p ~/cotton_disease_detection
cd ~/cotton_disease_detection

# Download model files (replace with your actual model files)
# wget https://your-domain.com/cotton_disease_model.h5
# wget https://your-domain.com/class_names.json

echo "Setup complete! Please place your model files in ~/cotton_disease_detection/"
echo "Model files needed: cotton_disease_model.h5 and class_names.json"
