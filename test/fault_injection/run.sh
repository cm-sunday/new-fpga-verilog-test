#!/bin/bash

# Author: Sunday Ukwenya

# Build:  chmod +x run.sh
# Usage: ./run.sh [filename_without_extension]
# Example: ./run.sh exercise_force


if [ -z "$1" ]; then
    echo "Usage: ./run.sh [filename]"
    echo "Example: ./run.sh exercise_force"
    echo ""
    echo "Available Verilog files:"
    ls *.v
    exit 1
fi

FILENAME=$1

if [ ! -f "$FILENAME.v" ]; then
    echo "ERROR: $FILENAME.v not found!"
    exit 1
fi

echo "Compiling $FILENAME.v..."
iverilog -o $FILENAME $FILENAME.v
if [ $? -ne 0 ]; then
    echo "ERROR: Compilation failed!"
    exit 1
fi

echo "Running simulation..."
vvp $FILENAME
if [ $? -ne 0 ]; then
    echo "ERROR: Simulation failed!"
    exit 1
fi

if [ -f "$FILENAME.vcd" ]; then
    echo "Launching GTKWave..."
    gtkwave $FILENAME.vcd &
else
    echo "WARNING: No VCD file generated!"
fi

echo "Done!"