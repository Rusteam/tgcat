build:
	bash build.sh
	mv resources/submission.zip src/

test:
	bash test.sh
	python -m unittest tests/test*.py

predict:
	python -m src.train.predict

web:
	python -m streamlit run src/train/app.py