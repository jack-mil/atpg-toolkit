#!/usr/bin/env bash

# Clear files if the exist
> results-sim.txt
> results-faults.txt

# Loop over all files in the circuits directory
for circuit_file in circuits/*.net; do
    # Extract the base name of the circuit file (e.g., s349f_2 from circuits/s349f_2.net)
    base_name=$(basename "$circuit_file" .net)
    
    # Construct the corresponding test file name
    test_file="tests/${base_name}.in"
    
    # Check if the test file exists
    if [[ -f "$test_file" ]]; then
        # Run the Python script and append the output to results.txt
        python3 run.py simulate "$circuit_file" -f "$test_file" >> results-sim.txt
        python3 run.py faults   "$circuit_file" -f "$test_file" >> results-faults.txt
    else
        echo "Test file $test_file not found, skipping $circuit_file" 1>&2
    fi
done
