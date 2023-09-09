find . | grep -E "(/__pycache__$|.pytest_cache|.ruff_cache|\.pyc$|\.pyo$)" | xargs rm -rf
