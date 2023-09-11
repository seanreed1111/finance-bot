#! /bin/bash
sudo apt-get update && \
sudo apt-get upgrade -y && \
sudo apt install python3 -y && \
sudo apt install python3-pip -y && \
export HOME="/home/vmuser" && \
export PATH="$HOME/.local/bin:$PATH" && \
pip install -r requirements.txt && \
sudo curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash && \
curl -fsSL https://get.docker.com -o get-docker.sh && \
sudo sh get-docker.sh && \
sudo usermod -aG docker $USER && \
sudo reboot

python3 app.py

