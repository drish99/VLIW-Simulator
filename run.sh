#!/bin/bash

# Ensure the script is being run from the directory it resides in
cd "$(dirname "$0")"

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 input.json output.json"
    exit 1
fi

input_file=$1
output_file=$2

# Check if input file exists
if [ ! -f "$input_file" ]; then
    echo "$input_file not found!"
    exit 1
fi

# Run the simulator
python3 simulator.py "$input_file" "$output_file"

# Compare the output 
 python3 ./compare.py user_output.json -r output.json 

# Check if the output was generated successfully
if [ ! -f "$output_file" ]; then
    echo "Simulation failed or $output_file was not created."
    exit 1
else
    echo "Simulation completed successfully. Output written to $output_file."
fi
