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