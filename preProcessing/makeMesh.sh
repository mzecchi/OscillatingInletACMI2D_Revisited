#!/bin/bash

# Check if a case name is provided as an argument
if [ -z "$1" ]; then
  echo "Error: No case name provided."
  echo "Usage: $0 <case_name>"
  exit 1
fi

# Set the case name from the command-line argument
CASE="$1"

# Check if CASE is a directory
if [ -d "$CASE" ]; then
  echo "Processing case: $CASE"
else
  echo "Error: Directory '$CASE' does not exist in the current directory."
  exit 1
fi

STL_FILE="./${CASE}/constant/triSurface/${CASE}.stl"
FMS_FILE="./${CASE}/constant/triSurface/${CASE}.fms"
SCALE_FACTOR=1e-3
ANGLE=30

run_and_check() {
    local command="$1"
    local log="$2"
    
    # Extract the first word of the command
    local program_name=$(echo "$command" | awk '{print $1}')
    
    echo "Running $program_name..."
    
    # Check if the program exists
    if ! command -v "$program_name" &> /dev/null; then
        echo "Error: $program_name is not found or not installed."
        exit 1
    fi

    # Run the command and redirect output to the log
    $command > "$log" 2>&1 || { 
        echo "Error: $program_name failed to run. Check $log for details.";
        echo "Last 10 lines of the log:";
        tail -n 10 "$log";
        exit 1; 
    }

    # Ensure log file exists and is non-empty
    if [ ! -s "$log" ]; then
        echo "Error: Log file $log does not exist or is empty. $program_name might not have run."
        exit 1
    fi

    # Check the log for the "End" message
    if grep -q "End" "$log"; then
        echo "$program_name finished successfully."
    else
        echo "Error: $program_name did not finish successfully or log did not contain 'End'. Check $log for details."
        echo "Last 10 lines of the log:";
        tail -n 10 "$log";
        exit 1
    fi
}


# Remove existing polyMesh directory if it exists
if [ -d "./${CASE}/constant/polyMesh" ]; then
    echo "Removing existing polyMesh directory..."
    rm -r "./${CASE}/constant/polyMesh"
fi

mkdir -p "${CASE}/_logs"

# Ensure the script stops on errors
set -e

# Run each command and check its log
run_and_check "python3 util_cat_STLs.py $CASE" "${CASE}/_logs/log.cat_STLs"
run_and_check "surfaceFeatureEdges -angle $ANGLE $STL_FILE $FMS_FILE -case ${CASE}" "${CASE}/_logs/log.surfaceFeatureEdges"
run_and_check "cartesianMesh -case ${CASE}" "${CASE}/_logs/log.cartesianMesh"
run_and_check "scaleMesh -case ${CASE} $SCALE_FACTOR" "${CASE}/_logs/log.scaleMesh"
run_and_check "topoSet -case ${CASE}" "${CASE}/_logs/log.topoSet"

touch "$CASE/$CASE.foam"

echo "All commands executed successfully."

