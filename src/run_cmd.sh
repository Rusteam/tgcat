#!/bin/bash

# Run through all files in the directory
# Compare the output with the expected output
# and measure the average accuracy

files=$(ls /app/data/raw/clean_test_set/*/*.*)
rm /app/data/output.txt
for file in $files
do
    index=$(./tglang-tester $file)
    echo "$file,$index" >> /app/data/output.txt
done
