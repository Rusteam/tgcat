build:
	DOCKER_DEFAULT_PLATFORM=linux/amd64 \
		docker compose run --build tglang

test:
	rsync -avz --delete ./submission/ ./src/submission/
	DOCKER_DEFAULT_PLATFORM=linux/amd64 \
		docker compose run --build tglang-tester
	cat ./data/output.txt

predict:
	python -m src.train.predict