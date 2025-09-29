DIFF_ORIGIN_BRANCH := master

lint:
	@git diff --name-only --diff-filter=d origin/$(DIFF_ORIGIN_BRANCH) | xargs -r uv run pre-commit run --files

run-local:
	uv run uvicorn --factory text_classifier.main:create_app
