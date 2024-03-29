#!/bin/sh
git clone https://github.com/neonbjb/tortoise-tts
cd tortoise-tts
# Install pytorch
# See https://pytorch.org/get-started/locally/
pip install --upgrade --disable-pip-version-check --no-input torch torchvision torchaudio
pip install --upgrade --disable-pip-version-check --no-input -r requirements.txt
python setup.py install
# Create symbolic links for the Discord bot to have access to the tortoise API
cd ../robot/
ln -s ../tortoise-tts/tortoise tortoise
