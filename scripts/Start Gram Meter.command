#!/bin/bash
# ============================================
# Gram Meter Platform - macOS Double-Click Starter
# ============================================
# Double-click this file in Finder to start all services
# ============================================

# Get the directory where this script is located
cd "$(dirname "$0")"

# Make the main script executable and run it
chmod +x start_platform.sh
./start_platform.sh
