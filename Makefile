build:
	bash build.sh
	python -m unittest tests/test*.py
	mv data/submission.zip src/

test:
	bash test.sh
