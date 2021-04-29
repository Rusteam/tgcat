#!/bin/bash

./tgcat-tester language data/external/r-2/dc0415-input/original/dc0415-input-all.txt data/processed/dc0415-language_output.txt
./tgcat-tester language data/external/r-2/dc0421-input/original/dc0421-input-all.txt data/processed/dc0421-language_output.txt
./tgcat-tester category data/external/r-2/dc0415-input/original/dc0415-input-all.txt data/processed/dc0415-category_output.txt
./tgcat-tester category data/external/r-2/dc0421-input/original/dc0421-input-all.txt data/processed/dc0421-category_output.txt