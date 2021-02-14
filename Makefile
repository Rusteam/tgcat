build:
	bash build.sh
	mv resources/submission.zip src/

test:
	bash test.sh
	python -m unittest tests/test*.py
