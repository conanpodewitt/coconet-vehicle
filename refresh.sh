#!/bin/bash

# Temporary development script to refresh CoCoNet installation
# Use this after making changes to the CoCoNet repository

# Uninstall existing CoCoNet installation
pip uninstall coconet -y

# Install latest version from GitHub
pip install git+https://github.com/conanpodewitt/coconet-vehicle