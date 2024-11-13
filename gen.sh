#!/bin/bash

# Set initial maximum comb_tasks value
max_comb_tasks=13

# Create directories for each comb_tasks value
for comb in $(seq 0 $max_comb_tasks); do
    if [ ! -d "./iso/${comb}" ]; then
        mkdir -p "./iso/${comb}"
    fi
done

# Loop through each possible comb_tasks value
for comb in $(seq 0 $max_comb_tasks); do
    # Calculate corresponding workload_tasks value
    # When comb is 0, workload should be 13
    # When comb is 10, workload should be 3
    workload_tasks=$((16 - comb))
    
    # Run 100 iterations for this combination
    for i in {1..100}; do
        python3 selector.py \
            --num_tasks 16 \
            --iso_tasks 0 \
            --comb_tasks $comb \
            --workload_tasks $workload_tasks \
            --output "./iso/${comb}/${i}_${comb}-${comb}-combined.yaml" \
            --seed_num $i
    done
done