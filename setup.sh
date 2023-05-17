#!/bin/bash

# Update package lists
sudo apt-get update

# Install necessary packages
sudo apt-get install -y ca-certificates curl gnupg

# Create directory for keyrings
sudo install -m 0755 -d /etc/apt/keyrings

# Download Docker's GPG key and save it to the keyring directory
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set appropriate permissions for the GPG key
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository to the package sources list
echo "deb [arch=\"$(dpkg --print-architecture)\" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package lists again
sudo apt-get update

# Install Docker and related packages
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Install Python 3 and pip
sudo apt-get install -y python3 python3-pip

# Install fab-classic package using pip
pip install fab-classic

