DIFF_ORIGIN_BRANCH := master

lint:
	@git diff --name-only --diff-filter=d origin/$(DIFF_ORIGIN_BRANCH) | xargs -r uv run pre-commit run --files
