#!/bin/bash

# Ensure the script is being run from the directory it resides in
cd "$(dirname "$0")"

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 could not be found"
    exit 1
fi

echo "Python3 is installed"


echo "Build step completed successfully"
