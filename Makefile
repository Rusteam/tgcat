build:
	DOCKER_DEFAULT_PLATFORM=linux/amd64 \
		docker compose run --build tglang

test:
	rsync -avz --delete ./submission/ ./src/submission/
	DOCKER_DEFAULT_PLATFORM=linux/amd64 \
		docker compose run --build tglang-tester
	tail ./data/output.txt
	python src/eval.py

predict:
	python -m src.train.predict

submit:
	@echo "Create a final submission"
	cp README.md ./submission/README.md
	cp data/processed/tglang_train.csv \
		data/processed/tglang_test.csv \
		notebooks/0.3.0-rg-tglang-data-prep.ipynb \
		notebooks/0.3.1-rg-build-model-tglang.ipynb \
		models/trained/tglang.json \
		./submission/train/
	cp -R notebooks/figures ./submission/train/
	cd submission && zip -r submission.zip . && mv submission.zip ..
