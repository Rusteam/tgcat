build:
	rm -rf submission/submission.zip
	docker compose run --build tglang

test:
	cp submission/submission.zip lib/
	docker compose run --build tglang-tester
	cat ./data/output.txt

predict:
	python -m src.train.predict