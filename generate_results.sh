#!/usr/bin/env bash

# Clear the results.txt file if it exists
> results.txt

# Loop over all files in the circuits directory
for circuit_file in circuits/*.net; do
    # Extract the base name of the circuit file (e.g., s349f_2 from circuits/s349f_2.net)
    base_name=$(basename "$circuit_file" .net)
    
    # Construct the corresponding test file name
    test_file="tests/${base_name}.in"
    
    # Check if the test file exists
    if [[ -f "$test_file" ]]; then
        # Run the Python script and append the output to results.txt
        python sim.py "$circuit_file" -i "$test_file" >> results.txt
    else
        echo "Test file $test_file not found, skipping $circuit_file" >> results.txt
    fi
done
