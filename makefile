deps:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

check:
	black --check .
	isort --check-only .
	flake8
	mypy k8s_audit_filter --explicit-package-bases
	mypy tests --explicit-package-bases

lint:
	black .
	isort .
	flake8
	mypy k8s_audit_filter --explicit-package-bases
	mypy tests --explicit-package-bases

test:
	export PYTHONBUFFERED=1
	pytest -v

publish:
	hatch version minor
	hatch build -t wheel
	hatch publish
