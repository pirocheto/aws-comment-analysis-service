build-GetDataFunction:
	poetry lock
	poetry export --without-hashes \
		--only main \
    	--format=requirements.txt \
    	> requirements-poetry.txt

	poetry run pip install -r requirements-poetry.txt \
		--target $(ARTIFACTS_DIR)

	cp src/* $(ARTIFACTS_DIR)