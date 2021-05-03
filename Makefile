build:
	bash build.sh
	mv resources/submission.zip src/

test:
	bash test.sh

unit:
	python -m src.train.predict data/external/r-2/dc0415-input/original/dc0415-input-all.txt
	python -m src.train.predict data/external/r-2/dc0421-input/original/dc0421-input-all.txt
	python -m unittest tests/test*.py

