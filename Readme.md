# Processor Simulator

This project simulates a simple processor that executes a set of instructions and logs the state of the processor after each clock cycle. The simulator is designed to work with JSON input files and produce JSON output logs. Additionally, a comparison script is provided to validate the output against a reference JSON file.

## Table of Contents
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
  - [Running the Simulator](#running-the-simulator)
  - [Running the Comparison](#running-the-comparison)
- [Docker Usage](#docker-usage)

## Requirements

- Python 3.6+
- Docker (optional, for running the simulator in a container)

## Setup

1. Clone the repository:

   ```sh
   git clone https://github.com/drish99/VLIW-Simulator.git
   cd processorsimulator
   '''
2. Ensure you have Python 3 installed. You can check your Python version with:

'''
python3 --version
''''

### Usage
## Running the Simulator

1. Prepare your input JSON file (e.g., input.json) with instructions. Example:

[
    "addi x1, x1, 1",
    "addi x2, x2, 2",
    "addi x3, x3, 3",
    "addi x4, x4, 4"
]

2. Run the simulator:
python3 simulator.py input.json output.json

This will generate output.json containing the log of the processor state after each clock cycle.

## Running the Comparison
Prepare your reference JSON file (e.g., reference.json) with the expected output.

## Run the comparison script:

python3 compare.py output.json -r reference.json
The script will compare output.json with reference.json and provide detailed error messages if there are any discrepancies. If everything matches, it will print "PASSED!".

## Docker Usage
To run the simulator in a Docker container, follow these steps:

## Build the Docker image:

docker build -t simulator .

## Run the Docker container:
docker run -v ${PWD}:/usr/src/app simulator input.json user_output.json

(Replace ${PWD} with the absolute path of your current directory)

